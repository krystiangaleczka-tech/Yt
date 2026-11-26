/* GTA Clipper — local app (vanilla JS, no build step). All visible text is Polish. */
"use strict";

const S = { state: null, shorts: [], page: "home", tab: "new", group: "day", qc: "all", q: "", makeTab: "now",
  review: null, detail: null, wiz: null, lastJobs: "", planPreview: null };
const $ = (sel, el = document) => el.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmtDur = (s) => `${Math.round(s || 0)} s`;
const fmtTime = (t) => new Date(t * 1000).toLocaleString("pl-PL", { weekday: "short", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
const dayKey = (t) => new Date(t * 1000).toLocaleDateString("pl-PL", { weekday: "short", day: "numeric", month: "short" });
const STATUS = { new: "do przeglądu", approved: "zatwierdzony", rejected: "odrzucony" };
const RULES = { allowed: "Pozwala klipować", tips: "Ma zasady klipowania", no: "Nie pozwala", unknown: "Nie wiadomo" };
const AIS = { claude: "Claude Code", codex: "Codex", gemini: "Gemini CLI", kimi: "Kimi", opencode: "OpenCode", ollama: "Ollama (lokalny model)", custom: "Własne polecenie", none: "Bez AI" };
const LAYOUTS = { auto: "Automatycznie", stack: "Kamerka na górze", bubble: "Bańka z kamerką", full: "Cały kadr", facecrop: "Twarz w kadrze" };
const LANGS = { en: "English", pl: "Polski", es: "Español", pt: "Português", de: "Deutsch", fr: "Français", it: "Italiano", tr: "Türkçe", ar: "العربية", ru: "Русский", any: "Każdy język" };

async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch(path, opt);
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error(j.error || r.statusText);
  return j;
}
function toast(msg, ms = 2600) {
  const t = $("#toast"); t.textContent = msg; t.hidden = false;
  clearTimeout(toast._t); toast._t = setTimeout(() => (t.hidden = true), ms);
}
async function copy(text) {
  try { await navigator.clipboard.writeText(text); toast("Skopiowane"); }
  catch { const ta = document.createElement("textarea"); ta.value = text; document.body.append(ta); ta.select(); document.execCommand("copy"); ta.remove(); toast("Skopiowane"); }
}
async function load() {
  S.state = await api("/api/state");
  S.shorts = await api("/api/shorts");
}

/* ------------------------------------------------------------------ router */
function go(page) {
  S.page = page;
  document.querySelectorAll("#side button").forEach((b) => b.classList.toggle("on", b.dataset.page === page));
  render();
}
function render() {
  if (!S.state) return;
  if (!S.state.settings.setup_done && !S.wiz) return openWizard();
  const pages = { home, shorts, streamers, make, ready, plan, look, publish, propose, settings };
  $("#main").innerHTML = (pages[S.page] || home)();
  after[S.page]?.();
}
const after = {};

/* ------------------------------------------------------------------ home */
function home() {
  const c = S.state.counts, ap = S.state.settings.autopilot;
  const live = S.state.live;
  const nNew = S.shorts.filter((x) => x.status === "new").length;
  const nAppr = S.shorts.filter((x) => x.status === "approved" && !x.scheduled_at).length;
  return `
  <div class="row between"><h1>Start</h1>
    <span class="mute small"><span class="dot ${ap.enabled ? "on" : ""}"></span>Autopilot ${ap.enabled ? `włączony · ${esc(ap.time)}` : "wyłączony"}</span></div>
  <p class="sub">Wszystko działa tylko na tym komputerze. Nic nie jest publikowane bez Ciebie.</p>
  <div class="row" style="margin-bottom:16px">
    ${nNew ? `<button class="btn blue big" data-act="review-start">Przejrzyj ${nNew} ${plural(nNew, "nowy Short", "nowe Shorty", "nowych Shortsów")}</button>`
           : nAppr ? `<button class="btn blue big" data-act="goto" data-page="plan">Rozplanuj ${nAppr} zatwierdzonych</button>`
           : `<button class="btn blue big" data-act="goto" data-page="make">Zrób nowe Shorty</button>`}
    <button class="btn" data-act="goto" data-page="make">Co zrobi następny przebieg</button>
  </div>
  <div class="tiles">
    <div class="tile" data-act="tab" data-tab="new"><b>${c.new || 0}</b><span>Do przeglądu</span></div>
    <div class="tile" data-act="tab" data-tab="approved"><b>${c.approved || 0}</b><span>Zatwierdzone</span></div>
    <div class="tile" data-act="goto" data-page="plan"><b>${c.scheduled || 0}</b><span>Zaplanowane</span></div>
    <div class="tile" data-act="tab" data-tab="published"><b>${c.published || 0}</b><span>Opublikowane</span></div>
  </div>
  <div class="card">
    <div class="row between"><h2>Polowanie na żywo <span class="mute small">— Twitch: nagrywa stream i tnie moment, gdy czat wybucha</span></h2>
      ${live.length ? `<button class="btn red" data-act="live-stop">Zatrzymaj</button>` : `<button class="btn blue" data-act="live-start">Zacznij polowanie</button>`}</div>
    ${live.length ? live.map(liveRow).join("") : `<p class="mute">Wyłączone. Włącz „Obserwuj na żywo” przy streamerach z Twitcha, potem kliknij „Zacznij polowanie”.</p>`}
  </div>
  ${jobsCard()}
  ${S.state.update?.available ? `<div class="card hl row between"><span>Jest nowa wersja aplikacji.</span><button class="btn blue" data-act="update-apply">Aktualizuj teraz</button></div>` : ""}`;
}
function liveRow(l) {
  return `<div class="job"><b>${esc(l.channel)}</b>
    <span class="small"><span class="dot ${l.chat ? "on" : "bad"}"></span>czat ${l.chat ? "połączony" : "—"}</span>
    <span class="small"><span class="dot ${l.recording ? "on" : ""}"></span>${l.recording ? "nagrywa" : "offline / czeka"}</span>
    <span class="small mute">${l.per_min} wiad./min · teraz ${l.distinct} osób / 10 s · zwykle ${l.baseline ?? "?"}</span>
    ${l.events.length ? `<div class="small mute">${l.events.slice(-4).reverse().map((e) => `${new Date(e.t * 1000).toLocaleTimeString("pl-PL")} ${esc(e.what)}`).join("<br>")}</div>` : ""}</div>`;
}
function jobsCard() { return `<div id="jobs-box">${jobsInner()}</div>`; }
function jobsInner() {
  const jobs = S.state.jobs;
  if (!jobs.length) return "";
  return `<div class="card"><h2>Zadania</h2>${jobs.slice(0, 6).map((j) => `
    <div class="job"><div class="row between"><span><span class="dot ${j.status === "running" ? "run" : j.status === "done" ? "on" : "bad"}"></span>
      <b>${esc(j.label)}</b> <span class="mute small">${j.status === "running" ? "trwa…" : j.status === "done" ? "gotowe" : "błąd"}</span></span>
      <button class="btn small" data-act="job-log" data-id="${j.id}">Log</button></div>
      <div class="log" style="max-height:90px;margin-top:6px">${esc(j.tail.join("\n"))}</div></div>`).join("")}</div>`;
}
function plural(n, one, few, many) {
  if (n === 1) return one;
  const d = n % 10, dd = n % 100;
  return d >= 2 && d <= 4 && !(dd >= 12 && dd <= 14) ? few : many;
}

/* ------------------------------------------------------------------ shorts */
function filtered() {
  let xs = S.shorts;
  if (S.tab === "published") xs = xs.filter((x) => x.published);
  else if (S.tab !== "all") xs = xs.filter((x) => x.status === S.tab && (S.tab !== "approved" || !x.published));
  if (S.qc !== "all") xs = xs.filter((x) => x.qc.status === S.qc);
  if (S.q) { const q = S.q.toLowerCase(); xs = xs.filter((x) => `${x.hook} ${x.title} ${x.name} ${x.id}`.toLowerCase().includes(q)); }
  return xs;
}
function shorts() {
  const xs = filtered();
  const tabs = [["new", "Do przeglądu"], ["approved", "Zatwierdzone"], ["published", "Opublikowane"], ["rejected", "Odrzucone"], ["all", "Wszystkie"]];
  const groups = {};
  for (const x of xs) {
    const k = S.group === "day" ? dayKey(x.created) : `${x.name || "?"} · ${x.source_title || x.batch}`;
    (groups[k] = groups[k] || []).push(x);
  }
  const unscheduled = S.shorts.filter((x) => x.status === "approved" && !x.scheduled_at && !x.published).length;
  return `
  <div class="row between"><h1>Shorty</h1>
    <div class="row">
      <button class="btn" data-act="review-start" ${xs.length ? "" : "disabled"}>Przeglądaj te (${xs.length})</button>
      <button class="btn" data-act="goto" data-page="plan" ${unscheduled ? "" : "disabled"}>Rozplanuj zatwierdzone (${unscheduled})</button>
      <button class="btn" data-act="copy-posts">Kopiuj wszystkie opisy</button></div></div>
  <p class="sub">${S.shorts.length} Shortsów · nic nie jest publikowane bez Ciebie</p>
  <div class="row" style="margin-bottom:10px">
    <div class="tabs">${tabs.map(([k, l]) => `<button class="${S.tab === k ? "on" : ""}" data-act="tab" data-tab="${k}">${l} (${countTab(k)})</button>`).join("")}</div>
    <div class="tabs"><button class="${S.group === "day" ? "on" : ""}" data-act="group" data-g="day">Po dniu</button><button class="${S.group === "stream" ? "on" : ""}" data-act="group" data-g="stream">Po streamie</button></div>
    <div class="tabs">${["all", "PASS", "WARN", "FAIL"].map((k) => `<button class="${S.qc === k ? "on" : ""}" data-act="qcf" data-qc="${k}">${k === "all" ? "Każda kontrola" : k}</button>`).join("")}</div>
    <input type="text" id="search" placeholder="Szukaj w tytułach, hookach…" value="${esc(S.q)}" style="width:240px">
  </div>
  ${xs.length ? Object.entries(groups).map(([k, items]) => `
    <div class="daygroup"><b>${esc(k)}</b><span class="mute small">${items.length} · ${items.filter((i) => i.qc.status === "PASS").length} PASS · ${items.filter((i) => i.qc.status === "WARN").length} WARN · ${items.filter((i) => i.qc.status === "FAIL").length} FAIL</span></div>
    <div class="grid">${items.map(card).join("")}</div>`).join("")
  : `<div class="card mute">Nic tu nie ma. ${S.tab === "new" ? "Zrób nowe Shorty w zakładce „Zrób”." : ""}</div>`}`;
}
function countTab(k) {
  if (k === "all") return S.shorts.length;
  if (k === "published") return S.shorts.filter((x) => x.published).length;
  return S.shorts.filter((x) => x.status === k && (k !== "approved" || !x.published)).length;
}
function card(x) {
  return `<div class="sc" data-act="detail" data-id="${esc(x.id)}">
    <img loading="lazy" src="${esc(x.cover)}" alt="">
    <div class="top"><span class="badge ${x.qc.status}">${x.qc.status}</span>
      <span class="badge st-${x.status}">${STATUS[x.status]}</span>${x.source === "live" ? `<span class="badge st-live">LIVE</span>` : ""}</div>
    <span class="dur">${fmtDur(x.duration)}</span>
    <div class="bot"><b>${esc(x.title || x.hook)}</b><br><span class="mute">${esc(x.name || "")}${x.scheduled_at ? ` · ${fmtTime(x.scheduled_at)}` : ""}</span></div>
    ${x.busy ? `<div class="busy">Robię nową wersję…</div>` : ""}</div>`;
}
after.shorts = () => {
  const s = $("#search");
  s?.addEventListener("input", () => { S.q = s.value; const pos = s.selectionStart; render(); const n = $("#search"); n.focus(); n.setSelectionRange(pos, pos); });
};

/* ------------------------------------------------------------------ review */
function openReview(list) {
  S.review = { list: list.map((x) => x.id), i: 0 };
  drawReview();
}
function drawReview() {
  const R = S.review; if (!R) return;
  if (R.i >= R.list.length) { closeOverlay(); toast("Wszystko przejrzane"); S.review = null; return; }
  const x = S.shorts.find((s) => s.id === R.list[R.i]);
  if (!x) { R.i++; return drawReview(); }
  overlay(`<div class="review">
    <button class="btn navbtn" data-act="rv-prev">‹</button>
    <video src="${esc(x.file)}" autoplay loop playsinline controls id="rv-video"></video>
    <button class="btn navbtn" data-act="rv-next">›</button>
    <div class="col">
      <div class="row between"><span class="mute">${R.i + 1} / ${R.list.length}</span><button class="btn" data-act="close">Zamknij (Esc)</button></div>
      <div class="row"><span class="badge ${x.qc.status}">${x.qc.status}</span><span class="badge st-${x.status}">${STATUS[x.status]}</span>
        ${x.score ? `<span class="mute small">ocena AI ${x.score}</span>` : ""}</div>
      <h2 style="margin:4px 0 0">${esc(x.hook)}</h2>
      <div>${esc(x.title)}</div>
      <div class="mute small">${esc(x.name || "")} · ${fmtDur(x.duration)} · ${esc(x.why || "")}</div>
      ${x.qc.notes.length ? `<ul class="notes small">${x.qc.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>` : ""}
      <div class="row" style="margin:8px 0">
        <button class="btn green big" data-act="rv-approve">Zatwierdź (A)</button>
        <button class="btn red big" data-act="rv-reject">Odrzuć (X)</button></div>
      <div class="card" style="margin:0"><h3>Poproś AI o zmianę</h3>
        <textarea id="rv-change" rows="2" placeholder="np. zakończ 2 sekundy wcześniej"></textarea>
        <div class="row" style="margin-top:6px"><button class="btn blue" data-act="rv-change">Zrób nową wersję</button>
        <button class="btn" data-act="detail" data-id="${esc(x.id)}">Więcej opcji</button></div></div>
      <div class="keys"><span><kbd>A</kbd> zatwierdź</span><span><kbd>X</kbd> odrzuć</span><span><kbd>←</kbd><kbd>→</kbd> poprzedni / następny</span><span><kbd>Spacja</kbd> pauza</span><span><kbd>Esc</kbd> zamknij</span></div>
    </div></div>`, "wide");
}
async function reviewDecide(status) {
  const R = S.review, id = R.list[R.i];
  await api(`/api/shorts/${id}/status`, { status });
  const x = S.shorts.find((s) => s.id === id); if (x) x.status = status;
  R.i++; drawReview();
}

/* ------------------------------------------------------------------ detail */
function openDetail(id) {
  S.detail = id; S.review = null;
  drawDetail();
}
function drawDetail() {
  const x = S.shorts.find((s) => s.id === S.detail); if (!x) return closeOverlay();
  const v = x.versions[x.current];
  const th = S.state.themes, look = { ...lookDefaults(), ...x.look };
  overlay(`<div class="row between"><h2 style="margin:0">${esc(x.hook)}</h2><button class="btn" data-act="close">Zamknij</button></div>
  <p class="mute small">${esc(x.name || "")} · ${esc(x.source_title || "")} ${x.url && x.url.startsWith("http") ? `· <a href="${esc(x.url)}" target="_blank">źródło</a>` : ""}</p>
  <div class="detail">
    <div class="col">
      <video src="${esc(v.file)}" controls loop playsinline></video>
      <div class="row"><span class="badge ${v.qc.status}">${v.qc.status}</span><span class="mute small">${fmtDur(v.duration)} · ${LAYOUTS[v.layout] || v.layout}</span>
        <a class="btn small" href="${esc(v.file)}" download>Pobierz</a></div>
      ${v.qc.notes.length ? `<ul class="notes small">${v.qc.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>` : ""}
      <h3 style="margin-top:8px">Wersje</h3>
      <div class="vers">${x.versions.map((vv, i) => `<button class="btn ${i === x.current ? "on" : ""}" data-act="set-version" data-i="${i}">
        v${vv.v} · ${esc(vv.note)} <span class="badge ${vv.qc.status}">${vv.qc.status}</span></button>`).join("")}</div>
      <p class="mute small">Oryginał zostaje zawsze. Każda zmiana robi nową wersję obok.</p>
    </div>
    <div class="col">
      <div class="row">
        <button class="btn green" data-act="d-status" data-s="approved" ${x.status === "approved" ? "disabled" : ""}>Zatwierdź</button>
        <button class="btn red" data-act="d-status" data-s="rejected" ${x.status === "rejected" ? "disabled" : ""}>Odrzuć</button>
        <button class="btn" data-act="d-status" data-s="new">Wróć do przeglądu</button>
        <label class="chk"><input type="checkbox" id="d-pub" ${x.published ? "checked" : ""}> opublikowany</label></div>
      ${x.busy ? `<div class="card hl">Robię nową wersję… zobaczysz ją tu za kilka minut.</div>` : ""}
      <div class="card"><h3>Poproś AI o zmianę</h3>
        <p class="mute small">Napisz zwykłymi słowami. Proste rzeczy („zakończ 2 s wcześniej”, „zacznij 3 s wcześniej”, „hook: NOWY HOOK”, nazwa stylu) działają też bez AI.</p>
        <textarea id="d-change" rows="2" placeholder="np. zakończ 2 sekundy wcześniej"></textarea>
        <div class="chips" style="margin:6px 0">${["zakończ 2 s wcześniej", "zacznij 3 s wcześniej", "zakończ 2 s później", "krótszy hook"].map((t) => `<span class="chip" data-act="fill-change" data-t="${t}">${t}</span>`).join("")}</div>
        <button class="btn blue" data-act="d-change" ${x.busy ? "disabled" : ""}>Zrób nową wersję</button></div>
      <div class="card"><h3>Wygląd tej wersji</h3>
        <div class="row"><select id="d-style">${Object.entries(th).map(([k, t]) => `<option value="${k}" ${look.style === k ? "selected" : ""}>${esc(t.label)}</option>`).join("")}</select>
          <select id="d-layout">${Object.entries(LAYOUTS).map(([k, l]) => `<option value="${k}" ${look.layout === k ? "selected" : ""}>${l}</option>`).join("")}</select>
          <label class="chk"><input type="checkbox" id="d-flip" ${look.flip ? "checked" : ""}> kamerka pod grą</label>
          <input type="text" id="d-wm" placeholder="znak wodny, np. @mojkanal" value="${esc(look.watermark || "")}"></div>
        <button class="btn" style="margin-top:8px" data-act="d-look" ${x.busy ? "disabled" : ""}>Zrób wersję z tym wyglądem</button></div>
      <div class="card"><h3>Twój głos</h3>
        <p class="mute small">Jedno zdanie od Ciebie zmienia kopię w komentarz. Dźwięk gry ścisza się pod głosem i wraca po nim.</p>
        <div class="row"><input type="file" id="d-voice" accept="audio/*,.m4a,.caf,video/webm">
          <button class="btn" data-act="rec">${S.rec ? "■ Zatrzymaj nagrywanie" : "● Nagraj teraz"}</button>
          <select id="d-at"><option value="payoff">zaraz po puencie</option><option value="start">na początku</option></select>
          <button class="btn" data-act="d-voice" ${x.busy ? "disabled" : ""}>Dodaj głos</button></div></div>
      <div class="card"><h3>Opis do publikacji</h3>
        <input type="text" id="d-title" value="${esc(x.title)}" style="width:100%" maxlength="100">
        <input type="text" id="d-tags" value="${esc((x.hashtags || []).join(" "))}" style="width:100%;margin-top:6px">
        <input type="text" id="d-credit" value="${esc(x.credit)}" style="width:100%;margin-top:6px">
        <div class="row" style="margin-top:6px"><button class="btn" data-act="d-post">Zapisz</button><button class="btn" data-act="d-copy">Kopiuj opis</button></div></div>
      <div class="card"><h3>Termin publikacji</h3>
        <div class="row"><input type="datetime-local" id="d-when" value="${x.scheduled_at ? toLocalInput(x.scheduled_at) : ""}">
          <button class="btn" data-act="d-when">Ustaw</button><button class="btn" data-act="d-unwhen">Usuń z planu</button></div></div>
    </div></div>`, "wide");
  $("#d-pub")?.addEventListener("change", async (e) => { await api(`/api/shorts/${x.id}/published`, { published: e.target.checked }); await refresh(); });
}
function toLocalInput(t) { const d = new Date(t * 1000); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 16); }
function lookDefaults() { const s = S.state.settings; return { style: s.style, layout: s.layout, flip: s.flip, watermark: s.watermark }; }

/* voice recording in the browser */
async function toggleRec() {
  if (S.rec) { S.rec.stop(); return; }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const chunks = []; const rec = new MediaRecorder(stream);
    rec.ondataavailable = (e) => chunks.push(e.data);
    rec.onstop = () => { stream.getTracks().forEach((t) => t.stop()); S.recBlob = new Blob(chunks, { type: rec.mimeType || "audio/webm" }); S.rec = null; drawDetail(); toast("Nagranie gotowe — kliknij „Dodaj głos”"); };
    rec.start(); S.rec = rec; drawDetail();
  } catch (e) { toast("Brak dostępu do mikrofonu: " + e.message); }
}
function blobToDataUrl(b) { return new Promise((res) => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(b); }); }

