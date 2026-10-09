"""Durable validator history invariants."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tenderlens.score_store import record_round


class ScoreHistoryTests(unittest.TestCase):
    def test_replayed_task_does_not_add_or_rewrite_score(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "history.sqlite"
            first = record_round(17, [{"uid": 3, "hotkey": "miner-a", "task_id": "task-a", "score": 0.8}], path=database)
            replay = record_round(17, [{"uid": 3, "hotkey": "miner-a", "task_id": "task-a", "score": 0.1}], path=database)

        self.assertEqual(first["miner-a"], {"uid": 3, "score": 0.8, "samples": 1})
        self.assertEqual(replay["miner-a"], first["miner-a"])


if __name__ == "__main__":
    unittest.main()
