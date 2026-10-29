import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from studio_connectors.sources import Connectors
from studio_core.assistant import complete


class ClaudeResponseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.connectors = Connectors(Path(self.temp.name))

    def response(self, code, stdout):
        with patch("studio_core.assistant.shutil.which", return_value="/usr/bin/claude"), \
             patch("studio_core.assistant.subprocess.run", return_value=subprocess.CompletedProcess([], code, stdout, "")):
            return complete(self.connectors, "Test")

    def test_usage_limit_is_reported_instead_of_media_error(self):
        with self.assertRaisesRegex(ValueError, "Osiągnięto limit Claude.*resets Oct 28"):
            self.response(1, json.dumps({"is_error": True, "api_error": "usage_limit_reached", "result": "Weekly limit; resets Oct 28"}))

    def test_failed_cli_without_json_has_actionable_message(self):
        with self.assertRaisesRegex(ValueError, "Claude CLI.*Sprawdź logowanie"):
            self.response(1, "Connection failed")

    def test_successful_cli_keeps_model_response(self):
        self.assertEqual(self.response(0, json.dumps({"result": '{"operations": []}'})), '{"operations": []}')


if __name__ == "__main__":
    unittest.main()
