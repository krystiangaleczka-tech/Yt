import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from studio_api.app import create_app
from studio_api.flow import flow_prompt
from studio_core import sketches
from studio_core.models import Project
from studio_core.production_flow import validated_flow

H = {"X-Docos-Request": "1"}
REPO = Path(__file__).resolve().parents[1]


def shot(nr, **extra):
    return {"id": f"szkic_a-{nr:03d}", "nr": nr, "key": f"k{nr}", "kadr": "", "seconds": 5,
            "description": f"Opis {nr}", "line": f"Kwestia {nr}", "mark": "", "assetId": ""} | extra


def write_variant(folder: Path, wariant: str, frames: dict[str, tuple[int, int, int] | None], film="test-film",
                  extra_shots=()):
    """Katalog wariantu: frames = {plik: kolor} (None = plik nie istnieje)."""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "klatki").mkdir(exist_ok=True)
    shots = []
    for i, (name, colour) in enumerate(frames.items(), 1):
        if colour is not None:
            Image.new("RGB", (320, 180), colour).save(folder / name)
        shots.append({"nr": i, "klucz": f"{wariant}_{i}", "sekundy": 4 + i, "opis": f"Ujęcie {i}",
                      "kwestia": f"Line {i}", "klatka": name, "kadr": "plan ogólny"})
    shots.append({"nr": "ujęcie 9", "klucz": "karta", "sekundy": 3, "opis": "Bez obrazu", "kwestia": "", "klatka": "",
                  "znacznik": "HOOK 1"})
    shots += list(extra_shots)
    (folder / "szkic.json").write_text(json.dumps({
        "film": film, "wariant": wariant, "tytul": f"Podejście {wariant}", "scenariusz": f"Scenariusz {wariant}",
        "ujecia": shots}, ensure_ascii=False), encoding="utf-8")


class SketchModelTests(unittest.TestCase):
    def test_duplicate_ids_and_limits_are_rejected(self):
        with self.assertRaises(ValueError):
            validated_flow({"sketches": {"variants": [{"id": "a"}, {"id": "a"}]}})
        with self.assertRaises(ValueError):
            validated_flow({"sketches": {"variants": [{"id": "a", "shots": [shot(1), shot(1)]}]}})
        with self.assertRaises(ValueError):
            validated_flow({"sketches": {"variants": [{"id": f"v{i}"} for i in range(13)]}})
        with self.assertRaises(ValueError):
            validated_flow({"sketches": {"playSeconds": 2}})
        validated_flow({"sketches": {"variants": [{"id": "a", "shots": [shot(1), shot(2)]}], "approved": None}})

    def test_content_ignores_ids_and_source(self):
        a = {"id": "x", "title": "T", "scenario": "S", "shots": [shot(1)], "source": {"film": "f"}}
        b = {"id": "y", "title": "T", "scenario": "S", "shots": [shot(1, id="other")], "source": {}}
        self.assertEqual(sketches.signature(a), sketches.signature(b))
        self.assertNotEqual(sketches.signature(a), sketches.signature(b | {"title": "U"}))


class SketchApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {"DOCOS_SKETCH_ROOTS": str(self.root / "zrodla")})
        self.env.start()
        self.app = create_app(self.root / "home", seed_demo=False)
        self.store = self.app.state.store
        self.client = TestClient(self.app)
        self.project = self.store.create(Project(title="Syn słońca", production_mode="animation_2d",
                                                 legacy={"production_flow": {"factual": False, "acts": []}}))
        self.pid = self.project.id

    def tearDown(self):
        self.client.close()
        self.app.state.jobs.close()
        self.env.stop()
        self.tmp.cleanup()

    def url(self, suffix=""):
        return f"/api/projects/{self.pid}/sketches{suffix}"

    def revision(self):
        return self.store.get(self.pid).revision

    def put_variants(self, variants, play=25):
        return self.client.put(self.url(), headers=H, json={
            "expected_revision": self.revision(), "sketches": {"variants": variants, "playSeconds": play}})

    def flow(self):
        return self.store.get(self.pid).legacy["production_flow"]

    def test_default_three_empty_variants(self):
        r = self.client.get(self.url())
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual([v["id"] for v in data["sketches"]["variants"]], ["szkic_a", "szkic_b", "szkic_c"])
        self.assertEqual([v["label"] for v in data["variants"]], ["Wariant A", "Wariant B", "Wariant C"])
        self.assertEqual(data["state"], "none")
        self.assertEqual(data["sketches"]["playSeconds"], 25)

    def test_put_never_overwrites_approval(self):
        variant = {"id": "szkic_a", "title": "Hook", "scenario": "Tekst", "shots": [shot(1)], "source": {}}
        self.assertEqual(self.put_variants([variant]).status_code, 200)
        self.assertEqual(self.client.post(self.url("/approve"), headers=H, json={"variant_id": "szkic_a"}).status_code, 200)
        forged = {"variants": [variant], "approved": {"variantId": "szkic_x", "snapshot": {}}}
        r = self.client.put(self.url(), headers=H, json={"expected_revision": self.revision(), "sketches": forged})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(self.flow()["sketches"]["approved"]["variantId"], "szkic_a")

    def test_put_rejects_stale_revision(self):
        r = self.client.put(self.url(), headers=H, json={"expected_revision": self.revision() - 1,
                                                          "sketches": {"variants": []}})
        self.assertEqual(r.status_code, 409)

    def test_approve_snapshot_log_and_stale_check(self):
        empty = self.client.post(self.url("/approve"), headers=H, json={"variant_id": "szkic_b"})
        self.assertEqual(empty.status_code, 422, "pusty wariant nie może być zatwierdzony")
        variants = [{"id": "szkic_a", "title": "Hak z koroną", "scenario": "2019…", "shots": [shot(1), shot(2)], "source": {}},
                    {"id": "szkic_b", "title": "", "scenario": "", "shots": [], "source": {}}]
        self.put_variants(variants)
        check = self.client.post(f"/api/projects/{self.pid}/continuity/check", headers=H).json()
        self.assertTrue(any(i["rule"] == "szkic" and i["severity"] == 1 for i in check["issues"]))
        r = self.client.post(self.url("/approve"), headers=H, json={"variant_id": "szkic_a", "note": "Ten"})
        self.assertEqual(r.status_code, 200, r.text)
        approved = self.flow()["sketches"]["approved"]
        self.assertEqual(approved["title"], "Hak z koroną")
        self.assertEqual(approved["snapshot"], sketches.content(variants[0]))
        self.assertEqual(approved["signature"], sketches.signature(variants[0]))
        entry = self.flow()["log"][-1]
        self.assertEqual(entry["kind"], "szkic")
        self.assertIn("Zatwierdzony szkic ujęć: Hak z koroną", entry["summary"])
        self.assertIn("Ujęć: 2, długość filmu 0:10", entry["details"])
        self.assertEqual(self.client.get(self.url()).json()["state"], "current")
        check = self.client.post(f"/api/projects/{self.pid}/continuity/check", headers=H).json()
        self.assertFalse([i for i in check["issues"] if i["rule"] == "szkic"])

        variants[0]["shots"][1]["seconds"] = 9
        self.put_variants(variants)
        self.assertEqual(self.client.get(self.url()).json()["state"], "stale")
        check = self.client.post(f"/api/projects/{self.pid}/continuity/check", headers=H).json()
        found = [i for i in check["issues"] if i["rule"] == "szkic"]
        self.assertEqual([i["severity"] for i in found], [2])
        self.assertEqual(check["totals"]["2"], sum(1 for i in check["issues"] if i["severity"] == 2))

        self.put_variants(variants[1:])
        self.assertEqual(self.client.get(self.url()).json()["state"], "missing")
        r = self.client.post(self.url("/withdraw"), headers=H, json={})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIsNone(self.flow()["sketches"]["approved"])
        self.assertIn("Cofnięte zatwierdzenie", self.flow()["log"][-1]["summary"])

    def test_approval_survives_whole_flow_save_from_browser(self):
        """Regresja: JS zapisuje 6.0 jako 6, więc migawka i wariant po zapisie całego planu mają liczby całkowite."""
        folder = self.root / "zrodla" / "film" / "szkice" / "a"
        write_variant(folder, "a", {"klatki/001.png": (9, 9, 9)})
        self.client.post(self.url("/import"), headers=H, json={"path": str(folder)})
        self.assertEqual(self.client.post(self.url("/approve"), headers=H, json={"variant_id": "szkic_a"}).status_code, 200)

        def as_js(value):
            if isinstance(value, float) and value.is_integer():
                return int(value)
            if isinstance(value, dict):
                return {k: as_js(v) for k, v in value.items()}
            if isinstance(value, list):
                return [as_js(v) for v in value]
            return value

        flow = as_js(self.flow())
        flow["master"] = {"id": "master", "variants": [{"id": "m1", "title": "T", "description": "D"}], "selected": "m1"}
        r = self.client.put(f"/api/projects/{self.pid}/flow", headers=H,
                            json={"expected_revision": self.revision(), "flow": flow})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(self.client.get(self.url()).json()["state"], "current")
        check = self.client.post(f"/api/projects/{self.pid}/continuity/check", headers=H).json()
        self.assertFalse([i for i in check["issues"] if i["rule"] == "szkic"])

    def test_flow_prompt_carries_approved_sketch(self):
        self.put_variants([{"id": "szkic_a", "title": "Dwa hooki", "scenario": "HOOK 1: miecz",
                            "shots": [shot(1, mark="HOOK 1")], "source": {}}])
        self.client.post(self.url("/approve"), headers=H, json={"variant_id": "szkic_a"})
        prompt = flow_prompt(self.store.get(self.pid), "master")
        self.assertIn("trzymaj się jego struktury", prompt)
        context = json.loads(prompt.split("KONTEKST:\n", 1)[1])
        self.assertEqual(context["approved_sketch"]["title"], "Dwa hooki")
        self.assertEqual(context["approved_sketch"]["shots"][0]["mark"], "HOOK 1")
        self.assertFalse(context["approved_sketch"]["stale"])

    def test_import_variant_with_frames_cards_and_missing_file(self):
        folder = self.root / "zrodla" / "docs" / "filmy" / "test-film" / "szkice" / "a"
        write_variant(folder, "a", {"klatki/001.png": (200, 30, 30), "klatki/002.png": (30, 200, 30),
                                    "klatki/brak.png": None})
        before = self.revision()
        r = self.client.post(self.url("/import"), headers=H, json={"path": str(folder)})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["project"]["revision"], before + 1, "import to jedna zmiana projektu")
        self.assertEqual(len(data["warnings"]), 1)
        self.assertIn("brak pliku", data["warnings"][0])
        variant = self.flow()["sketches"]["variants"][0]
        self.assertEqual(variant["id"], "szkic_a", "pierwszy pusty wariant")
        self.assertEqual(variant["title"], "Podejście a")
        self.assertEqual([s["nr"] for s in variant["shots"]], [1, 2, 3, 9])
        self.assertEqual([s["id"] for s in variant["shots"]][:2], ["szkic_a-001", "szkic_a-002"])
        self.assertEqual(variant["shots"][3]["mark"], "HOOK 1")
        self.assertEqual(variant["source"]["frames"], 2)
        self.assertEqual(variant["source"]["missing"], 1)
        with_frames = [s["assetId"] for s in variant["shots"] if s["assetId"]]
        self.assertEqual(len(with_frames), 2)
        project = self.store.get(self.pid)
        assets = {a.id: a for a in project.assets}
        media = self.store.folder(self.pid) / "media"
        for asset_id in with_frames:
            asset = assets[asset_id]
            self.assertEqual(asset.mime, "image/jpeg")
            self.assertEqual(asset.provenance["kind"], "sketch-frame")
            import hashlib
            self.assertEqual(hashlib.sha256((media / asset.filename).read_bytes()).hexdigest(), asset.sha256)
            self.assertTrue((media / asset.thumbnail).is_file())
            self.assertEqual(self.client.get(f"/api/projects/{self.pid}/media/{asset_id}?thumbnail=true").status_code, 200)
        self.assertEqual(self.flow()["log"][-1]["kind"], "szkic")

        # Ponowny import: te same materiały, ten sam wariant, nowa treść.
        data = json.loads((folder / "szkic.json").read_text())
        data["tytul"] = "Podejście a, druga wersja"
        (folder / "szkic.json").write_text(json.dumps(data, ensure_ascii=False))
        r = self.client.post(self.url("/import"), headers=H, json={"path": str(folder)})
        self.assertEqual(r.status_code, 200, r.text)
        project = self.store.get(self.pid)
        self.assertEqual(len(project.assets), 2)
        variants = self.flow()["sketches"]["variants"]
        self.assertEqual(variants[0]["title"], "Podejście a, druga wersja")
        self.assertEqual(sum(1 for v in variants if not sketches.is_empty(v)), 1)

    def test_import_szkice_folder_fills_empty_variants_then_appends(self):
        base = self.root / "zrodla" / "docs" / "filmy" / "test-film" / "szkice"
        write_variant(base / "a", "a", {"klatki/001.png": (10, 10, 10)})
        write_variant(base / "b", "b", {})
        r = self.client.post(self.url("/import"), headers=H, json={"path": str(base)})
        self.assertEqual(r.status_code, 200, r.text)
        variants = self.flow()["sketches"]["variants"]
        self.assertEqual([(v["id"], v["source"].get("wariant")) for v in variants],
                         [("szkic_a", "a"), ("szkic_b", "b"), ("szkic_c", None)])
        write_variant(base / "c", "c", {})
        write_variant(base / "d", "d", {})
        self.client.post(self.url("/import"), headers=H, json={"path": str(base)})
        ids = [v["id"] for v in self.flow()["sketches"]["variants"]]
        self.assertEqual(ids, ["szkic_a", "szkic_b", "szkic_c", "szkic_d"])

    def test_import_outside_roots_is_refused(self):
        outside = Path(tempfile.mkdtemp())
        try:
            write_variant(outside / "a", "a", {})
            r = self.client.post(self.url("/import"), headers=H, json={"path": str(outside / "a")})
            self.assertEqual(r.status_code, 422)
            self.assertIn("tylko z katalogów projektu", r.json()["detail"])
            escape = str(self.root / "zrodla" / ".." / ".." / outside.name / "a")
            self.assertEqual(self.client.post(self.url("/import"), headers=H, json={"path": escape}).status_code, 422)
        finally:
            import shutil
            shutil.rmtree(outside)

    def test_frame_path_cannot_leave_variant_folder(self):
        base = self.root / "zrodla" / "film" / "szkice"
        (self.root / "zrodla").mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (64, 36), (0, 0, 0)).save(self.root / "zrodla" / "tajny.png")
        write_variant(base / "a", "a", {}, extra_shots=[{"nr": 10, "opis": "ucieczka", "klatka": "../../../tajny.png"},
                                                       {"nr": 11, "opis": "zły typ", "klatka": "notatka.txt"}])
        r = self.client.post(self.url("/import"), headers=H, json={"path": str(base / "a")})
        self.assertEqual(r.status_code, 200, r.text)
        warnings = r.json()["warnings"]
        self.assertTrue(any("poza katalogiem wariantu" in w for w in warnings), warnings)
        self.assertTrue(any("PNG, JPG albo WEBP" in w for w in warnings), warnings)
        self.assertEqual(self.store.get(self.pid).assets, [])

    def test_broken_json_is_a_clear_error(self):
        folder = self.root / "zrodla" / "film" / "szkice" / "zly"
        folder.mkdir(parents=True)
        (folder / "szkic.json").write_text('{"ujecia": [{"sekundy": -1}]}')
        r = self.client.post(self.url("/import"), headers=H, json={"path": str(folder)})
        self.assertEqual(r.status_code, 422)
        self.assertIn("sekundy", r.json()["detail"])
        self.assertEqual(self.revision(), self.project.revision)

    def test_sources_lists_sketch_folders(self):
        base = self.root / "zrodla" / "docs" / "filmy" / "test-film" / "szkice"
        write_variant(base / "a", "a", {"klatki/001.png": (1, 2, 3)})
        (base / "zly").mkdir(parents=True)
        (base / "zly" / "szkic.json").write_text("nie json")
        r = self.client.get("/api/sketches/sources")
        self.assertEqual(r.status_code, 200, r.text)
        found = {Path(s["path"]).name: s for s in r.json()["sources"] if "test-film" in s["path"]}
        self.assertEqual(found["a"]["shots"], 2)
        self.assertEqual(found["a"]["frames"], 1)
        self.assertEqual(found["a"]["tytul"], "Podejście a")
        self.assertIn("error", found["zly"])

    def test_cli_imports_without_root_limit(self):
        folder = Path(tempfile.mkdtemp())
        try:
            write_variant(folder / "x", "x", {"klatki/001.png": (5, 5, 5)})
            from studio_core import cli
            out = io.StringIO()
            argv = ["cli", "--home", str(self.root / "home"), "szkice", self.pid, str(folder / "x")]
            with patch.object(sys, "argv", argv), redirect_stdout(out):
                cli.main()
            result = json.loads(out.getvalue())
            self.assertEqual(result["imported"][0]["variantId"], "szkic_a")
            self.assertEqual(result["imported"][0]["frames"], 1)
            self.assertEqual(self.flow()["sketches"]["variants"][0]["source"]["wariant"], "x")
        finally:
            import shutil
            shutil.rmtree(folder)


if __name__ == "__main__":
    unittest.main()
