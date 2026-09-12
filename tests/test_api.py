import csv
from pathlib import Path

from job_radar.db import connect, public_jobs
from job_radar.ingest import ingest


def test_ingest_and_public_feed(tmp_path: Path):
    csv_path = tmp_path / "jobs.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["title", "company", "location", "description", "url", "status"])
        writer.writeheader()
        writer.writerow({"title":"Senior AI Engineer","company":"Acme","location":"Remote - Vietnam","description":"Python RAG FastAPI Docker","url":"https://example.com/1","status":"new"})
        writer.writerow({"title":"Old role","company":"Acme","location":"Remote","description":"Python","url":"https://example.com/2","status":"closed"})
    database = tmp_path / "jobs.db"
    assert ingest(csv_path, database) == 2
    with connect(database) as connection:
        jobs = public_jobs(connection)
    assert len(jobs) == 1
    assert jobs[0]["role"] == "AI Engineer"
    assert jobs[0]["seniority"] == "Senior"
    assert jobs[0]["skills"] == ["Python", "RAG", "FastAPI", "Docker"]
    assert jobs[0]["vietnam_eligible"] is True
