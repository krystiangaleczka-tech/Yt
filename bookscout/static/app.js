"use strict";

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const state = { meta: null, books: [], category: "random", source: "openlibrary", batchId: null,
                rankFilter: "all", selected: null };
const nf = new Intl.NumberFormat("pl-PL");
const compact = new Intl.NumberFormat("pl-PL", { notation: "compact", maximumFractionDigits: 1 });
const VERDICT_CLASS = { "Rób to": "v-0", "Obiecujące": "v-1", "Może": "v-2", "Odpuść": "v-3" };

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const num = (v, f = nf) => (v === null || v === undefined ? '<span class="dim">–</span>' : f.format(v));
const usd = v => (v === null || v === undefined ? '<span class="dim">–</span>' : "$" + nf.format(v));

async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts,
    body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Błąd ${res.status}`);
  return data;
}

function toast(text) {
  const t = $("#toast");
  t.textContent = text;
  t.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (t.hidden = true), 3500);
}

function busy(btn, on, label) {
  if (on) { btn.dataset.label = btn.textContent; btn.textContent = label || "Pracuję…"; btn.disabled = true; }
  else { btn.textContent = btn.dataset.label || btn.textContent; btn.disabled = false; }
}

// ── Dane ────────────────────────────────────────────────────────────────────
async function loadMeta() {
  state.meta = await api("/api/meta");
  const c = state.meta.counts;
  const pending = (c.new || 0) + (c.queued || 0);
  const rated = (c.rated || 0) + (c.analyzed || 0);
  $("#cnt-pending").textContent = pending || "";
  $("#cnt-rated").textContent = rated || "";
  $("#status-pills").innerHTML =
    `<span class="pill ${state.meta.google_key ? "on" : ""}">YouTube API: ${state.meta.google_key ? "włączone" : "brak klucza"}</span>` +
    `<span class="pill">${nf.format(pending)} do oceny</span><span class="pill">${nf.format(rated)} ocenionych</span>`;
  $("#key-status").innerHTML = state.meta.google_key
    ? '<span class="badge v-0">Klucz wczytany</span> YouTube i Google Books są aktywne.'
    : '<span class="badge v-2">Brak klucza</span> Dodaj GOOGLE_API_KEY, żeby włączyć YouTube.';
}

async function loadBooks() {
  state.books = await api("/api/books");
  renderPending();
  renderRanking();
}

async function refresh() {
  await Promise.all([loadMeta(), loadBooks()]);
}

// ── Zakładki ────────────────────────────────────────────────────────────────
function showTab(name) {
  $$(".tabs button").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  $$(".tab").forEach(t => t.classList.toggle("active", t.id === `tab-${name}`));
  try { localStorage.setItem("bookscout.tab", name); } catch (_) { /* brak storage */ }
}

function segment(el, onChange) {
  el.addEventListener("click", e => {
    const b = e.target.closest("button[data-v]");
    if (!b) return;
    $$("button", el).forEach(x => x.classList.toggle("on", x === b));
    onChange(b.dataset.v);
  });
}

// ── 1. Losowanie ────────────────────────────────────────────────────────────
function renderChips() {
  const cats = [{ key: "random", label: "Losowo", bn: true }, ...state.meta.categories];
  $("#cat-chips").innerHTML = cats.map(c =>
    `<button class="chip ${c.key === "random" ? "random" : ""} ${c.key === state.category ? "on" : ""}
      ${state.source === "bn" && !c.bn ? "nobn" : ""}" data-key="${c.key}">${esc(c.label)}</button>`).join("");
}

function availabilityBadge(key) {
  const a = state.meta.availability[key] || state.meta.availability.unknown;
  return `<span class="badge av-${esc(key)}">${esc(a.label)}</span>`;
}

function categoryLabel(key) {
  return (state.meta.categories.find(c => c.key === key) || {}).label || key;
}

