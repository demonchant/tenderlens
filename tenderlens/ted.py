"""Live, bounded TED Search API client and deterministic structured-delta reference."""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

TED_ENDPOINT = "https://api.ted.europa.eu/v3/notices/search"
FIELDS = [
    "ND", "PD", "notice-identifier", "notice-version", "notice-type", "notice-title",
    "change-description", "change-notice-version-identifier", "change-reason-code",
    "change-reason-description", "deadline-receipt-tender-date-lot",
    "deadline-receipt-tender-time-lot", "estimated-value-proc", "estimated-value-cur-proc",
    "estimated-value-lot", "estimated-value-cur-lot", "organisation-name-buyer",
    "selection-criterion-description-lot", "procedure-type",
]
TASK_FIELDS = (
    "notice-type", "notice-title", "change-description", "change-notice-version-identifier",
    "change-reason-code", "change-reason-description", "deadline-receipt-tender-date-lot",
    "deadline-receipt-tender-time-lot", "estimated-value-proc", "estimated-value-cur-proc",
    "estimated-value-lot", "estimated-value-cur-lot", "organisation-name-buyer",
    "selection-criterion-description-lot", "procedure-type",
)
PUBLICATION_RE = re.compile(r"^[0-9]{1,8}-20[0-9]{2}$")
NOTICE_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


class TedError(Exception):
    """A live TED request failed or returned data outside the expected contract."""


