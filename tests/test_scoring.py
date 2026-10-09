"""Scoring invariants over the retained real TED notice chain."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tenderlens.protocol import CompareTask
from tenderlens.scoring import _same_typed_value, normalize_weights, score_response
from tenderlens.ted import make_reference_delta, task_record

ROOT = Path(__file__).resolve().parents[1]


class LiveSourceScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        response = json.loads((ROOT / "evidence" / "ted-explicit-amendment-chain.json").read_text(encoding="utf-8"))
        edge = response["pairs"][0]
        prior = response["versions"][edge["prior_index"]]
        current = response["versions"][edge["current_index"]]
        cls.prior_hash, cls.current_hash = prior["record_hash"], current["record_hash"]
        cls.prior, cls.current = task_record(prior), task_record(current)
        cls.task = CompareTask("b" * 64, "TED", prior["ND"], current["ND"], edge["reference"])
        cls.truth = make_reference_delta(cls.prior, cls.current)
        cls.perfect = {"protocol": "1", "task_id": cls.task.task_id,
                       "prior_publication": cls.task.prior_publication,
                       "current_publication": cls.task.current_publication,
                       "reference": cls.task.reference, "prior_record_hash": cls.prior_hash,
                       "current_record_hash": cls.current_hash, "changes": cls.truth}

    def test_reference_delta_from_real_ted_records_scores_perfectly(self):
        self.assertTrue(self.truth)
        self.assertEqual(score_response(self.task, self.perfect, self.prior_hash, self.current_hash,
                                        self.prior, self.current)["score"], 1.0)

    def test_changed_evidence_lowers_score_even_when_values_match(self):
        output = json.loads(json.dumps(self.perfect))
        output["changes"][0]["evidence"]["current"] = "unsupported value"
        self.assertLess(score_response(self.task, output, self.prior_hash, self.current_hash,
                                       self.prior, self.current)["score"], 1.0)

    def test_omitted_live_change_lowers_recall(self):
        output = {**self.perfect, "changes": self.truth[1:]}
        score = score_response(self.task, output, self.prior_hash, self.current_hash,
                               self.prior, self.current)
        self.assertLess(score["components"]["tuple_recall"], 1.0)

    def test_relative_weights_are_normalized_and_nonfinite_values_are_safe(self):
        weights = normalize_weights({2: 0.9, 7: 0.3, 9: float("nan"), 11: -2})
        self.assertAlmostEqual(sum(weights.values()), 1.0)
        self.assertGreater(weights[2], weights[7])
        self.assertEqual(weights[9], 0.0)

    def test_json_boolean_does_not_match_a_numeric_source_value(self):
        self.assertFalse(_same_typed_value(True, 1))
        self.assertFalse(_same_typed_value(1, 1.0))
        self.assertTrue(_same_typed_value(1, 1))


if __name__ == "__main__":
    unittest.main()
