"""Chat: replay parsing (YouTube live chat, Twitch rechat), live Twitch IRC reader, spike detector."""
from __future__ import annotations

import json
import re
import socket
import statistics
import threading
import time
from collections import Counter, deque
from pathlib import Path

BOTS = {"nightbot", "streamelements", "streamlabs", "moobot", "fossabot", "wizebot", "sery_bot",
        "soundalerts", "pokemoncommunitygame", "kofistreambot", "botrixoficial", "own3d", "blerp"}
LINK = re.compile(r"https?://|www\.|\.com\b|\.tv\b", re.I)


def counts(author: str, text: str) -> bool:
    """Should this chat message count for spike detection?"""
    a = (author or "").lower().lstrip("@")
    if a in BOTS or a.endswith("bot"):
        return False
    t = (text or "").strip()
    if not t or t.startswith("!") or LINK.search(t):
        return False
    return True


# --------------------------------------------------------------------- replay
def parse_youtube_live_chat(path: Path) -> list[tuple[float, str, str]]:
    out = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            r = d.get("replayChatItemAction") or {}
            try:
                off = int(r.get("videoOffsetTimeMsec", 0)) / 1000.0
            except (TypeError, ValueError):
                continue
            for a in r.get("actions", []):
                item = (a.get("addChatItemAction") or {}).get("item") or {}
                m = item.get("liveChatTextMessageRenderer") or item.get("liveChatPaidMessageRenderer")
                if not m:
                    continue
                runs = (m.get("message") or {}).get("runs", [])
                text = "".join(r.get("text") or ((r.get("emoji") or {}).get("shortcuts") or [""])[0] for r in runs)
                author = (m.get("authorName") or {}).get("simpleText", "")
                out.append((off, author, text))
    return out


