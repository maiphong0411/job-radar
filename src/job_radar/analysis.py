from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from statistics import median


RESOURCES = {
    "Python": {"title": "Python Tutorial", "url": "https://docs.python.org/3/tutorial/"},
    "SQL": {"title": "PostgreSQL Tutorial", "url": "https://www.postgresql.org/docs/current/tutorial.html"},
    "Docker": {"title": "Docker Get Started", "url": "https://docs.docker.com/get-started/"},
    "Kubernetes": {"title": "Kubernetes Basics", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"},
    "FastAPI": {"title": "FastAPI Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"},
    "AWS": {"title": "AWS Skill Builder", "url": "https://skillbuilder.aws/"},
    "Azure": {"title": "Microsoft Learn: Azure", "url": "https://learn.microsoft.com/training/azure/"},
    "GCP": {"title": "Google Cloud Training", "url": "https://cloud.google.com/learn/training"},
    "MLflow": {"title": "MLflow Quickstart", "url": "https://mlflow.org/docs/latest/ml/getting-started/"},
    "Airflow": {"title": "Airflow Tutorial", "url": "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/"},
    "RAG": {"title": "RAG paper", "url": "https://arxiv.org/abs/2005.11401"},
}


def trend_report(jobs: list[dict], today: date | None = None) -> dict:
    today = today or date.today()
    current_start, previous_start = today - timedelta(days=6), today - timedelta(days=13)
    roles = Counter(job["role"] for job in jobs)
    skills = Counter(skill for job in jobs for skill in job["skills"])
    current = Counter(job["role"] for job in jobs if _day(job) >= current_start)
    previous = Counter(job["role"] for job in jobs if previous_start <= _day(job) < current_start)
    role_trends = []
    for role, active in roles.most_common():
        recent, prior = current[role], previous[role]
        momentum = None if prior == 0 else round((recent - prior) / prior * 100)
        role_trends.append({"role": role, "active_jobs": active, "new_this_week": recent,
                            "previous_week": prior, "momentum_pct": momentum,
                            "confidence": _confidence(recent + prior)})
    learning = [{"skill": skill, "job_count": count, "resource": RESOURCES.get(skill)}
                for skill, count in skills.most_common(8)]
    return {"window_days": 7, "roles": role_trends, "skills": learning,
            "method": "Active demand plus new postings versus the previous 7-day window"}


def salary_prediction(target: dict, jobs: list[dict]) -> dict:
    labelled = [job for job in jobs if job.get("reported_salary") and job["role"] == target["role"]]
    same_level = [job for job in labelled if job["seniority"] == target["seniority"]]
    comparable = same_level if len(same_level) >= 3 else labelled
    if not comparable:
        return {"status": "unknown", "reason": "No salary-labelled comparable jobs"}
    lows = [job["reported_salary"]["min_usd_year"] for job in comparable]
    highs = [job["reported_salary"]["max_usd_year"] for job in comparable]
    count = len(comparable)
    return {"status": "predicted", "currency": "USD", "period": "year",
            "min": round(median(lows), -2), "max": round(median(highs), -2),
            "sample_size": count, "confidence": _confidence(count),
            "method": "Median range of comparable salary-labelled roles"}


def enrich(jobs: list[dict]) -> list[dict]:
    for job in jobs:
        job["salary_prediction"] = salary_prediction(job, jobs)
    return jobs


def _day(job: dict) -> date:
    return date.fromisoformat(job["discovered_at"][:10])


def _confidence(sample_size: int) -> str:
    if sample_size >= 20: return "high"
    if sample_size >= 5: return "medium"
    return "low"