function bookCard(b, isNew) {
  const subjects = (b.subjects || []).slice(0, 4).map(s => `<span class="tag">${esc(String(s).slice(0, 40))}</span>`).join("");
  return `<article class="card ${isNew ? "new" : ""}">
    <button class="x" title="Odrzuć" data-dismiss="${esc(b.id)}">×</button>
    <h4>${esc(b.title)}</h4>
    <div class="meta">${esc(b.author || "autor nieznany")} · ${esc(b.year || "b.d.")} · ${esc(b.language || "")}</div>
    <div class="tags">${availabilityBadge(b.availability)}<span class="tag">${esc(categoryLabel(b.category))}</span>
      ${b.status === "queued" ? '<span class="tag">w paczce</span>' : ""}
      ${(b.toc || []).length ? `<span class="tag">spis treści: ${b.toc.length}</span>` : ""}</div>
    ${b.description ? `<p class="desc">${esc(b.description)}</p>` : ""}
    <div class="tags">${subjects}</div>
    <div class="meta" style="margin-top:8px"><a href="${esc(b.url)}" target="_blank" rel="noopener">katalog</a>
      ${(b.availability_detail || []).filter(d => d.url && d.source !== "Open Library").map(d =>
        ` · <a href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.source)}</a>`).join("")}</div>
  </article>`;
}

function renderPending(newIds = new Set()) {
  const pending = state.books.filter(b => b.status === "new" || b.status === "queued");
  $("#pending-info").textContent = pending.length ? `(${pending.length})` : "";
  $("#pending-list").innerHTML = pending.length
    ? pending.map(b => bookCard(b, newIds.has(b.id))).join("")
    : '<p class="muted">Pusto. Wybierz kategorię albo „Losowo” i kliknij „Losuj książki”.</p>';
}

async function draw() {
  const btn = $("#btn-draw");
  busy(btn, true, "Szukam w katalogach…");
  $("#draw-msg").textContent = "";
  try {
    const body = {
      category: state.category, source: state.source,
      count: +$("#draw-count").value || 10, only_offline: $("#only-offline").checked,
      year_from: +$("#year-from").value || null, year_to: +$("#year-to").value || null,
    };
    const res = await api("/api/draw", { method: "POST", body });
    $("#draw-msg").textContent = `Nowe: ${res.added.length} (kategorie: ${res.categories.join(", ")})` +
      (res.duplicates ? `, pominięte duplikaty: ${res.duplicates}` : "") +
      (res.drawn < body.count ? `. Katalog zwrócił mniej pasujących książek (${res.drawn}).` : "");
    await loadMeta();
    state.books = await api("/api/books");
    renderPending(new Set(res.added.map(b => b.id)));
    renderRanking();
  } catch (e) {
    $("#draw-msg").innerHTML = `<span class="err">${esc(e.message)}</span>`;
  } finally {
    busy(btn, false);
  }
}

async function setFlag(id, flag) {
  await api(`/api/books/${encodeURIComponent(id)}/flag`, { method: "POST", body: { flag } });
  const b = state.books.find(x => x.id === id);
  if (flag === "dismissed") state.books = state.books.filter(x => x.id !== id);
  else if (b) b.flag = flag;
  if (state.selected === id && flag === "dismissed") state.selected = null;
  renderPending();
  renderRanking();
  loadMeta();
}

// ── 2. Claude ───────────────────────────────────────────────────────────────
function importReport(res) {
  const parts = [`Zaimportowano ocen: <b>${res.imported}</b>.`];
  if (res.errors?.length) parts.push(`<span class="err">Błędy:</span><ul>${res.errors.map(e => `<li>${esc(e)}</li>`).join("")}</ul>`);
  if (res.warnings?.length) parts.push(`Uwagi:<ul>${res.warnings.slice(0, 8).map(e => `<li>${esc(e)}</li>`).join("")}</ul>`);
  return parts.join(" ");
}

async function makePrompt() {
  const btn = $("#btn-prompt");
  busy(btn, true);
  try {
    const res = await api("/api/claude/prompt", { method: "POST", body: { count: +$("#batch-count").value || 15 } });
    state.batchId = res.batch_id;
    $("#prompt-box").value = res.prompt;
    $("#btn-copy").disabled = false;
    $("#import-msg").textContent = `Paczka ${res.batch_id}: ${res.ids.length} książek.`;
    await refresh();
  } catch (e) {
    $("#import-msg").innerHTML = `<span class="err">${esc(e.message)}</span>`;
  } finally {
    busy(btn, false);
  }
}

