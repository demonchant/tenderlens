"""Durable idempotent validator score history for real testnet tasks."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10, isolation_level="IMMEDIATE")
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("""CREATE TABLE IF NOT EXISTS task_scores (
        netuid INTEGER NOT NULL,
        miner_hotkey TEXT NOT NULL,
        miner_uid INTEGER NOT NULL,
        task_id TEXT NOT NULL,
        score REAL NOT NULL CHECK(score >= 0 AND score <= 1),
        recorded_at TEXT NOT NULL,
        PRIMARY KEY (netuid, miner_hotkey, task_id)
    )""")
    connection.execute("CREATE INDEX IF NOT EXISTS score_window ON task_scores(netuid, miner_hotkey, recorded_at)")
    return connection


def record_round(netuid: int, entries: list[dict], window: int = 32,
                 path: Path | None = None) -> dict[str, dict[str, float | int]]:
    """Keep the first score for each task/hotkey immutable, then average distinct recent tasks."""
    if path is None:
        path = Path(os.getenv("TL_SCORE_DB", "data/validator-scores.sqlite"))
    now = datetime.now(timezone.utc).isoformat()
    db = _connect(path)
    try:
        for entry in entries:
            db.execute("""INSERT OR IGNORE INTO task_scores(netuid, miner_hotkey, miner_uid, task_id, score, recorded_at)
                VALUES(?, ?, ?, ?, ?, ?)""",
                       (netuid, entry["hotkey"], entry["uid"], entry["task_id"], entry["score"], now))
        result: dict[str, dict[str, float | int]] = {}
        for entry in entries:
            hotkey = entry["hotkey"]
            rows = db.execute("""SELECT miner_uid, score FROM task_scores
                WHERE netuid=? AND miner_hotkey=? ORDER BY recorded_at DESC, task_id DESC LIMIT ?""",
                              (netuid, hotkey, window)).fetchall()
            if rows:
                result[hotkey] = {"uid": int(rows[0][0]), "score": sum(float(r[1]) for r in rows) / len(rows),
                                  "samples": len(rows)}
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return result
