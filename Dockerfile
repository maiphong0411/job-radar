FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN mkdir -p /app/data
ENV JOB_RADAR_DB=/app/data/job-radar.db
EXPOSE 8000
CMD ["uvicorn", "job_radar.api:app", "--host", "0.0.0.0", "--port", "8000"]