def parse_twitch_rechat(path: Path) -> list[tuple[float, str, str]]:
    try:
        d = json.load(open(path, "r", encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    comments = d.get("comments", d if isinstance(d, list) else [])
    out = []
    for c in comments:
        try:
            out.append((float(c.get("content_offset_seconds", 0)),
                        (c.get("commenter") or {}).get("display_name", ""),
                        (c.get("message") or {}).get("body", "")))
        except (TypeError, ValueError):
            continue
    return out


def load_replay(src_dir: Path, sid: str) -> list[tuple[float, str, str]]:
    for p in src_dir.glob(f"{sid}*.live_chat.json"):
        return parse_youtube_live_chat(p)
    for p in src_dir.glob(f"{sid}*.rechat.json"):
        return parse_twitch_rechat(p)
    p = src_dir / f"{sid}.chat.json"  # our own normalized format
    if p.exists():
        return [tuple(x) for x in json.load(open(p, encoding="utf-8"))]
    return []


def top_tokens(msgs: list[tuple[float, str, str]], n: int = 1) -> list[str]:
    c = Counter()
    for _, _, t in msgs:
        for tok in set(re.findall(r"[A-Za-z][A-Za-z0-9]{1,15}|[\U0001F300-\U0001FAFF]", t)):
            c[tok] += 1
    return [t for t, k in c.most_common(n) if k >= 3]


# ----------------------------------------------------------- Twitch VOD chat
# Twitch has no official API for the chat of past broadcasts. Its own web player loads it from
# Twitch's GraphQL endpoint with the public web client id (the same one yt-dlp uses for VODs);
# tools like TwitchDownloader do the same. Unofficial: it can stop working any day — then the
# clipper simply carries on without the chat signal.
TWITCH_GQL = "https://gql.twitch.tv/gql"
TWITCH_WEB_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
VOD_COMMENTS_HASH = "b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a"


def _gql_post(body: list) -> list:
    import urllib.request

    req = urllib.request.Request(TWITCH_GQL, data=json.dumps(body).encode(),
                                 headers={"Client-ID": TWITCH_WEB_CLIENT_ID, "Content-Type": "text/plain;charset=UTF-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _comments_page(vod_id: str, offset: float | None = None, cursor: str | None = None, post=None):
    variables = {"videoID": vod_id}
    if cursor:
        variables["cursor"] = cursor
    else:
        variables["contentOffsetSeconds"] = int(offset or 0)
    res = (post or _gql_post)([{"operationName": "VideoCommentsByOffsetOrCursor", "variables": variables,
                                "extensions": {"persistedQuery": {"version": 1, "sha256Hash": VOD_COMMENTS_HASH}}}])
    item = res[0] if isinstance(res, list) and res else res
    if item.get("errors"):
        raise RuntimeError("; ".join(str(e.get("message")) for e in item["errors"])[:200])
    comments = ((item.get("data") or {}).get("video") or {}).get("comments")
    if comments is None:
        raise RuntimeError("brak czatu dla tego nagrania")
    return comments.get("edges") or [], (comments.get("pageInfo") or {}).get("hasNextPage", False)


def fetch_twitch_vod_chat(vod_id: str, start: float, end: float, out: Path, post=None,
                          sleep: float = 0.05) -> int:
    """Save the chat of [start, end] of a Twitch VOD as [[offset_s, author, text], ...]. Returns message count.

    Pages by cursor (fast); if Twitch refuses cursors, falls back to paging by time offset."""
    vod_id = str(vod_id).lstrip("v")
    msgs: list[list] = []
    seen: set[str] = set()

    def take(edges) -> float:
        last = -1.0
        for e in edges:
            n = e.get("node") or {}
            cid = n.get("id") or f"{n.get('contentOffsetSeconds')}-{len(seen)}"
            if cid in seen:
                continue
            seen.add(cid)
            off = float(n.get("contentOffsetSeconds") or 0)
            last = max(last, off)
            if start <= off <= end:
                text = "".join(f.get("text", "") for f in (n.get("message") or {}).get("fragments") or [])
                msgs.append([off, (n.get("commenter") or {}).get("displayName", ""), text])
        return last

    try:
        edges, more = _comments_page(vod_id, offset=start, post=post)
        last = take(edges)
        mode = "cursor"
        while more and edges and last <= end:
            try:
                edges, more = _comments_page(vod_id, cursor=edges[-1].get("cursor"), post=post)
            except RuntimeError:
                mode = "offset"
                break
            last = max(last, take(edges))
            time.sleep(sleep)
        if mode == "offset":  # cursor paging refused: walk forward by time offset
            t = max(start, last)
            while t <= end:
                edges, _ = _comments_page(vod_id, offset=t, post=post)
                newest = take(edges)
                t = newest + 1 if newest >= t + 1 else t + 1  # always move forward
                time.sleep(sleep)
    except Exception as e:  # unofficial API: never break the pipeline
        from .util import log
        log(f"  czat z Twitcha niedostępny ({str(e)[:120]}) — wybór bez sygnału czatu")
        if not msgs:
            return 0
    msgs.sort(key=lambda m: m[0])
    Path(out).write_text(json.dumps(msgs, ensure_ascii=False), encoding="utf-8")
    return len(msgs)


# --------------------------------------------------------------- live Twitch
class TwitchChat(threading.Thread):
    """Anonymous read-only Twitch IRC client (no login needed)."""

    def __init__(self, channel: str, on_message):
        super().__init__(daemon=True)
        self.channel = channel.lower().lstrip("#")
        self.on_message = on_message
        self.stop_flag = threading.Event()
        self.connected = False

    def run(self):
        while not self.stop_flag.is_set():
            try:
                self._loop()
            except OSError:
                self.connected = False
                time.sleep(5)

    def _loop(self):
        s = socket.create_connection(("irc.chat.twitch.tv", 6667), timeout=30)
        s.sendall(b"CAP REQ :twitch.tv/tags\r\n")
        s.sendall(b"PASS SCHMOOPIIE\r\nNICK justinfan%d\r\n" % (int(time.time()) % 90000 + 10000))
        s.sendall(f"JOIN #{self.channel}\r\n".encode())
        self.connected = True
        buf = b""
        while not self.stop_flag.is_set():
            try:
                data = s.recv(65536)
            except socket.timeout:
                s.sendall(b"PING :tmi.twitch.tv\r\n")
                continue
            if not data:
                raise OSError("chat disconnected")
            buf += data
            while b"\r\n" in buf:
                line, buf = buf.split(b"\r\n", 1)
                self._handle(line.decode("utf-8", "replace"), s)
        s.close()

    def _handle(self, line: str, s):
        if line.startswith("PING"):
            s.sendall(b"PONG :tmi.twitch.tv\r\n")
            return
        m = re.match(r"(?:@(\S+) )?:(\w+)!\S+ PRIVMSG #\w+ :(.*)", line)
        if m:
            tags = dict(kv.split("=", 1) for kv in (m.group(1) or "").split(";") if "=" in kv)
            author = tags.get("display-name") or m.group(2)
            self.on_message(time.time(), author, m.group(3))


class SpikeDetector:
    """A spike = distinct chatters in the last `window` seconds reach `ratio` x the
    stream's own baseline (median of recent windows), while chat is busy enough."""

    def __init__(self, ratio: float = 3.0, min_per_min: float = 30, window: float = 10, cooldown: float = 60):
        self.ratio, self.min_per_min, self.window, self.cooldown = ratio, min_per_min, window, cooldown
        self.msgs: deque = deque()          # (t, author, text) for last 6 min
        self.history: deque = deque(maxlen=30)  # distinct counts per window, last 5 min
        self.last_spike = 0.0
        self.last_sample = 0.0
        self.lock = threading.Lock()

    def add(self, t: float, author: str, text: str):
        if not counts(author, text):
            return
        with self.lock:
            self.msgs.append((t, author, text))
            while self.msgs and self.msgs[0][0] < t - 360:
                self.msgs.popleft()

    def stats(self, now: float | None = None) -> dict:
        now = now or time.time()
        with self.lock:
            win = [m for m in self.msgs if m[0] >= now - self.window]
            minute = [m for m in self.msgs if m[0] >= now - 60]
        distinct = len({a for _, a, _ in win})
        base = statistics.median(self.history) if len(self.history) >= 6 else None
        return {"distinct": distinct, "per_min": len(minute), "baseline": base, "msgs": win}

    def check(self, now: float | None = None) -> dict | None:
        """Call about once a second. Returns spike info or None."""
        now = now or time.time()
        st = self.stats(now)
        if now - self.last_sample >= self.window:
            self.history.append(st["distinct"])
            self.last_sample = now
        base = st["baseline"]
        if base is None or now - self.last_spike < self.cooldown:
            return None
        if st["per_min"] >= self.min_per_min and st["distinct"] >= max(3, self.ratio * max(base, 1)):
            self.last_spike = now
            return {"t": now, "distinct": st["distinct"], "baseline": base,
                    "ratio": round(st["distinct"] / max(base, 1), 1), "tokens": top_tokens(st["msgs"], 2)}
        return None
