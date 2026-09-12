from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


def _tokens(value: str) -> set[str]:
    return {token.strip(".") for token in re.findall(r"[a-z0-9+#.]+", value.lower())}


def _contains_phrase(text: str, phrase: str) -> bool:
    return phrase.lower() in text.lower()


@dataclass(frozen=True)
class CandidateProfile:
    target_titles: tuple[str, ...]
    skills: tuple[str, ...]
    preferred_locations: tuple[str, ...] = ("remote", "vietnam")
    minimum_score: int = 60


@dataclass(frozen=True)
class Job:
    title: str
    company: str
    location: str
    description: str
    url: str
    eligibility_evidence: str = ""
    status: str = "new"


@dataclass(frozen=True)
class Analysis:
    score: int
    eligible: bool
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    reasons: tuple[str, ...]
    recommendation: str


def analyze(job: Job, profile: CandidateProfile) -> Analysis:
    searchable = " ".join((job.title, job.location, job.description, job.eligibility_evidence))
    eligible = _is_eligible(job)
    title_match = any(_contains_phrase(job.title, title) for title in profile.target_titles)
    location_match = any(
        _contains_phrase(job.location + " " + job.eligibility_evidence, location)
        for location in profile.preferred_locations
    )

    searchable_tokens = _tokens(searchable)
    matched = tuple(skill for skill in profile.skills if _tokens(skill) <= searchable_tokens)
    missing = tuple(skill for skill in profile.skills if skill not in matched)
    skill_ratio = len(matched) / max(len(profile.skills), 1)

    score = round(45 * skill_ratio + 30 * title_match + 25 * location_match)
    if not eligible:
        score = min(score, 39)

    reasons: list[str] = []
    reasons.append(f"Matched {len(matched)}/{len(profile.skills)} profile skills")
    reasons.append("Target title match" if title_match else "Title is outside the primary targets")
    reasons.append("Location preference match" if location_match else "Location needs verification")
    if not eligible:
        reasons.append("Eligibility evidence conflicts with remote work from Vietnam")

    if not eligible:
        recommendation = "skip"
    elif score >= 80:
        recommendation = "apply_now"
    elif score >= profile.minimum_score:
        recommendation = "review"
    else:
        recommendation = "low_priority"

    return Analysis(score, eligible, matched, missing, tuple(reasons), recommendation)


def _is_eligible(job: Job) -> bool:
    evidence = f"{job.location} {job.eligibility_evidence}".lower()
    blockers: Iterable[str] = (
        "us only",
        "united states only",
        "must be located in the us",
        "no international",
        "not available in vietnam",
    )
    return not any(blocker in evidence for blocker in blockers)
