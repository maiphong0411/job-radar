from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from job_radar.scoring import CandidateProfile, Job, analyze


def _load_profile(path: Path) -> CandidateProfile:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CandidateProfile(
        target_titles=tuple(raw["target_titles"]),
        skills=tuple(raw["skills"]),
        preferred_locations=tuple(raw.get("preferred_locations", ("Remote", "Vietnam"))),
        minimum_score=int(raw.get("minimum_score", 60)),
    )


def _first(row: dict[str, str], *names: str) -> str:
    for name in names:
        if row.get(name):
            return row[name].strip()
    return ""


def _load_jobs(path: Path) -> list[Job]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source)
        return [
            Job(
                title=_first(row, "title", "job_title"),
                company=_first(row, "company", "company_name"),
                location=_first(row, "location", "job_location"),
                description=_first(row, "description", "job_description"),
                url=_first(row, "url", "job_url", "source_url"),
                eligibility_evidence=_first(row, "eligibility_evidence"),
                status=_first(row, "status") or "new",
            )
            for row in rows
        ]


def run(csv_path: Path, profile_path: Path, output_path: Path) -> int:
    profile = _load_profile(profile_path)
    results = []
    for job in _load_jobs(csv_path):
        if job.status.lower() == "closed":
            continue
        analysis = analyze(job, profile)
        results.append({"job": asdict(job), "analysis": asdict(analysis)})

    results.sort(key=lambda item: item["analysis"]["score"], reverse=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Analyzed {len(results)} active jobs. Shortlist saved to {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank private job-history data")
    parser.add_argument("command", choices=["analyze"])
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--profile", type=Path, default=Path("profile.example.json"))
    parser.add_argument("--output", type=Path, default=Path("output/shortlist.json"))
    args = parser.parse_args()
    return run(args.csv_path, args.profile, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
