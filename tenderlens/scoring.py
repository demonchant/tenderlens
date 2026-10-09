"""Deterministic score contract for actual TED notice-pair miner responses."""

from __future__ import annotations

import math

from .protocol import CompareTask, validate_output
from .ted import make_reference_delta, source_text


def _same_typed_value(left: object, right: object) -> bool:
    """Keep JSON booleans and numbers distinct despite Python's bool/int inheritance."""
    return type(left) is type(right) and left == right


def score_response(task: CompareTask, raw: object, prior_hash: str, current_hash: str,
                   prior: dict, current: dict) -> dict[str, object]:
    clean, errors = validate_output(raw, task, prior_hash, current_hash)
    expected = {row["field"]: row for row in make_reference_delta(prior, current)}
    if errors:
        clean = {"changes": []}
    actual = {row["field"]: row for row in clean.get("changes", [])}
    tp = 0
    grounded_tp = 0
    for field, row in actual.items():
        gold = expected.get(field)
        if not gold or not _same_typed_value(row["prior"], gold["prior"]) \
                or not _same_typed_value(row["current"], gold["current"]):
            continue
        tp += 1
        evidence = row["evidence"]
        prior_ok = evidence["prior"] == source_text(gold["prior"])
        current_ok = evidence["current"] == source_text(gold["current"])
        if prior_ok and current_ok:
            grounded_tp += 1
    predicted, relevant = len(actual), len(expected)
    precision = tp / predicted if predicted else (1.0 if not relevant else 0.0)
    recall = tp / relevant if relevant else (1.0 if not predicted else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    evidence_precision = grounded_tp / predicted if predicted else (1.0 if not relevant else 0.0)
    validity = 0.0 if errors else 1.0
    score = 0.70 * f1 + 0.25 * evidence_precision + 0.05 * validity
    return {"task_id": task.task_id, "score": round(score, 8), "expected_changes": relevant,
            "predicted_changes": predicted, "true_positive": tp,
            "components": {"tuple_precision": round(precision, 8), "tuple_recall": round(recall, 8),
                           "tuple_f1": round(f1, 8), "evidence_precision": round(evidence_precision, 8),
                           "protocol_validity": validity}, "errors": list(errors)}


def normalize_weights(scores: dict[int, float]) -> dict[int, float]:
    finite = {uid: max(0.0, float(value)) if math.isfinite(value) else 0.0 for uid, value in scores.items()}
    total = sum(finite.values())
    return {uid: (value / total if total else 0.0) for uid, value in finite.items()}