async function copyPrompt() {
  const box = $("#prompt-box");
  try { await navigator.clipboard.writeText(box.value); }
  catch (_) { box.select(); document.execCommand("copy"); }
  toast("Prompt skopiowany. Wklej go w Claude.");
}

async function importAnswer() {
  const text = $("#answer-box").value.trim();
  if (!text) { $("#import-msg").innerHTML = '<span class="err">Wklej najpierw odpowiedź Claude.</span>'; return; }
  const btn = $("#btn-import");
  busy(btn, true);
  try {
    const res = await api("/api/claude/import", { method: "POST", body: { text, batch_id: state.batchId } });
    $("#import-msg").innerHTML = importReport(res);
    if (res.imported) { $("#answer-box").value = ""; toast(`Zaimportowano ${res.imported} ocen. Zobacz Ranking.`); }
    await refresh();
  } catch (e) {
    $("#import-msg").innerHTML = `<span class="err">${esc(e.message)}</span>`;
  } finally {
    busy(btn, false);
  }
}

async function exportFile() {
  try {
    const res = await api("/api/claude/export-file", { method: "POST", body: { count: +$("#batch-count").value || 15 } });
    $("#file-msg").innerHTML = `Zapisano ${res.count} książek do <code>${esc(res.path)}</code>.<br>
      W Claude Code napisz: <code>oceń paczkę Book Scout ${esc(res.batch_id)}</code>`;
    await refresh();
  } catch (e) {
    $("#file-msg").innerHTML = `<span class="err">${esc(e.message)}</span>`;
  }
}

async function importFiles(target) {
  try {
    const res = await api("/api/import-files", { method: "POST" });
    if (!res.batches.length) { target.innerHTML = "Brak nowych odpowiedzi w folderze paczek."; return; }
    target.innerHTML = res.batches.map(b =>
      `${esc(b.batch_id)}: zaimportowano ${b.imported}` +
      (b.errors.length ? ` <span class="err">(${b.errors.length} błędów: ${esc(b.errors.slice(0, 3).join("; "))})</span>` : "")).join("<br>");
    await refresh();
  } catch (e) {
    target.innerHTML = `<span class="err">${esc(e.message)}</span>`;
  }
}

// ── 3. Ranking ──────────────────────────────────────────────────────────────
function rankedBooks() {
  let list = state.books.filter(b => b.rating);
  if (state.rankFilter === "analyzed") list = list.filter(b => b.market);
  if (state.rankFilter === "picked") list = list.filter(b => b.flag === "picked");
  return list.sort((a, b) => (b.scoring.score ?? -1) - (a.scoring.score ?? -1));
}

function renderRanking() {
  const list = rankedBooks();
  const unanalyzed = state.books.filter(b => b.rating && !b.market).length;
  $("#btn-market").textContent = unanalyzed ? `Analizuj rynek (${unanalyzed})` : "Analizuj rynek";
  $("#btn-docos").textContent = `Eksport ★ do DocOS (${state.books.filter(b => b.flag === "picked" && b.rating).length})`;
  $("#rank-empty").hidden = list.length > 0;
  $("#rank-table tbody").innerHTML = list.map(b => {
    const s = b.scoring, r = b.rating;
    const ratio = s.opportunity_ratio;
    return `<tr data-id="${esc(b.id)}" class="${state.selected === b.id ? "sel" : ""}">
      <td><button class="star ${b.flag === "picked" ? "on" : ""}" data-star="${esc(b.id)}" title="Wybierz do DocOS">★</button></td>
      <td><div class="t1">${esc(r.video_title || b.title)}</div><div class="t2">${esc(b.title.length > 90 ? b.title.slice(0, 88) + "…" : b.title)} · ${esc(b.year || "b.d.")}</div></td>
      <td>${s.score !== null ? `<span class="badge ${VERDICT_CLASS[s.verdict]}">${s.score} · ${esc(s.verdict)}</span>` : "–"}
        ${b.market ? "" : '<div class="t2">bez rynku</div>'}</td>
      <td>${num(s.interest)}</td><td>${num(s.demand)}</td><td>${num(s.competition)}</td>
      <td>${ratio === null ? '<span class="dim">–</span>' : (ratio >= 1.5 ? `<b>${ratio}×</b>` : `${ratio}×`)}</td>
      <td>${num(s.difficulty)}</td>
      <td>${num(s.views, compact)}</td><td>${usd(s.revenue_usd)}</td><td>${usd(s.cost?.usd)}</td>
      <td>${s.roi === null ? '<span class="dim">–</span>' : s.roi + "×"}</td>
      <td>${availabilityBadge(b.availability)}</td>
    </tr>`;
  }).join("");
  renderDetail();
}

