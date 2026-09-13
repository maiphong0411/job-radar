from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

from job_radar.db import connect, upsert_job


KNOWN_SKILLS = ("Python", "SQL", "NLP", "LLM", "RAG", "FastAPI", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "MLflow", "Airflow")


def first(row: dict[str, str], *names: str) -> str:
    return next((row[name].strip() for name in names if row.get(name)), "")


def infer_role(title: str) -> str:
    lowered = title.lower()
    for value in ("AI Engineer", "Machine Learning Engineer", "Data Scientist", "Data Engineer"):
        if value.lower() in lowered:
            return value
    return "Other"


def infer_seniority(title: str) -> str:
    lowered = title.lower()
    if re.search(r"\b(senior|sr\.?|lead|principal|staff)\b", lowered): return "Senior"
    if re.search(r"\b(junior|jr\.?|intern|graduate)\b", lowered): return "Junior"
    return "Mid-level"


def normalize(row: dict[str, str]) -> dict:
    title = first(row, "title", "job_title")
    url = first(row, "url", "job_url", "source_url")
    description = first(row, "description", "job_description")
    location = first(row, "location", "job_location")
    evidence = first(row, "eligibility_evidence")
    identifier = first(row, "id", "job_id") or hashlib.sha256(url.encode()).hexdigest()[:20]
    text = f"{title} {description}".lower()
    blockers = ("us only", "united states only", "not available in vietnam", "no international")
    eligible = not any(value in f"{location} {evidence}".lower() for value in blockers)
    salary_min = first(row, "salary_min_usd", "min_salary_usd")
    salary_max = first(row, "salary_max_usd", "max_salary_usd")
    period = first(row, "salary_period").lower()
    multiplier = 12 if period in ("month", "monthly") else 1
    return {
        "id": identifier, "title": title, "company": first(row, "company", "company_name"),
        "role": first(row, "role") or infer_role(title),
        "seniority": first(row, "seniority") or infer_seniority(title), "location": location,
        "vietnam_eligible": eligible,
        "discovered_at": first(row, "discovered_at", "first_seen_at")[:10] or datetime.now(UTC).date().isoformat(),
        "url": url, "description": description,
        "status": "closed" if first(row, "status").lower() == "closed" else "open",
        "skills": [skill for skill in KNOWN_SKILLS if skill.lower() in text],
        "salary_min_usd": float(salary_min) * multiplier if salary_min else None,
        "salary_max_usd": float(salary_max or salary_min) * multiplier if salary_min else None,
    }


def ingest(csv_path: Path, db_path: Path | None = None) -> int:
    with csv_path.open(encoding="utf-8-sig", newline="") as source, connect(db_path) as connection:
        count = 0
        for row in csv.DictReader(source):
            job = normalize(row)
            if not job["title"] or not job["url"]:
                continue
            upsert_job(connection, job); count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Import private job CSV into SQLite")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--database", type=Path)
    args = parser.parse_args()
    print(f"Imported {ingest(args.csv_path, args.database)} jobs")
    return 0