def _search(query: str, limit: int) -> dict[str, Any]:
    body = json.dumps({"query": query, "fields": FIELDS, "limit": limit,
                       "page": 1, "scope": "ALL"}, separators=(",", ":")).encode()
    request = urllib.request.Request(TED_ENDPOINT, data=body, headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": "TenderLens/0.1 (public procurement version comparison)",
    }, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                raise TedError(f"TED returned HTTP {response.status}")
            payload = response.read(3_000_001)
    except urllib.error.HTTPError as exc:
        raise TedError(f"TED returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise TedError("TED Search API is temporarily unreachable") from exc
    if len(payload) > 3_000_000:
        raise TedError("TED response exceeded the 3 MB response limit")
    try:
        data = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TedError("TED response was not valid JSON") from exc
    if not isinstance(data, dict) or not isinstance(data.get("notices"), list):
        raise TedError("TED response did not match the Search API contract")
    return data


def versions_for_publication(publication: str) -> dict[str, Any]:
    if not PUBLICATION_RE.fullmatch(publication):
        raise ValueError("Enter a TED publication number such as 123456-2026")
    data = _search(f"ND = {publication}", 10)
    records = [r for r in data["notices"] if isinstance(r, dict)]
    if not records:
        return {"source": "TED", "retrieved_at": _now(), "publication": publication,
                "versions": [], "pairs": [], "total": data.get("totalNoticeCount", 0),
                "pair_available": False}
    seed = records[0]
    started = time.monotonic()
    chain: dict[str, dict[str, Any]] = {}
    pending: list[dict[str, Any]] = []

    # A submitted change notice points backward via BT-758. Resolve that exact
    # reference; same procedure IDs/titles never count as amendment evidence.
    parent_ref = _parent_reference(seed)
    if parent_ref:
        parent = _find_referenced_notice(parent_ref)
        if parent:
            chain[_notice_key(parent)] = parent
            pending.append(parent)
        chain[_notice_key(seed)] = seed
        pending.append(seed)
    else:
        chain[_notice_key(seed)] = seed
        pending.append(seed)

    pairs: list[dict[str, Any]] = []
    searched_refs: set[str] = set()
    truncated = False
    while pending and len(chain) < 20:
        if time.monotonic() - started > 30:
            truncated = True
            break
        parent = pending.pop(0)
        reference = _self_reference(parent)
        if not reference or reference in searched_refs:
            continue
        searched_refs.add(reference)
        child_result = _search(f'change-notice-version-identifier = "{reference}"', 20)
        children = child_result["notices"]
        if isinstance(child_result.get("totalNoticeCount"), int) and child_result["totalNoticeCount"] > len(children):
            truncated = True
        for child in children:
            if not isinstance(child, dict) or _parent_reference(child) != reference:
                continue
            key = _notice_key(child)
            parent_key = _notice_key(parent)
            if key == parent_key:
                continue
            chain.setdefault(key, child)
            pairs.append({"prior_key": parent_key, "current_key": key,
                          "reference": reference})
            if len(chain) < 20:
                pending.append(child)
            else:
                truncated = True

    if pending:
        truncated = True

    ordered = sorted(chain.values(), key=lambda row: (str(row.get("PD") or ""), str(row.get("ND") or "")))
    index_by_key = {_notice_key(row): i for i, row in enumerate(ordered)}
    linked_pairs = [{"prior_index": index_by_key[row["prior_key"]],
                    "current_index": index_by_key[row["current_key"]],
                    "reference": row["reference"]}
                   for row in pairs if row["prior_key"] in index_by_key and row["current_key"] in index_by_key]
    return {"source": "TED", "retrieved_at": _now(), "publication": publication,
            "notice_identifier": seed.get("notice-identifier"), "versions": _decorate(ordered),
            "pairs": linked_pairs, "total": data.get("totalNoticeCount", len(records)),
            "truncated": truncated, "pair_available": bool(linked_pairs) and not truncated}


def _parent_reference(record: dict[str, Any]) -> str | None:
    value = record.get("change-notice-version-identifier")
    if isinstance(value, list):
        value = value[0] if value else None
    return value.strip() if isinstance(value, str) and value.strip() else None


def _self_reference(record: dict[str, Any]) -> str | None:
    identifier = record.get("notice-identifier")
    version = record.get("notice-version")
    if isinstance(identifier, str) and NOTICE_UUID_RE.fullmatch(identifier) and version is not None:
        try:
            return f"{identifier}-{int(version):02d}"
        except (TypeError, ValueError):
            return None
    publication = record.get("ND")
    return publication if isinstance(publication, str) and PUBLICATION_RE.fullmatch(publication) else None


def _notice_key(record: dict[str, Any]) -> str:
    return str(record.get("ND") or record.get("notice-identifier") or hashlib.sha256(
        json.dumps(record, sort_keys=True, ensure_ascii=False).encode()).hexdigest())


def _find_referenced_notice(reference: str) -> dict[str, Any] | None:
    if PUBLICATION_RE.fullmatch(reference):
        rows = _search(f"ND = {reference}", 5)["notices"]
        return next((row for row in rows if isinstance(row, dict) and row.get("ND") == reference), None)
    match = re.fullmatch(r"([0-9a-fA-F-]{36})-([0-9]{2})", reference)
    if not match or not NOTICE_UUID_RE.fullmatch(match.group(1)):
        return None
    rows = _search(f"notice-identifier = {match.group(1)}", 20)["notices"]
    return next((row for row in rows if isinstance(row, dict)
                 and row.get("notice-identifier") == match.group(1)
                 and str(row.get("notice-version")).zfill(2) == match.group(2)), None)


def _decorate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for record in records:
        if not isinstance(record, dict):
            continue
        item = dict(record)
        item["source_url"] = f"https://ted.europa.eu/en/notice/-/detail/{item.get('ND', '')}"
        item["record_hash"] = hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False,
                                                          separators=(",", ":")).encode()).hexdigest()
        result.append(item)
    return result


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten nested TED values to stable field paths, preserving array order."""
    out: dict[str, Any] = {}
    if isinstance(value, dict):
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            out.update(flatten(value[key], path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.update(flatten(child, f"{prefix}[{index}]"))
    elif prefix:
        out[prefix] = value
    return out


def source_text(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def make_reference_delta(prior: dict[str, Any], current: dict[str, Any]) -> list[dict[str, Any]]:
    before, after = flatten(prior), flatten(current)
    changes = []
    for field in sorted(before.keys() | after.keys()):
        old, new = before.get(field), after.get(field)
        if old != new:
            changes.append({"field": field, "prior": old, "current": new,
                            "evidence": {"prior": source_text(old), "current": source_text(new)}})
    return changes


def task_record(record: dict[str, Any]) -> dict[str, Any]:
    """Project only meaningful eForms values; omit identity and transport metadata."""
    return {key: record[key] for key in TASK_FIELDS if key in record}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
