"""Testy bez sieci: parsowanie odpowiedzi Claude, metryki YouTube, scoring i przepływ API."""
import datetime as dt
import json
import os
import tempfile
import unittest
from pathlib import Path

from bookscout import claude_batch, config, db, market, scoring

NOW = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)

BOOK = {
    "id": "ol:OL1W", "source": "openlibrary", "category": "espionage", "title": "The Vassall affair",
    "author": "Rebecca West", "year": 1963, "language": "eng", "subjects": ["Espionage"], "description": "",
    "toc": [], "isbn": [], "url": "https://openlibrary.org/works/OL1W", "availability": "none",
    "availability_detail": [],
}
RATING = {
    "id": "ol:OL1W", "interest": 78, "confidence": 70, "hook": "A clerk, a honey trap and a Cold War scandal.",
    "video_title": "The Spy Who Was Too Ordinary", "youtube_query": "John Vassall spy scandal",
    "wikipedia_article": "John Vassall", "central_question": "How did a junior clerk betray the Admiralty?",
    "interesting_points": ["a", "b", "c"], "layers": ["ludzka", "polityczna", "wywiad"],
    "research_leads": ["National Archives"], "difficulty": 6, "difficulty_reasons": "x", "visuals": 5,
    "research_hours": 12, "evergreen": 70, "series_potential": 60, "en_translation": None,
    "risk_flags": ["none"], "shorts_ideas": ["s1"],
}


def video(title, views, months_ago, length=900, subs=None):
    published = (NOW - dt.timedelta(days=30.44 * months_ago)).isoformat()
    return {"id": title[:5], "title": title, "channel": "c", "views": views, "published": published,
            "length_seconds": length, "subs": subs}


class ClaudeBatchTest(unittest.TestCase):
    def test_parses_fenced_json_and_clamps(self):
        raw = dict(RATING, interest=140, difficulty=0, risk_flags=["Legal", "bogus"])
        text = "Oto oceny:\n```json\n" + json.dumps([raw]) + "\n```\nPozdrawiam"
        result = claude_batch.parse_response(text, ["ol:OL1W"])
        self.assertEqual(result["errors"], [])
        rating = result["ratings"]["ol:OL1W"]
        self.assertEqual(rating["interest"], 100)
        self.assertEqual(rating["difficulty"], 1)
        self.assertEqual(rating["risk_flags"], ["legal"])

    def test_rejects_unknown_and_incomplete(self):
        items = [dict(RATING, id="ol:OTHER"), {"id": "ol:OL1W", "interest": 50}]
        result = claude_batch.parse_response(json.dumps(items), ["ol:OL1W", "ol:OL2W"])
        self.assertEqual(result["ratings"], {})
        self.assertEqual(len(result["errors"]), 2)
        self.assertTrue(any("1 książek" in w for w in result["warnings"]))

    def test_invalid_json_is_reported(self):
        result = claude_batch.parse_response("[{\"id\": ", ["ol:OL1W"])
        self.assertTrue(result["errors"])

    def test_prompt_contains_books_and_schema(self):
        prompt = claude_batch.build_prompt([BOOK], config.DEFAULT_SETTINGS)
        self.assertIn("The Vassall affair", prompt)
        self.assertIn("youtube_query", prompt)
        self.assertIn("Brak wersji cyfrowej", prompt)


class MarketTest(unittest.TestCase):
    def test_iso_duration(self):
        self.assertEqual(market.iso_duration_seconds("PT1H2M3S"), 3723)
        self.assertEqual(market.iso_duration_seconds("PT45S"), 45)
        self.assertIsNone(market.iso_duration_seconds("bad"))

    def test_metrics_skip_shorts_and_irrelevant(self):
        videos = [
            video("John Vassall spy scandal explained", 250_000, 6, subs=500_000),
            video("The Vassall spy case", 40_000, 30, subs=20_000),
            video("Vassall: the Admiralty spy", 120_000, 40, subs=300_000),
            video("Cooking pasta at home", 9_000_000, 3),
            video("Vassall spy short", 1_000_000, 2, length=50),
        ]
        m = market.video_metrics(videos, "John Vassall spy scandal", now=NOW)
        self.assertEqual(m["long_form"], 4)
        self.assertEqual(m["relevant"], 3)
        self.assertEqual(m["strong"], 2)
        self.assertEqual(m["strong_recent"], 1)
        self.assertEqual(m["median_views"], 120_000)
        self.assertIsNotNone(m["outlier_ratio"])


