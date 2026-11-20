import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from retry_eval import Attempt, compare_retries


class RetryEvaluationTests(unittest.TestCase):
    def test_retries_receive_same_feedback_and_one_attempt_each(self):
        calls = []

        def attempt(feedback, reflection):
            calls.append((feedback, reflection))
            return Attempt("read", None, "file missing", 1)

        compare_retries(attempt, lambda feedback: "check the file path", lambda _: False)

        self.assertEqual(calls, [
            (None, None),
            ("file missing", None),
            ("file missing", "check the file path"),
        ])

    def test_successful_first_attempt_cannot_seed_a_retry_comparison(self):
        with self.assertRaisesRegex(ValueError, "failed first attempt"):
            compare_retries(
                lambda *_: Attempt("read", "answer", None, 1),
                lambda _: self.fail("Reflection ran without a failure."),
                lambda _: True,
            )

    def test_cli_writes_machine_and_human_readable_results(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "artifacts"
            subprocess.run(
                [sys.executable, str(Path(__file__).with_name("retry_eval.py")),
                 "--output-dir", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            records = [
                json.loads(line)
                for line in (output / "retry_results.jsonl").read_text().splitlines()
            ]
            summary = (output / "summary.md").read_text()
            self.assertEqual([row["success"] for row in records], [False, False, True])
            self.assertIn("Deterministic fixture with no live model", summary)


if __name__ == "__main__":
    unittest.main()
