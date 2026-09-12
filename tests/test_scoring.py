from job_radar.scoring import CandidateProfile, Job, analyze


PROFILE = CandidateProfile(
    target_titles=("AI Engineer", "Data Scientist"),
    skills=("Python", "LLM", "RAG", "FastAPI"),
)


def test_strong_remote_match_is_apply_now():
    job = Job(
        title="Senior AI Engineer",
        company="Example",
        location="Remote - Vietnam",
        description="Build Python LLM and RAG services using FastAPI.",
        url="https://example.com/job/1",
    )
    result = analyze(job, PROFILE)

    assert result.eligible is True
    assert result.score == 100
    assert result.recommendation == "apply_now"


def test_geographic_blocker_caps_score_and_skips():
    job = Job(
        title="AI Engineer",
        company="Example",
        location="Remote, US only",
        description="Python LLM RAG FastAPI",
        url="https://example.com/job/2",
    )
    result = analyze(job, PROFILE)

    assert result.eligible is False
    assert result.score == 39
    assert result.recommendation == "skip"