function list(items) {
  return items && items.length ? `<ul>${items.map(i => `<li>${esc(i)}</li>`).join("")}</ul>` : '<p class="dim">–</p>';
}

const PART_LABELS = { interest: "Ciekawość", demand: "Popyt", open_field: "Wolne pole", exclusivity: "Wyjątkowość",
                      roi: "ROI", ease: "Łatwość" };

function renderDetail() {
  const el = $("#detail");
  const b = state.books.find(x => x.id === state.selected && x.rating);
  if (!b) { el.hidden = true; return; }
  const r = b.rating, s = b.scoring, m = b.market || {}, yt = m.youtube, wiki = m.wiki;
  const bars = Object.entries(s.parts).map(([k, v]) => `<div class="bar"><span>${PART_LABELS[k]}</span>
    <div class="track"><div class="fill" style="width:${v ?? 0}%"></div></div><span>${v === null ? "–" : Math.round(v)}</span></div>`).join("");
  const competitors = yt?.top_videos?.length ? `<ul>${yt.top_videos.map(v =>
    `<li><a href="https://www.youtube.com/watch?v=${esc(v.id)}" target="_blank" rel="noopener">${esc(v.title)}</a>
     <span class="dim">· ${esc(v.channel || "")} · ${num(v.views, compact)}</span></li>`).join("")}</ul>` : '<p class="dim">Brak danych YouTube.</p>';
  const cost = s.cost ? Object.entries(s.cost.hours).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v} h</dd>`).join("") : "";
  el.hidden = false;
  el.innerHTML = `
    <div class="head">
      <div><h2>${esc(r.video_title || b.title)}</h2>
        <div class="muted">${esc(b.title)} · ${esc(b.author || "")} · ${esc(b.year || "b.d.")} ·
          <a href="${esc(b.url)}" target="_blank" rel="noopener">katalog</a></div>
        ${r.hook ? `<p class="hook">${esc(r.hook)}</p>` : ""}</div>
      <div>${s.score !== null ? `<span class="badge ${VERDICT_CLASS[s.verdict]}" style="font-size:15px">${s.score} · ${esc(s.verdict)}</span>` : ""}
        <div class="t2 muted">dane: ${esc(s.completeness)} składowych</div>
        <button data-analyze="${esc(b.id)}" style="margin-top:8px">${b.market ? "Odśwież rynek" : "Analizuj rynek"}</button></div>
    </div>
    <div class="cols">
      <div>
        <h3>Pytanie filmu</h3><p>${esc(r.central_question || "–")}</p>
        <h3>Ciekawe wątki (do sprawdzenia)</h3>${list(r.interesting_points)}
        <h3>Warstwy</h3>${list(r.layers)}
        <h3>Shorts</h3>${list(r.shorts_ideas)}
      </div>
      <div>
        <h3>Składowe wyniku</h3><div class="bars">${bars}</div>
        <h3>Liczby</h3>
        <dl class="kv">
          <dt>Wyświetlenia (12 mies.)</dt><dd>${num(s.views_low, compact)}–${num(s.views_high, compact)}</dd>
          <dt>Zarobek z reklam</dt><dd>${usd(s.revenue_usd)}${s.monetized ? "" : " (kanał niezarabiający)"}</dd>
          <dt>Koszt filmu</dt><dd>${usd(s.cost?.usd)} · ${s.cost?.total_hours ?? "–"} h</dd>
          <dt>ROI</dt><dd>${s.roi ?? "–"}×</dd>
          <dt>Ratio popyt/konkurencja</dt><dd>${s.opportunity_ratio ?? "–"}×</dd>
          <dt>Ratio wyśw./subskr. (rynek)</dt><dd>${s.outlier_ratio ?? "–"}</dd>
          <dt>Wyświetlenia / trudność</dt><dd>${num(s.value_per_effort, compact)}</dd>
          <dt>Evergreen</dt><dd>${num(r.evergreen)}</dd>
          <dt>Potencjał serii</dt><dd>${num(r.series_potential)}</dd>
          <dt>Materiały wizualne</dt><dd>${num(r.visuals)}/10</dd>
          <dt>Pewność Claude</dt><dd>${num(r.confidence)}</dd>
        </dl>
        <p class="t2 muted">${esc(s.views_basis)}</p>
        <h3>Godziny pracy</h3><dl class="kv">${cost}</dl>
      </div>
      <div>
        <h3>Trudność ${num(r.difficulty)}/10</h3><p>${esc(r.difficulty_reasons || "–")}</p>
        <h3>Ryzyka</h3><p>${esc((r.risk_flags || []).join(", ") || "–")}</p>
        <h3>Wikipedia</h3>
        <p>${wiki?.article ? `<a href="${esc(wiki.url)}" target="_blank" rel="noopener">${esc(wiki.article)}</a> · ${num(wiki.monthly_avg)} odsłon/mies.` +
          (wiki.matched === "search" ? ' <span class="dim">(dopasowane wyszukiwarką — sprawdź, czy trafnie)</span>' : "") : '<span class="dim">–</span>'}</p>
        <h3>Konkurencja na YouTube ${yt ? `<span class="dim">(„${esc(yt.query)}”, ${yt.relevant} trafnych, ${yt.strong} &gt;100 tys.)</span>` : ""}</h3>
        ${competitors}
        <h3>Gdzie szukać</h3>${list(r.research_leads)}
        <div class="tags">${(b.availability_detail || []).map(d => d.url
          ? `<a class="tag" href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.source)}: ${esc(d.status)}</a>`
          : `<span class="tag">${esc(d.source)}: ${esc(d.status)}</span>`).join("")}</div>
      </div>
    </div>`;
}

async function analyzeOne(id) {
  const updated = await api(`/api/market/${encodeURIComponent(id)}`, { method: "POST" });
  const i = state.books.findIndex(b => b.id === id);
  if (i >= 0) state.books[i] = updated;
}

async function analyzeAll() {
  const todo = state.books.filter(b => b.rating && !b.market);
  if (!todo.length) { toast("Wszystkie ocenione tematy mają już analizę rynku."); return; }
  const btn = $("#btn-market");
  busy(btn, true);
  let done = 0;
  const errors = [];
  for (const b of todo) {
    btn.textContent = `Analizuję ${done + 1}/${todo.length}…`;
    try { await analyzeOne(b.id); } catch (e) { errors.push(e.message); if (/quota|API/i.test(e.message)) break; }
    done++;
    renderRanking();
  }
  busy(btn, false);
  renderRanking();
  loadMeta();
  $("#rank-msg").innerHTML = errors.length ? `<span class="err">${esc(errors[0])}</span>` : `Przeanalizowano ${done}.`;
}

async function exportMarketFile() {
  try {
    const res = await api("/api/market/export-file", { method: "POST", body: { count: 10 } });
    $("#rank-msg").innerHTML = `Zapisano ${res.count} tematów. W Claude Code napisz: <code>sprawdź YouTube dla paczki ${esc(res.batch_id)}</code>,
      potem w zakładce Ocena Claude kliknij „Importuj z plików”.`;
  } catch (e) {
    $("#rank-msg").innerHTML = `<span class="err">${esc(e.message)}</span>`;
  }
}

async function exportDocos() {
  try {
    const res = await api("/api/export/docos", { method: "POST", body: {} });
    $("#rank-msg").innerHTML = `Zapisano ${res.count} tematów do <code>${esc(res.path)}</code>.` +
      (res.count === 10 ? " Plik przejdzie wprost przez <code>docos.py save-topics</code>."
        : " <code>save-topics</code> wymaga dokładnie 10 tematów. Pojedynczy temat otwórz przez <code>docos.py new</code>.");
  } catch (e) {
    $("#rank-msg").innerHTML = `<span class="err">${esc(e.message)}</span>`;
  }
}

// ── Ustawienia ──────────────────────────────────────────────────────────────
function fillSettings() {
  const f = $("#settings-form");
  for (const [k, v] of Object.entries(state.meta.settings)) {
    const input = f.elements[k];
    if (!input) continue;
    if (input.type === "checkbox") input.checked = !!v; else input.value = v;
  }
}

async function saveSettings(e) {
  e.preventDefault();
  const f = e.target;
  const values = {};
  for (const k of Object.keys(state.meta.settings)) {
    const input = f.elements[k];
    if (input) values[k] = input.type === "checkbox" ? input.checked : +input.value;
  }
  try {
    state.meta.settings = await api("/api/settings", { method: "PUT", body: values });
    $("#settings-msg").textContent = "Zapisano. Ranking przeliczony.";
    await loadBooks();
  } catch (err) {
    $("#settings-msg").innerHTML = `<span class="err">${esc(err.message)}</span>`;
  }
}

// ── Start ───────────────────────────────────────────────────────────────────
function bind() {
  $(".tabs").addEventListener("click", e => { const b = e.target.closest("button[data-tab]"); if (b) showTab(b.dataset.tab); });
  segment($("#source-seg"), v => { state.source = v; renderChips(); });
  segment($("#rank-filter"), v => { state.rankFilter = v; renderRanking(); });
  $("#cat-chips").addEventListener("click", e => {
    const c = e.target.closest(".chip");
    if (!c) return;
    state.category = c.dataset.key;
    renderChips();
  });
  $("#btn-draw").addEventListener("click", draw);
  $("#pending-list").addEventListener("click", e => { const x = e.target.closest("[data-dismiss]"); if (x) setFlag(x.dataset.dismiss, "dismissed"); });
  $("#btn-prompt").addEventListener("click", makePrompt);
  $("#btn-copy").addEventListener("click", copyPrompt);
  $("#btn-import").addEventListener("click", importAnswer);
  $("#btn-export-file").addEventListener("click", exportFile);
  $("#btn-import-files").addEventListener("click", () => importFiles($("#file-msg")));
  $("#btn-market").addEventListener("click", analyzeAll);
  $("#btn-market-file").addEventListener("click", exportMarketFile);
  $("#btn-docos").addEventListener("click", exportDocos);
  $("#settings-form").addEventListener("submit", saveSettings);
  $("#rank-table tbody").addEventListener("click", e => {
    const star = e.target.closest("[data-star]");
    if (star) {
      const b = state.books.find(x => x.id === star.dataset.star);
      setFlag(b.id, b.flag === "picked" ? "" : "picked");
      return;
    }
    const tr = e.target.closest("tr[data-id]");
    if (!tr) return;
    state.selected = state.selected === tr.dataset.id ? null : tr.dataset.id;
    renderRanking();
    if (state.selected) $("#detail").scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
  $("#detail").addEventListener("click", async e => {
    const btn = e.target.closest("[data-analyze]");
    if (!btn) return;
    busy(btn, true, "Analizuję…");
    try { await analyzeOne(btn.dataset.analyze); renderRanking(); loadMeta(); }
    catch (err) { toast(err.message); busy(btn, false); }
  });
}

(async function init() {
  bind();
  await loadMeta();
  renderChips();
  fillSettings();
  await loadBooks();
  let tab = "draw";
  try { tab = localStorage.getItem("bookscout.tab") || "draw"; } catch (_) { /* brak storage */ }
  showTab(tab);
})();
