from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator


SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    seniority TEXT NOT NULL,
    location TEXT NOT NULL,
    vietnam_eligible INTEGER NOT NULL DEFAULT 0,
    discovered_at TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open',
    skills_json TEXT NOT NULL DEFAULT '[]',
    analysis_json TEXT,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_discovered ON jobs(discovered_at DESC);
"""


def database_path() -> Path:
    return Path(os.getenv("JOB_RADAR_DB", "data/job-radar.db"))


@contextmanager
def connect(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    target = path or database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    try:
        connection.executescript(SCHEMA)
        yield connection
        connection.commit()
    finally:
        connection.close()


def upsert_job(connection: sqlite3.Connection, job: dict) -> None:
    now = datetime.now(UTC).isoformat()
    connection.execute(
        """INSERT INTO jobs (
            id,title,company,role,seniority,location,vietnam_eligible,discovered_at,
            url,description,status,skills_json,analysis_json,updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title, company=excluded.company, role=excluded.role,
            seniority=excluded.seniority, location=excluded.location,
            vietnam_eligible=excluded.vietnam_eligible, description=excluded.description,
            status=excluded.status, skills_json=excluded.skills_json,
            analysis_json=COALESCE(excluded.analysis_json,jobs.analysis_json),
            updated_at=excluded.updated_at""",
        (
            job["id"], job["title"], job["company"], job["role"], job["seniority"],
            job["location"], int(job["vietnam_eligible"]), job["discovered_at"],
            job["url"], job.get("description", ""), job.get("status", "open"),
            json.dumps(job.get("skills", [])),
            json.dumps(job["analysis"]) if job.get("analysis") else None, now,
        ),
    )


def public_jobs(connection: sqlite3.Connection) -> list[dict]:
    rows = connection.execute(
        "SELECT * FROM jobs WHERE status='open' ORDER BY discovered_at DESC"
    ).fetchall()
    return [serialize(row) for row in rows]


def serialize(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"], "title": row["title"], "company": row["company"],
        "role": row["role"], "seniority": row["seniority"],
        "location": row["location"], "vietnam_eligible": bool(row["vietnam_eligible"]),
        "discovered_at": row["discovered_at"], "url": row["url"],
        "skills": json.loads(row["skills_json"]),
        "analysis": json.loads(row["analysis_json"]) if row["analysis_json"] else None,
    }
