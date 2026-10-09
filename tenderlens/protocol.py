"""Versioned request and response contracts shared by TenderLens neurons."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PROTOCOL_VERSION = "1"
MAX_CHANGES = 128
MAX_TEXT = 8_000


@dataclass(frozen=True)
class CompareTask:
    task_id: str
    source: str
    prior_publication: str
    current_publication: str
    reference: str

    def as_dict(self) -> dict[str, Any]:
        return {"protocol": PROTOCOL_VERSION, "task_id": self.task_id, "source": self.source,
                "prior_publication": self.prior_publication,
                "current_publication": self.current_publication, "reference": self.reference}


def validate_output(raw: Any, task: CompareTask, prior_hash: str, current_hash: str) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Validate untrusted miner output; reject unsafe size/shape before scoring."""
    errors: list[str] = []
    if not isinstance(raw, dict):
        return {}, ("response_not_object",)
    if raw.get("protocol") != PROTOCOL_VERSION:
        errors.append("protocol_mismatch")
    if raw.get("task_id") != task.task_id:
        errors.append("task_id_mismatch")
    if raw.get("prior_publication") != task.prior_publication or raw.get("current_publication") != task.current_publication:
        errors.append("source_pair_mismatch")
    if raw.get("reference") != task.reference:
        errors.append("source_reference_mismatch")
    if raw.get("prior_record_hash") != prior_hash or raw.get("current_record_hash") != current_hash:
        errors.append("source_hash_mismatch")
    changes = raw.get("changes")
    if not isinstance(changes, list):
        return {}, tuple(errors + ["changes_not_list"])
    if len(changes) > MAX_CHANGES:
        return {}, tuple(errors + ["too_many_changes"])
    clean: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, change in enumerate(changes):
        if not isinstance(change, dict):
            errors.append(f"change_{index}_not_object")
            continue
        field = change.get("field")
        if not isinstance(field, str) or not field or len(field) > 160:
            errors.append(f"change_{index}_invalid_field")
            continue
        if field in seen:
            errors.append(f"duplicate_field:{field}")
        seen.add(field)
        if "prior" not in change or "current" not in change:
            errors.append(f"change_{index}_missing_values")
            continue
        evidence = change.get("evidence")
        if not isinstance(evidence, dict) or set(evidence) != {"prior", "current"}:
            errors.append(f"change_{index}_invalid_evidence")
            continue
        if any(not isinstance(evidence[k], str) or len(evidence[k]) > MAX_TEXT for k in evidence):
            errors.append(f"change_{index}_evidence_too_large")
            continue
        clean.append({"field": field, "prior": change["prior"], "current": change["current"],
                      "evidence": evidence})
    return {"changes": clean}, tuple(errors)