/* ------------------------------------------------------------------ streamers */
function streamers() {
  const items = S.state.streamers, live = S.state.live;
  return `<div class="row between"><h1>Streamerzy</h1>
    ${live.length ? `<button class="btn red" data-act="live-stop">Zatrzymaj polowanie na żywo</button>` : `<button class="btn blue" data-act="live-start">Zacznij polowanie na żywo</button>`}</div>
  <p class="sub">Klipuj tylko streamerów, którzy na to pozwalają. Kogoś z „Nie pozwala” aplikacja nie ruszy.</p>
  <div class="card"><div class="row"><input type="text" id="st-add" placeholder="Wklej link Twitch, YouTube albo Kick, albo wpisz nazwę" style="flex:1">
    <button class="btn blue" data-act="st-add">Dodaj</button></div></div>
  <div class="card list">${items.length ? items.map((s, i) => `
    <div class="item"><b style="min-width:140px">${esc(s.name)}</b><span class="plat ${s.platform}">${s.platform}</span>
      <select data-st="${i}" data-k="rules" class="rule-${s.rules}">${Object.entries(RULES).map(([k, l]) => `<option value="${k}" ${s.rules === k ? "selected" : ""}>${l}</option>`).join("")}</select>
      <label class="chk"><input type="checkbox" data-st="${i}" data-k="enabled" ${s.enabled ? "checked" : ""}> szukaj nowych filmów</label>
      ${s.platform === "twitch" ? `<label class="chk"><input type="checkbox" data-st="${i}" data-k="live_watch" ${s.live_watch ? "checked" : ""}> obserwuj na żywo</label>` : `<span class="mute small">na żywo tylko Twitch — z ${s.platform} biorę nagranie po streamie</span>`}
      <span class="grow"></span>
      <button class="btn" data-act="st-past" data-i="${i}">Ostatnie streamy</button>
      <button class="btn" data-act="st-del" data-i="${i}">Usuń</button>
      <div id="past-${i}" style="width:100%"></div></div>`).join("") : `<p class="mute">Nikogo jeszcze nie dodałeś.</p>`}</div>
  <div id="live-box">${liveInner()}</div>`;
}
function liveInner() {
  const live = S.state.live;
  return live.length ? `<div class="card"><h2>Na żywo</h2>${live.map(liveRow).join("")}</div>` : "";
}
after.streamers = () => {
  document.querySelectorAll("[data-st]").forEach((el) => el.addEventListener("change", async () => {
    const items = S.state.streamers, i = +el.dataset.st, k = el.dataset.k;
    items[i][k] = el.type === "checkbox" ? el.checked : el.value;
    await api("/api/streamers", { items }); render();
  }));
};

