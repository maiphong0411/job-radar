# Job Radar

Job Radar is an MVP for finding remote AI/Data jobs available to candidates in Vietnam and turning raw listings into a useful, explainable shortlist.

The repository contains application code only. Personal job-history data stays outside GitHub and is supplied at runtime.

## MVP scope

- Import normalized job listings from a private CSV.
- Apply hard eligibility checks before ranking.
- Score each role against a configurable candidate profile.
- Explain matching evidence, gaps, and a recommended action.
- Export a JSON shortlist for a future web UI.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
job-radar analyze /path/to/linkedin_ai_job_history.csv --profile profile.example.json
pytest
```

See `docs/data-contract.md` for the expected private CSV fields.