class ScoringTest(unittest.TestCase):
    def test_rating_only_gives_partial_score(self):
        s = scoring.compute({**BOOK, "rating": RATING}, config.DEFAULT_SETTINGS)
        self.assertIsNotNone(s["score"])
        self.assertEqual(s["completeness"], "3/6")
        self.assertIsNone(s["views"])
        self.assertEqual(s["exclusivity"], 78.0)
        self.assertGreater(s["cost"]["usd"], 0)

    def test_full_market_data(self):
        yt = {"query": "q", "results": 20, "long_form": 18, "relevant": 6, "strong": 1, "strong_recent": 0,
              "median_views": 60_000, "top_views": 300_000, "median_first_year": 30_000, "median_subs": 80_000,
              "outlier_ratio": 0.4}
        book = {**BOOK, "rating": RATING, "market": {"wiki": {"article": "John Vassall", "monthly_avg": 9000},
                                                       "youtube": yt}}
        s = scoring.compute(book, {**config.DEFAULT_SETTINGS, "channel_subs": 20_000})
        self.assertEqual(s["completeness"], "6/6")
        self.assertGreater(s["views"], 0)
        self.assertLess(s["views_low"], s["views"])
        self.assertGreater(s["opportunity_ratio"], 1)
        self.assertIn(s["verdict"], {"Rób to", "Obiecujące", "Może", "Odpuść"})
        self.assertEqual(s["revenue_usd"], round(s["views"] / 1000 * 5.0))

    def test_unmonetized_channel_earns_nothing(self):
        book = {**BOOK, "rating": RATING, "market": {"wiki": {"article": "X", "monthly_avg": 5000}}}
        s = scoring.compute(book, {**config.DEFAULT_SETTINGS, "monetized": False})
        self.assertEqual(s["revenue_usd"], 0)
        self.assertEqual(s["roi"], 0)

    def test_no_rating_no_score(self):
        self.assertIsNone(scoring.compute(BOOK, config.DEFAULT_SETTINGS)["score"])


class ApiFlowTest(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from bookscout.app import create_app
        self.tmp = tempfile.TemporaryDirectory()
        tmp = Path(self.tmp.name)
        self.old = (config.BATCH_DIR, config.EXPORT_DIR)
        config.BATCH_DIR, config.EXPORT_DIR = tmp / "batches", tmp / "exports"
        self.db_path = tmp / "t.db"
        seed = db.connect(self.db_path)
        db.insert_books(seed, [BOOK])
        seed.close()
        self.client = TestClient(create_app(self.db_path))

    def tearDown(self):
        config.BATCH_DIR, config.EXPORT_DIR = self.old
        self.tmp.cleanup()

    def test_prompt_import_flag_and_docos_export(self):
        res = self.client.post("/api/claude/prompt", json={"count": 5}).json()
        self.assertEqual(res["ids"], ["ol:OL1W"])
        imp = self.client.post("/api/claude/import", json={"text": json.dumps([RATING]),
                                                           "batch_id": res["batch_id"]}).json()
        self.assertEqual(imp["imported"], 1)
        books = self.client.get("/api/books").json()
        self.assertEqual(books[0]["status"], "rated")
        self.assertIsNotNone(books[0]["scoring"]["score"])
        self.client.post("/api/books/ol:OL1W/flag", json={"flag": "picked"})
        export = self.client.post("/api/export/docos", json={}).json()
        self.assertEqual(export["count"], 1)
        topic = export["topics"][0]
        self.assertLessEqual(len(topic["title"]), 60)
        self.assertGreaterEqual(len(topic["layers"]), 3)
        self.assertTrue(topic["research_leads"][0].startswith("Book: The Vassall affair"))

    def test_file_mode_round_trip(self):
        res = self.client.post("/api/claude/export-file", json={"count": 5}).json()
        self.assertTrue(os.path.exists(res["path"]))
        response = config.BATCH_DIR / claude_batch.response_name(res["batch_id"])
        response.write_text(json.dumps([RATING]), encoding="utf-8")
        report = self.client.post("/api/import-files").json()["batches"]
        self.assertEqual(report[0]["imported"], 1)
        self.assertEqual(self.client.post("/api/import-files").json()["batches"], [])

    def test_settings_recompute(self):
        saved = self.client.put("/api/settings", json={"channel_subs": "5000", "monetized": False}).json()
        self.assertEqual(saved["channel_subs"], 5000)
        self.assertFalse(saved["monetized"])


if __name__ == "__main__":
    unittest.main()
