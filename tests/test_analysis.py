from datetime import date

from job_radar.analysis import salary_prediction, trend_report


def job(role, discovered, low=None, high=None, level="Senior", skills=None):
    return {"role": role, "discovered_at": discovered, "seniority": level,
            "skills": skills or ["Python"], "reported_salary":
            {"min_usd_year": low, "max_usd_year": high} if low else None}


def test_trend_separates_demand_and_momentum():
    jobs = [job("AI Engineer", "2026-09-12"), job("AI Engineer", "2026-09-11"),
            job("AI Engineer", "2026-09-03"), job("Data Scientist", "2026-09-10")]
    report = trend_report(jobs, date(2026, 9, 13))
    ai = report["roles"][0]
    assert ai["active_jobs"] == 3
    assert ai["new_this_week"] == 2
    assert ai["momentum_pct"] == 100


def test_salary_uses_comparables_and_reports_confidence():
    jobs = [job("AI Engineer", "2026-09-12", 60000, 90000),
            job("AI Engineer", "2026-09-11", 70000, 100000),
            job("AI Engineer", "2026-09-10", 80000, 110000)]
    prediction = salary_prediction(jobs[0], jobs)
    assert prediction["min"] == 70000
    assert prediction["max"] == 100000
    assert prediction["sample_size"] == 3
    assert prediction["confidence"] == "low"
