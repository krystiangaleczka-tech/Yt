import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from studio_workers.jobs import Jobs


class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name); self.jobs = Jobs(self.root)

    def tearDown(self):
        self.jobs.close(); self.temp.cleanup()

    def wait(self, job_id):
        for _ in range(200):
            value = self.jobs.get(job_id)
            if value["status"] not in ("RUNNING", "QUEUED", "CANCEL_REQUESTED"):
                return value
            time.sleep(.01)
        self.fail("Job did not finish")

    def test_success_persists_input_revision_and_output(self):
        job = self.jobs.submit("p", 8, "render", lambda jid, progress, cancel: {"revision": 8, "filename": "file.mp4"})
        result = self.wait(job["id"])
        self.assertEqual(result["status"], "SUCCEEDED")
        self.assertEqual(result["result"]["revision"], 8)
        self.assertEqual(result["revision"], 8)

    def test_worker_error_is_not_success(self):
        def task(*args):
            raise ValueError("Renderer rejected the file")
        job = self.jobs.submit("p", 3, "render", task)
        result = self.wait(job["id"])
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("rejected", result["message"])
        self.assertIsNone(result["result"])

    def test_cancellation_has_terminal_state(self):
        def task(jid, progress, cancel):
            cancel.wait(2)
            if cancel.is_set(): raise InterruptedError()
            return {}
        job = self.jobs.submit("p", 4, "render", task)
        self.jobs.cancel(job["id"])
        self.assertEqual(self.wait(job["id"])["status"], "CANCELLED")

    def test_restart_marks_unfinished_jobs_interrupted(self):
        with self.jobs.db() as db:
            db.execute("INSERT INTO jobs VALUES (?,?)", ("lost", json.dumps({"id": "lost", "status": "RUNNING", "revision": 9})))
        reopened = Jobs(self.root)
        try:
            self.assertEqual(reopened.get("lost")["status"], "INTERRUPTED")
        finally:
            reopened.close()

    def test_late_cancel_request_cannot_overwrite_terminal_status(self):
        job = self.jobs.submit("p", 1, "render", lambda *args: {})
        result = self.wait(job["id"])
        self.jobs.update(job["id"], status="CANCEL_REQUESTED", message="Late request")
        self.assertEqual(self.jobs.get(job["id"])["status"], result["status"])


if __name__ == "__main__":
    unittest.main()