/* ------------------------------------------------------------------ make */
function make() {
  const s = S.state.settings, ap = s.autopilot;
  const days = ["pon", "wt", "śr", "czw", "pt", "sob", "nd"];
  return `<h1>Zrób Shorty</h1><p class="sub">Szuka nowych filmów i streamów GTA 6, wybiera najlepsze momenty i robi z nich gotowe Shorty.</p>
  <div class="tabs" style="margin-bottom:14px"><button class="${S.makeTab === "now" ? "on" : ""}" data-act="mtab" data-t="now">Teraz</button>
    <button class="${S.makeTab === "daily" ? "on" : ""}" data-act="mtab" data-t="daily">Codziennie</button></div>
  ${S.makeTab === "now" ? `
  <div class="card"><h3>Skąd mają być Shorty?</h3>
    <div class="row"><label class="chk"><input type="radio" name="src" value="newest" checked> Najnowsze filmy i streamy GTA 6 (Twoi streamerzy + wyszukiwanie)</label></div>
    <div class="row" style="margin-top:6px"><label class="chk"><input type="radio" name="src" value="links"> Konkretne linki albo pliki z dysku:</label></div>
    <textarea id="mk-urls" rows="3" placeholder="https://www.youtube.com/watch?v=…   https://www.twitch.tv/videos/…   ~/Movies/gameplay.mp4"></textarea>
    <div class="row" style="margin-top:8px">
      <label>Ile Shortsów <input type="number" id="mk-count" min="1" max="30" value="${s.shorts_per_run}" style="width:70px"></label>
      <label>Wyszukiwanie <input type="text" id="mk-query" value="${esc(s.query)}" style="width:160px"></label>
      <label>Tylko fragment streamu <input type="text" id="mk-window" placeholder="1:00:00-2:00:00" style="width:140px"></label></div>
    <h3 style="margin-top:12px">Ile AI</h3>${modesHtml(s.pick_mode, "mk-mode")}
    <div class="row" style="margin-top:12px"><button class="btn blue big" data-act="make">Zrób Shorty</button><button class="btn" data-act="make-preview">Pokaż polecenie</button></div>
    <div id="mk-cmd" class="mute small" style="margin-top:8px"></div>
    <p class="mute small">Trwa to chwilę: pobieranie samego dźwięku, transkrypcja na tym PC, wybór, a potem pobranie tylko wybranych sekund. Shorty pojawią się w „Shorty → Do przeglądu”.</p></div>`
  : `<div class="card"><h3>Codziennie o stałej porze</h3>
    <p class="mute small">Mac sam zrobi nowe Shorty, jeśli jesteś zalogowany. Jeśli o tej porze śpi, przebieg ruszy po obudzeniu; wyłączony — przebieg przepada. Niczego nie publikuje — rano tylko przeglądasz.</p>
    <div class="row"><label>Godzina <input type="time" id="ap-time" value="${esc(ap.time)}"></label>
      <label>Ile Shortsów <input type="number" id="ap-count" min="1" max="30" value="${ap.count}" style="width:70px"></label></div>
    <div class="chips" style="margin:10px 0">${days.map((d, i) => `<label class="chip ${ap.days.includes(i) ? "on" : ""}"><input type="checkbox" class="ap-day" value="${i}" ${ap.days.includes(i) ? "checked" : ""} hidden>${d}</label>`).join("")}</div>
    <div class="row"><button class="btn ${ap.enabled ? "red" : "blue"}" data-act="ap-toggle">${ap.enabled ? "Wyłącz" : "Włącz"}</button>
      <button class="btn" data-act="ap-save">Zapisz godzinę i dni</button>
      <button class="btn" data-act="ap-preview">Podgląd (nic nie zmienia)</button>
      <button class="btn" data-act="ap-run">Uruchom teraz</button></div>
    <pre id="ap-out" class="log" style="margin-top:10px" hidden></pre></div>`}
  ${jobsCard()}`;
}
function modesHtml(cur, name) {
  const m = [["smart", "Smart (domyślnie)", "AI czyta tylko ~30 najlepszych okien znalezionych po głośności i czacie. Mało kosztuje."],
    ["deep", "Deep", "AI czyta całe transkrypcje. Znajduje też ciche, dobre momenty. Kosztuje kilka razy więcej."],
    ["free", "Free", "Bez AI: głośność, czat, powtórki i słowa kluczowe. Nic nie kosztuje."]];
  return `<div class="modes">${m.map(([k, l, d]) => `<label class="mode ${cur === k ? "on" : ""}"><input type="radio" name="${name}" value="${k}" ${cur === k ? "checked" : ""} hidden><b>${l}</b><div class="mute small">${d}</div></label>`).join("")}</div>`;
}
after.make = () => {
  document.querySelectorAll(".mode input, .ap-day").forEach((el) => el.addEventListener("change", () => {
    if (el.classList.contains("ap-day")) el.parentElement.classList.toggle("on", el.checked);
    else { document.querySelectorAll(`input[name=${el.name}]`).forEach((r) => r.parentElement.classList.toggle("on", r.checked)); }
  }));
  $("#mk-urls")?.addEventListener("input", () => { const r = document.querySelector("input[name=src][value=links]"); if (r) r.checked = true; });
};
function makeBody() {
  const links = document.querySelector("input[name=src]:checked")?.value === "links";
  return { count: +$("#mk-count").value, mode: document.querySelector("input[name=mk-mode]:checked")?.value,
    urls: links ? $("#mk-urls").value : "", query: $("#mk-query").value, window: $("#mk-window").value.trim() };
}

