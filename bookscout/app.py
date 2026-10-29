"""Book Scout — serwer FastAPI i API dla panelu."""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import claude_batch, config, db, market, scoring, sources

FLAGS = {"", "picked", "dismissed"}


class DrawRequest(BaseModel):
    category: str = "random"
    source: str = "openlibrary"
    count: int = Field(10, ge=1, le=40)
    only_offline: bool = True
    year_from: int | None = None
    year_to: int | None = None


class PromptRequest(BaseModel):
    count: int = Field(15, ge=1, le=40)
    ids: list[str] | None = None


class ImportRequest(BaseModel):
    text: str
    batch_id: str | None = None


class FlagRequest(BaseModel):
    flag: str


class IdsRequest(BaseModel):
    ids: list[str] | None = None
    count: int = Field(10, ge=1, le=40)


def create_app(db_path: Path | None = None) -> FastAPI:
    config.load_env()
    app = FastAPI(title="Book Scout")
    conn = db.connect(db_path)

    def with_score(book: dict, settings: dict) -> dict:
        return {**book, "scoring": scoring.compute(book, settings)}

    def save_ratings(ratings: dict) -> int:
        for book_id, rating in ratings.items():
            book = db.get_book(conn, book_id)
            if book:
                db.update_book(conn, book_id, rating=rating,
                               status="analyzed" if book.get("market") else "rated")
        return len(ratings)

    @app.get("/")
    def index():
        return FileResponse(config.STATIC_DIR / "index.html")

    @app.get("/api/meta")
    def meta():
        return {
            "categories": [{"key": c.key, "label": c.label, "bn": bool(c.bn)} for c in config.CATEGORIES],
            "availability": config.AVAILABILITY,
            "settings": db.get_settings(conn),
            "google_key": bool(config.google_api_key()),
            "counts": db.counts(conn),
            "paths": {"batches": str(config.BATCH_DIR), "exports": str(config.EXPORT_DIR)},
        }

    @app.put("/api/settings")
    def put_settings(values: dict):
        try:
            return db.save_settings(conn, values)
        except (TypeError, ValueError) as exc:
            raise HTTPException(400, f"Złe ustawienie: {exc}")

    @app.post("/api/draw")
    async def draw(req: DrawRequest):
        if req.category == "random":
            pool = [c for c in config.CATEGORIES if req.source != "bn" or c.bn]
            cats = random.sample(pool, k=min(len(pool), max(1, -(-req.count // 5))))
        elif req.category in config.CATEGORY_BY_KEY:
            cats = [config.CATEGORY_BY_KEY[req.category]]
        else:
            raise HTTPException(400, "Nieznana kategoria")
        if req.source not in ("openlibrary", "bn", "both"):
            raise HTTPException(400, "Nieznane źródło")
        try:
            books = await sources.draw(cats, req.source, req.count, req.only_offline, req.year_from, req.year_to,
                                       config.google_api_key())
        except Exception as exc:  # noqa: BLE001 — błąd zewnętrznego katalogu pokazujemy w panelu
            raise HTTPException(502, f"Katalog nie odpowiedział: {exc}")
        added = db.insert_books(conn, books)
        settings = db.get_settings(conn)
        return {"added": [with_score(db.get_book(conn, b["id"]), settings) for b in added],
                "drawn": len(books), "duplicates": len(books) - len(added),
                "categories": [c.label for c in cats]}

    @app.get("/api/books")
    def books(status: str | None = None, include_dismissed: bool = False):
        settings = db.get_settings(conn)
        statuses = status.split(",") if status else None
        return [with_score(b, settings) for b in db.list_books(conn, statuses, include_dismissed)]

    @app.post("/api/books/{book_id}/flag")
    def set_flag(book_id: str, req: FlagRequest):
        if req.flag not in FLAGS:
            raise HTTPException(400, "Nieznana flaga")
        if not db.get_book(conn, book_id):
            raise HTTPException(404, "Nie ma takiej książki")
        db.update_book(conn, book_id, flag=req.flag)
        return {"ok": True}

    # ── Claude: kopiuj/wklej ────────────────────────────────────────────────
    def pick_for_rating(req: PromptRequest) -> list[dict]:
        if req.ids:
            chosen = [db.get_book(conn, i) for i in req.ids]
            return [b for b in chosen if b]
        pending = db.list_books(conn, ["new", "queued"])
        pending.sort(key=lambda b: (b["status"] != "new", b["created_at"]))
        return pending[: req.count]

    @app.post("/api/claude/prompt")
    def claude_prompt(req: PromptRequest):
        chosen = pick_for_rating(req)
        if not chosen:
            raise HTTPException(400, "Brak książek do oceny — najpierw wylosuj.")
        batch_id = db.create_batch(conn, "rate", [b["id"] for b in chosen])
        for b in chosen:
            db.update_book(conn, b["id"], status="queued" if b["status"] == "new" else b["status"], batch_id=batch_id)
        return {"batch_id": batch_id, "ids": [b["id"] for b in chosen],
                "prompt": claude_batch.build_prompt(chosen, db.get_settings(conn))}

    @app.post("/api/claude/import")
    def claude_import(req: ImportRequest):
        batch = db.get_batch(conn, req.batch_id) if req.batch_id else None
        expected = batch["book_ids"] if batch else [b["id"] for b in db.list_books(conn, include_dismissed=True)]
        result = claude_batch.parse_response(req.text, expected)
        imported = save_ratings(result["ratings"])
        if batch and imported:
            db.mark_batch_imported(conn, batch["id"])
        return {"imported": imported, "errors": result["errors"], "warnings": result["warnings"]}

    # ── Claude Code: pliki ──────────────────────────────────────────────────
    @app.post("/api/claude/export-file")
    def claude_export_file(req: PromptRequest):
        data = claude_prompt(req)
        config.BATCH_DIR.mkdir(parents=True, exist_ok=True)
        path = config.BATCH_DIR / f"{data['batch_id']}.prompt.md"
        path.write_text(claude_batch.file_prompt(data["batch_id"], data["prompt"]), encoding="utf-8")
        return {"batch_id": data["batch_id"], "count": len(data["ids"]), "path": str(path)}

    @app.post("/api/market/export-file")
    def market_export_file(req: IdsRequest):
        chosen = [db.get_book(conn, i) for i in req.ids] if req.ids else db.list_books(conn, ["rated"])[: req.count]
        chosen = [b for b in chosen if b and b.get("rating")]
        if not chosen:
            raise HTTPException(400, "Brak ocenionych książek bez analizy rynku.")
        batch_id = db.create_batch(conn, "market", [b["id"] for b in chosen])
        items = [{"id": b["id"], "query": b["rating"].get("youtube_query") or b["title"]} for b in chosen]
        config.BATCH_DIR.mkdir(parents=True, exist_ok=True)
        path = config.BATCH_DIR / f"{batch_id}.prompt.md"
        path.write_text(market.MARKET_FILE_HEADER.format(batch_id=batch_id,
                                                         response_name=claude_batch.response_name(batch_id))
                        + json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        return {"batch_id": batch_id, "count": len(items), "path": str(path)}

    @app.post("/api/import-files")
    async def import_files():
        report = []
        for response in sorted(config.BATCH_DIR.glob("*.response.json")) if config.BATCH_DIR.exists() else []:
            batch = db.get_batch(conn, response.name.removesuffix(".response.json"))
            if not batch or batch["imported_at"]:
                continue
            text = response.read_text(encoding="utf-8")
            if batch["kind"] == "rate":
                result = claude_batch.parse_response(text, batch["book_ids"])
                done = save_ratings(result["ratings"])
                errors = result["errors"]
            else:
                done, errors = await import_market(text, batch["book_ids"])
            if done:
                db.mark_batch_imported(conn, batch["id"])
            report.append({"batch_id": batch["id"], "kind": batch["kind"], "imported": done, "errors": errors})
        return {"batches": report}

    async def import_market(text: str, ids: list[str]) -> tuple[int, list[str]]:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return 0, [f"Niepoprawny JSON: {exc.msg}"]
        done, errors = 0, []
        for book_id in ids:
            entry, book = data.get(book_id), db.get_book(conn, book_id)
            if not entry or not book or not isinstance(entry.get("videos"), list):
                errors.append(f"{book_id}: brak listy videos")
                continue
            data_market = dict(book.get("market") or {})
            data_market["youtube"] = market.youtube_from_raw(entry.get("query", ""), entry["videos"], "tubealfred")
            if "wiki" not in data_market:
                data_market = {**await market.analyze({**book, "market": data_market}, ""), **data_market}
            db.update_book(conn, book_id, market=data_market, status="analyzed")
            done += 1
        return done, errors

    # ── Rynek ───────────────────────────────────────────────────────────────
    @app.post("/api/market/{book_id}")
    async def analyze(book_id: str):
        book = db.get_book(conn, book_id)
        if not book:
            raise HTTPException(404, "Nie ma takiej książki")
        if not book.get("rating"):
            raise HTTPException(400, "Najpierw ocena Claude (potrzebne youtube_query).")
        try:
            result = await market.analyze(book, config.google_api_key())
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(502, f"Analiza rynku nie powiodła się: {exc}")
        db.update_book(conn, book_id, market=result, status="analyzed")
        return with_score(db.get_book(conn, book_id), db.get_settings(conn))

    # ── Eksport do DocOS ────────────────────────────────────────────────────
    @app.post("/api/export/docos")
    def export_docos(req: IdsRequest):
        chosen = [db.get_book(conn, i) for i in req.ids] if req.ids else \
            [b for b in db.list_books(conn) if b["flag"] == "picked"]
        topics = []
        for b in chosen:
            r = (b or {}).get("rating") or {}
            if not r:
                continue
            leads = list(r.get("research_leads") or [])
            leads.insert(0, f"Book: {b['title']}" + (f" — {b['author']}" if b.get("author") else "")
                         + (f" ({b['year']})" if b.get("year") else "") + f" [{b['url']}]")
            topics.append({"title": (r.get("video_title") or b["title"])[:60],
                           "subject": r.get("hook") or b["title"],
                           "central_question": r.get("central_question") or "",
                           "layers": r.get("layers") or [],
                           "research_leads": leads})
        if not topics:
            raise HTTPException(400, "Oznacz gwiazdką ocenione tematy, które chcesz wysłać do DocOS.")
        config.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = config.EXPORT_DIR / f"tematy_{time.strftime('%Y%m%d_%H%M%S')}.json"
        path.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"path": str(path), "count": len(topics), "topics": topics}

    app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
    return app
