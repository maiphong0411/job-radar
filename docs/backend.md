# Private backend

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
job-radar-ingest /private/path/linkedin_ai_job_history.csv
uvicorn job_radar.api:app --reload
```

The API is available at `http://localhost:8000/jobs` and health checks at `/health`.

## Environment

| Variable | Default | Purpose |
| --- | --- | --- |
| `JOB_RADAR_DB` | `data/job-radar.db` | Private SQLite file path |
| `JOB_RADAR_ALLOWED_ORIGINS` | GitHub Pages plus localhost | Comma-separated CORS origins |

## Docker

```bash
docker build -t job-radar-api .
docker run -p 8000:8000 -v job-radar-data:/app/data job-radar-api
```

Use a persistent volume so the database survives container replacement. The database and imported CSV files are ignored by Git.

The current API deliberately exposes only normalized public job fields. Raw descriptions remain in SQLite for later analysis but are not returned by `/jobs`.