/* ------------------------------------------------------------------ ready */
/* Approved, not yet published: only the clip and what goes into the upload form. */
function postDescription(x) {
  return [(x.hashtags || []).join(" "), x.credit || ""].filter(Boolean).join("\n\n");
}
function readyList() {
  return S.shorts.filter((x) => x.status === "approved" && !x.published)
    .sort((a, b) => (a.scheduled_at || 9e12) - (b.scheduled_at || 9e12) || b.created - a.created);
}
const readyName = (x, i) => `${String(i + 1).padStart(2, "0")}_${x.id.split("_").slice(1).join("_")}`;
function ready() {
  const xs = readyList();
  return `<div class="row between"><h1>Gotowe do publikacji</h1>
    <div class="row"><button class="btn blue" data-act="rd-txt" ${xs.length ? "" : "disabled"}>Pobierz opisy (.txt)</button>
      <button class="btn" data-act="copy-posts" ${xs.length ? "" : "disabled"}>Kopiuj wszystkie opisy</button></div></div>
  <p class="sub">${xs.length} ${plural(xs.length, "zatwierdzony Short", "zatwierdzone Shorty", "zatwierdzonych Shortsów")} · pobierz klip, wklej tytuł i opis, zaznacz „opublikowany”</p>
  ${xs.length ? `<div class="ready">${xs.map((x, i) => readyCard(x, i)).join("")}</div>`
    : `<div class="card mute">Nic tu nie ma. Zatwierdź Shorty w przeglądzie (Shorty → Do przeglądu).</div>`}`;
}
function readyCard(x, i) {
  const desc = postDescription(x), name = readyName(x, i);
  return `<div class="rd card" data-id="${esc(x.id)}">
    <video src="${esc(x.file)}" controls loop playsinline preload="metadata" poster="${esc(x.cover)}"></video>
    <div class="rd-info">
      <div class="row between"><span class="mute small"><b>${String(i + 1).padStart(2, "0")}</b> · ${esc(x.name || "")} · ${fmtDur(x.duration)}${x.scheduled_at ? ` · plan: ${fmtTime(x.scheduled_at)}` : ""}</span>
        <span class="badge ${x.qc.status}">${x.qc.status}</span></div>
      <label class="small mute">Tytuł <span class="cnt">${(x.title || "").length}/100</span></label>
      <div class="row"><input type="text" class="rd-title" value="${esc(x.title)}" maxlength="100" style="flex:1">
        <button class="btn small" data-act="rd-copy" data-what="title" data-id="${esc(x.id)}">Kopiuj</button></div>
      <label class="small mute">Opis</label>
      <div class="row" style="align-items:flex-start"><textarea class="rd-desc" rows="4" style="flex:1">${esc(desc)}</textarea>
        <button class="btn small" data-act="rd-copy" data-what="desc" data-id="${esc(x.id)}">Kopiuj</button></div>
      <div class="row" style="margin-top:8px">
        <a class="btn blue" href="${esc(x.file)}" download="${esc(name)}.mp4">Pobierz klip</a>
        <a class="btn" href="${esc(x.cover)}" download="${esc(name)}.jpg">Pobierz okładkę</a>
        <button class="btn" data-act="rd-save" data-id="${esc(x.id)}">Zapisz tytuł i opis</button>
        <button class="btn green" data-act="rd-pub" data-id="${esc(x.id)}">Opublikowany ✔</button>
        <button class="btn" data-act="detail" data-id="${esc(x.id)}">Edytuj klip</button></div>
    </div></div>`;
}
after.ready = () => {
  document.querySelectorAll(".rd-title").forEach((el) => el.addEventListener("input", () => {
    el.closest(".rd").querySelector(".cnt").textContent = `${el.value.length}/100`;
  }));
};
function readyFields(id) {
  const el = document.querySelector(`.rd[data-id="${CSS.escape(id)}"]`);
  return { title: el.querySelector(".rd-title").value.trim(), desc: el.querySelector(".rd-desc").value.trim() };
}

