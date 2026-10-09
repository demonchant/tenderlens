"""Protocol invariants; all procurement values come from captured live TED records."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tenderlens.protocol import CompareTask, validate_output
from tenderlens.ted import make_reference_delta, task_record


ROOT = Path(__file__).resolve().parents[1]


class LiveRecordProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        response = json.loads((ROOT / "evidence" / "ted-explicit-amendment-chain.json").read_text(encoding="utf-8"))
        edge = response["pairs"][0]
        cls.prior = response["versions"][edge["prior_index"]]
        cls.current = response["versions"][edge["current_index"]]
        cls.task = CompareTask("a" * 64, "TED", cls.prior["ND"], cls.current["ND"], edge["reference"])
        cls.prior_values, cls.current_values = task_record(cls.prior), task_record(cls.current)
        cls.pair_reference = edge["reference"]

    def test_delta_is_derived_from_the_captured_real_source_pair(self):
        delta = make_reference_delta(self.prior_values, self.current_values)
        self.assertTrue(delta)
        self.assertEqual(self.current["change-notice-version-identifier"], self.pair_reference)
        self.assertTrue(all(row["field"] and set(row["evidence"]) == {"prior", "current"} for row in delta))
        self.assertTrue(all(row["evidence"][side] for row in delta for side in ("prior", "current")))

    def test_protocol_rejects_task_identity_mismatch(self):
        valid = {"protocol": "1", "task_id": "stale", "prior_publication": self.task.prior_publication,
                 "current_publication": self.task.current_publication, "reference": self.task.reference,
                 "prior_record_hash": self.prior["record_hash"], "current_record_hash": self.current["record_hash"],
                 "changes": []}
        clean, errors = validate_output(valid, self.task, self.prior["record_hash"], self.current["record_hash"])
        self.assertEqual(clean, {"changes": []})
        self.assertIn("task_id_mismatch", errors)

    def test_duplicate_change_paths_are_rejected(self):
        item = {"field": "notice-version", "prior": 1, "current": 2,
                "evidence": {"prior": "1", "current": "2"}}
        raw = {"protocol": "1", "task_id": self.task.task_id,
               "prior_publication": self.task.prior_publication,
               "current_publication": self.task.current_publication, "reference": self.task.reference,
               "prior_record_hash": self.prior["record_hash"], "current_record_hash": self.current["record_hash"],
               "changes": [item, item]}
        _, errors = validate_output(raw, self.task, self.prior["record_hash"], self.current["record_hash"])
        self.assertIn("duplicate_field:notice-version", errors)

    def test_unknown_task_output_shape_is_not_accepted(self):
        raw = {"protocol": "1", "task_id": self.task.task_id,
               "prior_publication": self.task.prior_publication,
               "current_publication": self.task.current_publication, "reference": self.task.reference,
               "prior_record_hash": self.prior["record_hash"], "current_record_hash": self.current["record_hash"],
               "changes": "no changes"}
        _, errors = validate_output(raw, self.task, self.prior["record_hash"], self.current["record_hash"])
        self.assertIn("changes_not_list", errors)


if __name__ == "__main__":
    unittest.main()
