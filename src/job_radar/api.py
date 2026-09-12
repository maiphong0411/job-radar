from __future__ import annotations

import os
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from job_radar.db import connect, public_jobs


def allowed_origins() -> list[str]:
    configured = os.getenv(
        "JOB_RADAR_ALLOWED_ORIGINS", "https://maiphong0411.github.io,http://localhost:8000"
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app = FastAPI(title="Job Radar API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/jobs")
def jobs() -> dict:
    with connect() as connection:
        records = public_jobs(connection)
    return {"updated_at": datetime.now(UTC).isoformat(), "jobs": records}