/* ------------------------------------------------------------------ plan */
function plan() {
  const days = [...Array(7)].map((_, i) => { const d = new Date(); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() + i); return d; });
  const sched = S.shorts.filter((x) => x.scheduled_at && !x.published);
  const pool = S.shorts.filter((x) => x.status === "approved" && !x.scheduled_at && !x.published);
  const s = S.state.settings;
  return `<h1>Plan publikacji</h1><p class="sub">Przeciągnij zatwierdzone Shorty na dzień albo rozłóż je automatycznie. Aplikacja niczego nie publikuje sama.</p>
  <div class="card"><div class="row between"><h3>Zatwierdzone, bez terminu (${pool.length})</h3>
    <div class="row"><label>Pierwszy o <input type="time" id="pl-first" value="${esc(s.post_first_at)}"></label>
      <label>co <input type="number" id="pl-every" value="${s.post_every_min}" style="width:70px"> min</label>
      <button class="btn" data-act="plan-preview" ${pool.length ? "" : "disabled"}>Podgląd planu</button>
      <button class="btn blue" data-act="plan-apply" ${pool.length ? "" : "disabled"}>Rozłóż automatycznie</button></div></div>
    <div class="pool">${pool.map(slot).join("") || `<span class="mute">Brak. Zatwierdź Shorty w przeglądzie.</span>`}</div>
    ${S.planPreview ? `<div class="log" style="margin-top:10px">Podgląd — nic jeszcze nie zapisane:\n${S.planPreview.map((p) => `${p.label}  ${p.id}`).join("\n")}</div>` : ""}</div>
  <div class="week">${days.map((d) => {
    const items = sched.filter((x) => new Date(x.scheduled_at * 1000).toDateString() === d.toDateString()).sort((a, b) => a.scheduled_at - b.scheduled_at);
    return `<div class="day" data-day="${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}">
      <h4>${d.toLocaleDateString("pl-PL", { weekday: "long", day: "numeric", month: "short" })}</h4>${items.map((x) => slot(x, true)).join("")}</div>`;
  }).join("")}</div>`;
}
function slot(x, withTime) {
  return `<div class="slot" draggable="true" data-id="${esc(x.id)}"><img src="${esc(x.cover)}" alt="">
    <span>${withTime ? `<b>${new Date(x.scheduled_at * 1000).toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" })}</b><br>` : ""}${esc((x.title || x.hook).slice(0, 40))}</span>
    ${withTime ? `<span class="x" data-act="unslot" data-id="${esc(x.id)}" title="Usuń z planu">×</span>` : ""}</div>`;
}
after.plan = () => {
  document.querySelectorAll(".slot").forEach((el) => el.addEventListener("dragstart", (e) => e.dataTransfer.setData("text/plain", el.dataset.id)));
  document.querySelectorAll(".day").forEach((d) => {
    d.addEventListener("dragover", (e) => { e.preventDefault(); d.classList.add("drop"); });
    d.addEventListener("dragleave", () => d.classList.remove("drop"));
    d.addEventListener("drop", async (e) => {
      e.preventDefault(); d.classList.remove("drop");
      const id = e.dataTransfer.getData("text/plain");
      const s = S.state.settings;
      const taken = S.shorts.filter((x) => x.scheduled_at && x.id !== id && new Date(x.scheduled_at * 1000).toISOString().slice(0, 10) === d.dataset.day).length;
      const [hh, mm] = s.post_first_at.split(":").map(Number);
      const [Y, M, D] = d.dataset.day.split("-").map(Number);
      const at = new Date(Y, M - 1, D, hh, mm + taken * s.post_every_min);
      await api(`/api/shorts/${id}/schedule`, { at: Math.floor(at / 1000) });
      await refresh();
    });
  });
};

/* ------------------------------------------------------------------ look */
function look() {
  const s = S.state.settings, th = S.state.themes;
  const lay = (k, ph) => `<div class="lay ${s.layout === k ? "on" : ""}" data-act="set" data-k="layout" data-v="${k}">${ph}${LAYOUTS[k]}</div>`;
  return `<h1>Wygląd</h1><p class="sub">Domyślny wygląd nowych Shortsów. Dla jednego Shorta zmienisz go w jego szczegółach (powstanie nowa wersja).</p>
  <div class="card"><h2>Napisy</h2><div class="styles">${Object.entries(th).map(([k, t]) => `
    <div class="style ${s.style === k ? "on" : ""}" data-act="set" data-k="style" data-v="${k}">
      <div class="pv">${stylePreview(t)}</div><div class="nm">${esc(t.label)}</div></div>`).join("")}</div>
    <p class="mute small">Słowa kluczowe zawsze na zielono. Wulgaryzmy-obelgi są wykropkowane tylko na ekranie, dźwięk zostaje bez zmian.</p></div>
  <div class="card"><h2>Układ</h2><div class="layouts">
    ${lay("auto", `<div class="ph"><div class="cam"></div><div class="game"></div></div>`)}
    ${lay("stack", `<div class="ph"><div class="cam"></div><div class="game"></div></div>`)}
    ${lay("bubble", `<div class="ph"><div class="game"></div><div class="bub"></div></div>`)}
    ${lay("full", `<div class="ph full"><div class="game"></div></div>`)}
    ${lay("facecrop", `<div class="ph face"></div>`)}</div>
    <div class="row" style="margin-top:10px">
      <label class="chk"><input type="checkbox" data-set="flip" ${s.flip ? "checked" : ""}> Odwróć: kamerka pod grą</label>
      <label class="chk"><input type="checkbox" data-set="punch_zooms" ${s.punch_zooms ? "checked" : ""}> Zbliżenia na największych reakcjach (do 3)</label>
      <label class="chk"><input type="checkbox" data-set="cut_dead_air" ${s.cut_dead_air ? "checked" : ""}> Wytnij ciszę</label>
      <label class="chk"><input type="checkbox" data-set="sfx" ${s.sfx ? "checked" : ""}> Efekt „whoosh” przy zbliżeniu</label>
      <label class="chk"><input type="checkbox" data-set="censor_on_screen" ${s.censor_on_screen ? "checked" : ""}> Wykropkuj obelgi w napisach</label></div></div>
  <div class="card"><h2>Marka</h2><div class="row">
    <label>Znak wodny <input type="text" data-set="watermark" value="${esc(s.watermark)}" placeholder="@twojkanal"></label>
    <label>Kolor hooka <input type="color" data-set="accent" value="${esc(s.accent)}"></label>
    <label>Kolor słów kluczowych <input type="color" data-set="keyword_color" value="${esc(s.keyword_color)}"></label></div></div>`;
}
function stylePreview(t) {
  const words = ["THIS", "IS", "CRAZY"].map((w) => (t.upper ? w : w.toLowerCase()));
  const box = t.box ? `background:${t.box};padding:2px 8px;border-radius:6px;` : "";
  const shadow = `-2px -2px 0 ${t.outline},2px -2px 0 ${t.outline},-2px 2px 0 ${t.outline},2px 2px 0 ${t.outline}`;
  return `<span style="font-family:'${t.font}';font-size:${Math.round(t.size / 3.2)}px;${box}text-shadow:${t.box ? "none" : shadow}">
    <span style="color:${t.text}">${words[0]} </span><span style="color:${t.active}">${words[1]} </span><span style="color:${t.text}">${words[2]}</span></span>`;
}
after.look = () => {
  document.querySelectorAll("[data-set]").forEach((el) => el.addEventListener("change", async () => {
    await api("/api/settings", { [el.dataset.set]: el.type === "checkbox" ? el.checked : el.value });
    await refresh(false); toast("Zapisane");
  }));
};

/* ------------------------------------------------------------------ publish */
function publish() {
  const appr = S.shorts.filter((x) => x.status === "approved" && !x.published);
  return `<h1>Publikacja</h1><p class="sub">Publikujesz sam, za darmo. Aplikacja przygotowuje pliki, okładki i opisy.</p>
  <div class="card"><h2>Ręcznie</h2>
    <p>1. Otwórz Shorta → „Pobierz”. 2. Wgraj go na YouTube / TikTok / Instagram. 3. Wklej opis. 4. Zaznacz „opublikowany”.</p>
    <div class="row"><button class="btn blue" data-act="copy-posts">Kopiuj opisy wszystkich zatwierdzonych (${appr.length})</button>
      <button class="btn" data-act="tab" data-tab="approved">Pokaż zatwierdzone</button></div></div>
  <div class="card"><h2>Automatycznie przez Claude Code (opcjonalnie)</h2>
    <p class="mute">Jeśli używasz usługi do planowania postów, która ma serwer MCP (np. Blotato — płatna), możesz podłączyć ją do Claude Code i poprosić: „opublikuj moje zatwierdzone Shorty według planu”. Claude Code czyta pliki z folderu roboczego:</p>
    <pre class="log">${esc(S.state.workspace)}/shorts/&lt;id&gt;/v*.mp4, post.txt, meta.json (status, scheduled_at)</pre>
    <p class="mute small">Kroki zależą od usługi: założenie konta, połączenie kanałów, dodanie serwera MCP poleceniem <code>claude mcp add …</code> z jej instrukcji, potem <code>/mcp</code> w Claude Code i logowanie. Publikowane są wyłącznie Shorty, które zatwierdziłeś.</p></div>`;
}

/* ------------------------------------------------------------------ propose */
function propose() {
  return `<h1>Zaproponuj zmianę</h1><p class="sub">Opisz, co dodać albo poprawić. Otworzy się zgłoszenie na GitHubie z Twoim tekstem.</p>
  <div class="card"><textarea id="pr-text" rows="6" placeholder="np. dodaj polskie napisy w stylu…"></textarea>
    <button class="btn blue" style="margin-top:8px" data-act="propose">Otwórz zgłoszenie</button></div>`;
}

/* ------------------------------------------------------------------ settings */
function settings() {
  const s = S.state.settings, up = S.state.update || {};
  return `<h1>Ustawienia</h1><p class="sub">Folder roboczy: <code>${esc(S.state.workspace)}</code> · wersja ${esc(S.state.version)}</p>
  <div class="card"><h2>Język filmów</h2><p class="mute small">Biorę tylko źródła w tym języku. W tym języku są też hooki, tytuły i hashtagi.</p>
    <select data-set="language">${Object.entries(LANGS).map(([k, l]) => `<option value="${k}" ${s.language === k ? "selected" : ""}>${l}</option>`).join("")}</select></div>
  <div class="card"><h2>AI, które wybiera momenty</h2>
    <div class="chips">${Object.entries(AIS).map(([k, l]) => `<span class="chip ${s.ai === k ? "on" : ""}" data-act="set" data-k="ai" data-v="${k}">${l}</span>`).join("")}</div>
    ${s.ai !== "none" ? `<div class="row" style="margin-top:10px"><label class="grow">Polecenie <input type="text" id="ai-cmd" value="${esc(s.ai_commands[s.ai] || "")}" style="width:100%"></label>
      <button class="btn" data-act="ai-save">Zapisz</button></div>
      <p class="small ${S.state.ai_available ? "" : "mute"}">${S.state.ai_available ? "✔ znalezione na tym PC" : "✖ nie znalazłem tego programu na tym PC — bez niego wybór działa jak Free"}</p>
      <p class="mute small">{prompt_text} = cała treść jako argument, {prompt_file} = ścieżka do pliku, bez nich treść idzie na wejście programu.</p>` : ""}
    <h3 style="margin-top:12px">Ile AI</h3>${modesHtml(s.pick_mode, "set-mode")}</div>
  <div class="card"><h2>Wyszukiwanie i wybór</h2><div class="row">
    <label>Szukaj <input type="text" data-set="query" value="${esc(s.query)}"></label>
    <label>Tytuł musi pasować do <input type="text" data-set="title_regex" value="${esc(s.title_regex)}"></label>
    <label>Nie starsze niż <input type="number" data-set="within_hours" value="${s.within_hours}" style="width:70px"> h</label>
    <label>Shortsów na przebieg <input type="number" data-set="shorts_per_run" value="${s.shorts_per_run}" style="width:60px"></label>
    <label>Maks. z jednego źródła <input type="number" data-set="max_per_source" value="${s.max_per_source}" style="width:60px"></label>
    <label>Długość <input type="number" data-set="min_len" value="${s.min_len}" style="width:55px">–<input type="number" data-set="max_len" value="${s.max_len}" style="width:55px"> s</label></div></div>
  <div class="card"><h2>Komputer</h2><div class="row">
    <label>Model mowy <select data-set="whisper_model">${["tiny", "base", "small", "medium", "large-v3"].map((m) => `<option ${s.whisper_model === m ? "selected" : ""}>${m}</option>`).join("")}</select></label>
    <label>Montaż naraz <input type="number" data-set="workers" min="1" max="8" value="${s.workers}" style="width:60px"></label></div>
    <p class="mute small">Na Macu transkrypcja idzie na procesorze. Starszy Mac albo MacBook Air: model „base” i 1 montaż naraz.</p></div>
  <div class="card"><h2>Polowanie na żywo</h2><div class="row">
    <label>Skok czatu × <input type="number" step="0.5" data-set-live="ratio" value="${s.live.ratio}" style="width:60px"></label>
    <label>Min. wiadomości / min <input type="number" data-set-live="min_per_min" value="${s.live.min_per_min}" style="width:70px"></label>
    <label>Sekund przed <input type="number" data-set-live="before" value="${s.live.before}" style="width:60px"></label>
    <label>Sekund po <input type="number" data-set-live="after" value="${s.live.after}" style="width:60px"></label>
    <label>AI przy klipie <select data-set-live="mode">${["smart", "free"].map((m) => `<option ${s.live.mode === m ? "selected" : ""}>${m}</option>`).join("")}</select></label></div>
    <p class="mute small">Skok = tylu różnych piszących w 10 s, ile zwykle × mnożnik. Hałaśliwy czat: mnożnik 2 i minimum 40.</p></div>
  <div class="card"><h2>Aktualizacje</h2>
    <label class="chk"><input type="checkbox" data-set-upd="auto_check" ${s.updates.auto_check ? "checked" : ""}> sprawdzaj co 5 godzin</label>
    <div class="row" style="margin-top:8px"><button class="btn" data-act="update-check">Sprawdź teraz</button>
      ${up.available ? `<button class="btn blue" data-act="update-apply">Aktualizuj teraz</button>` : ""}
      <span class="mute small">${up.error ? "nie udało się sprawdzić" : up.available ? `nowa wersja (${up.behind} zmian)` : up.local ? "masz najnowszą" : ""}</span></div>
    <p class="mute small">Aktualizacja to <code>git pull</code> repozytorium. Jeśli się nie uda, nic nie zmienia. Shorty i ustawienia są w folderze roboczym i zostają.</p></div>
  <div class="card"><button class="btn" data-act="wizard">Uruchom kreator od nowa</button></div>`;
}
after.settings = () => {
  after.look();
  document.querySelectorAll("[data-set-live],[data-set-upd]").forEach((el) => el.addEventListener("change", async () => {
    const live = el.dataset.setLive, k = live || el.dataset.setUpd;
    const v = el.type === "checkbox" ? el.checked : el.type === "number" ? +el.value : el.value;
    await api("/api/settings", { [live ? "live" : "updates"]: { [k]: v } }); await refresh(false); toast("Zapisane");
  }));
  document.querySelectorAll("input[name=set-mode]").forEach((el) => el.addEventListener("change", async () => {
    await api("/api/settings", { pick_mode: el.value }); await refresh();
  }));
};

/* ------------------------------------------------------------------ wizard */
function openWizard() {
  const s = S.state.settings;
  S.wiz = S.wiz || { step: 1, language: s.language || "en", ai: s.ai || "claude",
    picked: Object.fromEntries((S.state.streamers.length ? S.state.streamers : S.state.suggested).map((x) => [x.name, x.platform])) };
  drawWizard();
}
function drawWizard() {
  const W = S.wiz;
  const all = [...S.state.suggested];
  for (const [n, p] of Object.entries(W.picked)) if (!all.some((x) => x.name === n)) all.push({ name: n, platform: p });
  let body = "";
  if (W.step === 1) body = `<div class="steps">Krok 1 z 3</div><h2>Język filmów</h2>
    <p class="mute">Biorę streamy w tym języku i w nim piszę hooki. Zmienisz to później w Ustawieniach.</p>
    <div class="langs">${Object.entries(LANGS).map(([k, l]) => `<span class="chip ${W.language === k ? "on" : ""}" data-act="wz-lang" data-v="${k}">${l}</span>`).join("")}</div>`;
  if (W.step === 2) body = `<div class="steps">Krok 2 z 3</div><h2>Kogo klipować?</h2>
    <p class="mute">Duzi streamerzy GTA 6. Odznacz tych, których nie chcesz. <b>Klipuj tylko tych, którzy na to pozwalają.</b></p>
    <div class="chips">${all.map((x) => `<span class="chip ${W.picked[x.name] ? "on" : ""}" data-act="wz-st" data-n="${esc(x.name)}" data-p="${x.platform}">${esc(x.name)} <span class="plat ${x.platform}">${x.platform}</span></span>`).join("")}</div>
    <div class="row" style="margin-top:10px"><input type="text" id="wz-add" placeholder="Dodaj streamera: link Twitch, YouTube, Kick albo nazwa" style="flex:1"><button class="btn" data-act="wz-add">Dodaj</button></div>
    <p class="mute small">${Object.keys(W.picked).length} wybranych</p>`;
  if (W.step === 3) body = `<div class="steps">Krok 3 z 3</div><h2>Które AI wybiera momenty?</h2>
    <p class="mute">Używa Twojego istniejącego planu. „Bez AI” też działa — wybiera po głośności i czacie.</p>
    <div class="chips">${Object.entries(AIS).map(([k, l]) => `<span class="chip ${W.ai === k ? "on" : ""}" data-act="wz-ai" data-v="${k}">${l}</span>`).join("")}</div>`;
  overlay(`<div class="row between"><span></span><a href="#" data-act="wz-skip" class="small">Pomiń kreator</a></div>${body}
    <div class="row between" style="margin-top:18px">${W.step > 1 ? `<button class="btn" data-act="wz-back">Wstecz</button>` : "<span></span>"}
      <button class="btn blue big" data-act="wz-next">${W.step === 3 ? "Zakończ" : "Dalej"}</button></div>`, "wiz");
}
async function finishWizard(skip) {
  const W = S.wiz;
  const streamers = skip ? [] : Object.entries(W.picked).map(([name, platform]) => ({ name, platform }));
  await api("/api/setup/finish", { language: W.language, ai: W.ai, streamers });
  S.wiz = null; closeOverlay(); await refresh(); go("home");
}

/* ------------------------------------------------------------------ overlay */
function overlay(html, cls = "") {
  const o = $("#overlay"); o.innerHTML = `<div class="modal ${cls}">${html}</div>`; o.hidden = false;
}
function closeOverlay() {
  const o = $("#overlay"); o.hidden = true; o.innerHTML = ""; S.review = null; S.detail = null;
  if (S.rec) { S.rec.stop(); S.rec = null; }
}

/* ------------------------------------------------------------------ actions */
const ACT = {
  goto: (d) => go(d.page),
  tab: (d) => { S.tab = d.tab; go("shorts"); },
  group: (d) => { S.group = d.g; render(); },
  qcf: (d) => { S.qc = d.qc; render(); },
  mtab: (d) => { S.makeTab = d.t; render(); },
  close: () => { closeOverlay(); render(); },
  "review-start": () => {
    const list = S.page === "shorts" ? filtered() : S.shorts.filter((x) => x.status === "new");
    if (!list.length) return toast("Nie ma nic do przejrzenia");
    openReview(list);
  },
  "rv-prev": () => { S.review.i = Math.max(0, S.review.i - 1); drawReview(); },
  "rv-next": () => { S.review.i++; drawReview(); },
  "rv-approve": () => reviewDecide("approved"),
  "rv-reject": () => reviewDecide("rejected"),
  "rv-change": async () => {
    const t = $("#rv-change").value.trim(); if (!t) return;
    await api(`/api/shorts/${S.review.list[S.review.i]}/change`, { request: t }); toast("Robię nową wersję — oryginał zostaje");
  },
  detail: (d) => openDetail(d.id),
  "set-version": async (d) => { await api(`/api/shorts/${S.detail}/current`, { index: +d.i }); await refresh(); drawDetail(); },
  "d-status": async (d) => { await api(`/api/shorts/${S.detail}/status`, { status: d.s }); await refresh(); drawDetail(); },
  "fill-change": (d) => { $("#d-change").value = d.t; },
  "d-change": async () => {
    const t = $("#d-change").value.trim(); if (!t) return toast("Napisz, co zmienić");
    await api(`/api/shorts/${S.detail}/change`, { request: t }); toast("Robię nową wersję"); await refresh(); drawDetail();
  },
  "d-look": async () => {
    const look = { style: $("#d-style").value, layout: $("#d-layout").value, flip: $("#d-flip").checked, watermark: $("#d-wm").value };
    await api(`/api/shorts/${S.detail}/look`, { look }); toast("Robię wersję z nowym wyglądem"); await refresh(); drawDetail();
  },
  rec: () => toggleRec(),
  "d-voice": async () => {
    // Safari records audio/mp4, Chrome audio/webm
    const f = $("#d-voice").files[0] || (S.recBlob && new File([S.recBlob], /mp4/.test(S.recBlob.type) ? "nagranie.m4a" : "nagranie.webm"));
    if (!f) return toast("Wybierz plik albo nagraj głos");
    const data = await blobToDataUrl(f);
    await api(`/api/shorts/${S.detail}/voice`, { name: f.name, data, at: $("#d-at").value });
    S.recBlob = null; toast("Dodaję głos"); await refresh(); drawDetail();
  },
  "d-post": async () => {
    await api(`/api/shorts/${S.detail}/post`, { title: $("#d-title").value, hashtags: $("#d-tags").value.split(/\s+/).filter(Boolean), credit: $("#d-credit").value });
    await refresh(); toast("Zapisane");
  },
  "d-copy": () => copy(`${$("#d-title").value}\n\n${$("#d-tags").value}\n\n${$("#d-credit").value}`),
  "d-when": async () => {
    const v = $("#d-when").value; if (!v) return;
    await api(`/api/shorts/${S.detail}/schedule`, { at: Math.floor(new Date(v) / 1000) }); await refresh(); toast("Ustawione");
  },
  "d-unwhen": async () => { await api(`/api/shorts/${S.detail}/schedule`, { at: null }); await refresh(); drawDetail(); },
  "rd-txt": () => {
    const xs = readyList();
    const body = [`GTA Shorts gotowe do publikacji — ${xs.length} szt. Numer = numer pliku wideo („Pobierz klip”).`, ""]
      .concat(xs.map((x, i) => `===== ${String(i + 1).padStart(2, "0")} — plik ${readyName(x, i)}.mp4 =====\nTYTUŁ:\n${x.title || x.hook}\n\nOPIS:\n${postDescription(x)}\n`));
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([body.join("\n")], { type: "text/plain;charset=utf-8" }));
    a.download = `opisy-gotowe-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  },
  "rd-copy": (d) => { const f = readyFields(d.id); copy(d.what === "title" ? f.title : f.desc); },
  "rd-save": async (d) => {
    const f = readyFields(d.id);
    const tags = (f.desc.match(/#[^\s#]+/g) || []);
    const credit = f.desc.split("\n").filter((l) => l.trim() && !/^\s*#/.test(l)).join("\n");
    await api(`/api/shorts/${d.id}/post`, { title: f.title, hashtags: tags, credit });
    await refresh(); toast("Zapisane");
  },
  "rd-pub": async (d) => { await api(`/api/shorts/${d.id}/published`, { published: true }); await refresh(); toast("Przeniesione do opublikowanych"); },
  "copy-posts": async () => { const r = await api("/api/posttext?status=approved"); if (!r.text) return toast("Brak zatwierdzonych"); copy(r.text); },
  "live-start": async () => {
    const r = await api("/api/live/start", {});
    toast(r.channels.length ? `Poluję: ${r.channels.join(", ")}` : "Zaznacz „obserwuj na żywo” przy streamerach z Twitcha"); await refresh();
  },
  "live-stop": async () => { await api("/api/live/stop", {}); await refresh(); },
  "st-add": async () => { const t = $("#st-add").value.trim(); if (!t) return; await api("/api/streamers/add", { text: t }); await refresh(); },
  "st-del": async (d) => { const items = S.state.streamers; items.splice(+d.i, 1); await api("/api/streamers", { items }); await refresh(); },
  "st-past": async (d) => {
    const box = $(`#past-${d.i}`); box.innerHTML = `<span class="mute small">Szukam ostatnich streamów…</span>`;
    try {
      const xs = await api("/api/streamers/past", { name: S.state.streamers[+d.i].name });
      box.innerHTML = xs.length ? `<table class="t">${xs.map((x) => `<tr><td>${esc(x.title)}</td><td class="mute">${x.duration ? Math.round(x.duration / 60) + " min" : ""}</td>
        <td><button class="btn small" data-act="make-url" data-url="${esc(x.url)}">Zrób Shorty</button></td></tr>`).join("")}</table>` : `<span class="mute small">Nic nie znalazłem.</span>`;
    } catch (e) { box.innerHTML = `<span class="small">Błąd: ${esc(e.message)}</span>`; }
  },
  "make-url": async (d) => { await api("/api/make", { urls: d.url }); toast("Robię Shorty z tego streamu"); await refresh(); },
  make: async () => { await api("/api/make", makeBody()); toast("Zaczynam. Postęp w „Zadania”."); await refresh(); },
  "make-preview": async () => { const r = await api("/api/make/preview", makeBody()); $("#mk-cmd").innerHTML = `<code>${esc(r.cmd)}</code>`; },
  "ap-save": async () => {
    const days = [...document.querySelectorAll(".ap-day")].filter((x) => x.checked).map((x) => +x.value);
    await api("/api/autopilot", { time: $("#ap-time").value, count: +$("#ap-count").value, days }); await refresh(); toast("Zapisane");
  },
  "ap-toggle": async () => {
    const days = [...document.querySelectorAll(".ap-day")].filter((x) => x.checked).map((x) => +x.value);
    const on = !S.state.settings.autopilot.enabled;
    const r = await api("/api/autopilot", { time: $("#ap-time").value, count: +$("#ap-count").value, days, enabled: on });
    toast(r.ok ? (on ? "Autopilot włączony" : "Autopilot wyłączony") : "Nie udało się: " + (r.out || "")); await refresh();
  },
  "ap-preview": async () => {
    const r = await api("/api/autopilot/preview", {});
    const o = $("#ap-out"); o.hidden = false;
    o.textContent = `${r.kind}\n\nCo uruchomi o wybranej porze:\n${r.run}\n\n${r.install ? "Instalacja: " + r.install.join(" ") : r.line ? "Wpis: " + r.line : ""}`;
  },
  "ap-run": async () => { await api("/api/autopilot/run", {}); toast("Autopilot ruszył"); await refresh(); },
  "plan-preview": async () => {
    const ids = S.shorts.filter((x) => x.status === "approved" && !x.scheduled_at && !x.published).map((x) => x.id);
    S.planPreview = await api("/api/schedule/auto", { ids, every: +$("#pl-every").value, first: $("#pl-first").value, preview: true }); render();
  },
  "plan-apply": async () => {
    const ids = S.shorts.filter((x) => x.status === "approved" && !x.scheduled_at && !x.published).map((x) => x.id);
    await api("/api/settings", { post_every_min: +$("#pl-every").value, post_first_at: $("#pl-first").value });
    await api("/api/schedule/auto", { ids, every: +$("#pl-every").value, first: $("#pl-first").value }); S.planPreview = null; await refresh(); toast("Rozplanowane");
  },
  unslot: async (d) => { await api(`/api/shorts/${d.id}/schedule`, { at: null }); await refresh(); },
  set: async (d) => { await api("/api/settings", { [d.k]: d.v }); await refresh(); },
  "ai-save": async () => { const s = S.state.settings; await api("/api/settings", { ai_commands: { [s.ai]: $("#ai-cmd").value } }); await refresh(); toast("Zapisane"); },
  "update-check": async () => { await api("/api/update/check", {}); await refresh(); },
  "update-apply": async () => {
    if (!confirm("Zaktualizować aplikację? Shorty i ustawienia zostaną.")) return;
    const r = await api("/api/update/apply", {});
    if (r.ok) { toast("Zaktualizowano — restart…", 5000); setTimeout(() => location.reload(), 4000); } else toast("Nie udało się. Nic nie zmieniłem.");
  },
  propose: async () => { const t = $("#pr-text").value.trim(); if (!t) return; const r = await api("/api/propose", { text: t }); window.open(r.url, "_blank"); },
  "job-log": async (d) => {
    const r = await api(`/api/jobs/${d.id}/log`);
    overlay(`<div class="row between"><h2 style="margin:0">Log zadania</h2><button class="btn" data-act="close">Zamknij</button></div><div class="log" style="max-height:70vh;margin-top:10px">${esc(r.lines.join("\n"))}</div>`, "wide");
  },
  wizard: () => { S.wiz = null; openWizard(); },
  "wz-lang": (d) => { S.wiz.language = d.v; drawWizard(); },
  "wz-ai": (d) => { S.wiz.ai = d.v; drawWizard(); },
  "wz-st": (d) => { if (S.wiz.picked[d.n]) delete S.wiz.picked[d.n]; else S.wiz.picked[d.n] = d.p; drawWizard(); },
  "wz-add": () => {
    const t = $("#wz-add").value.trim(); if (!t) return;
    const plat = /kick\.com/i.test(t) ? "kick" : /youtu/i.test(t) ? "youtube" : "twitch";
    const name = t.includes("/") ? t.replace(/\/+$/, "").split("/").pop().replace(/^@/, "") : t.replace(/^@/, "");
    S.wiz.picked[name] = plat; drawWizard();
  },
  "wz-back": () => { S.wiz.step--; drawWizard(); },
  "wz-next": () => { if (S.wiz.step < 3) { S.wiz.step++; drawWizard(); } else finishWizard(false); },
  "wz-skip": () => finishWizard(true),
};

document.addEventListener("click", async (e) => {
  const nav = e.target.closest("#side button"); if (nav) return go(nav.dataset.page);
  const el = e.target.closest("[data-act]"); if (!el) return;
  if (el.tagName === "A") e.preventDefault();
  const fn = ACT[el.dataset.act]; if (!fn) return;
  try { await fn(el.dataset); } catch (err) { toast("Błąd: " + err.message, 5000); }
});
document.addEventListener("keydown", (e) => {
  if (!S.review || ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
    if (e.key === "Escape" && !$("#overlay").hidden && !S.wiz) { closeOverlay(); render(); }
    return;
  }
  const k = e.key.toLowerCase();
  if (k === "a") ACT["rv-approve"]();
  else if (k === "x") ACT["rv-reject"]();
  else if (e.key === "ArrowRight") ACT["rv-next"]();
  else if (e.key === "ArrowLeft") ACT["rv-prev"]();
  else if (e.key === " ") { e.preventDefault(); const v = $("#rv-video"); if (v) v.paused ? v.play() : v.pause(); }
  else if (e.key === "Escape") { closeOverlay(); render(); }
});

/* ------------------------------------------------------------------ refresh loop */
async function refresh(redraw = true) {
  await load();
  if (redraw && $("#overlay").hidden) render();
}
async function poll() {
  try {
    const st = await api("/api/state");
    const sig = JSON.stringify(st.jobs.map((j) => [j.id, j.status])) + JSON.stringify(st.live.map((l) => l.events.length));
    const changed = sig !== S.lastJobs;
    S.lastJobs = sig; S.state = st;
    if (changed) {
      S.shorts = await api("/api/shorts");
      if (S.detail && !S.review) drawDetail();
    }
    const typing = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName);
    if ($("#overlay").hidden) {
      if (S.page === "home") { const y = $("#main").scrollTop; render(); $("#main").scrollTop = y; }
      else if (["make", "streamers"].includes(S.page)) {   // only the live parts, never the form
        const jb = $("#jobs-box"); if (jb) jb.innerHTML = jobsInner();
        const lb = $("#live-box"); if (lb) lb.innerHTML = liveInner();
      } else if (changed && !typing) render();
    }
  } catch { /* server restarting */ }
  setTimeout(poll, 3000);
}
(async () => { await load(); go("home"); poll(); })();
