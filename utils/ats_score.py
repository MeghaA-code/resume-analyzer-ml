"""
ats_score.py
------------
Heuristic ATS (Applicant Tracking System) compatibility scorer.

This is NOT a real ATS engine (no vendor exposes their scoring algorithm
publicly) — it's a transparent, rule-based approximation covering the
factors that are widely documented as affecting ATS parsing & recruiter
screening: keyword/skill match, section structure, quantified achievements,
action-verb usage, contact info presence, resume length, and formatting
signals.

The score is a weighted sum of 6 sub-scores (each 0-100), returned along
with a breakdown so the frontend can render a chart explaining *why* the
resume scored the way it did.
"""

import re
from utils.skills_data import SECTION_HEADERS, ACTION_VERBS

WEIGHTS = {
    "skill_match": 0.35,
    "section_structure": 0.20,
    "action_verbs": 0.15,
    "quantified_achievements": 0.15,
    "contact_info": 0.05,
    "length": 0.10,
}

EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s()]{7,}\d)")
LINKEDIN_RE = re.compile(r"linkedin\.com", re.IGNORECASE)
NUMBER_RE = re.compile(r"\b\d+%?\b")
BULLET_RE = re.compile(r"^[\s]*[•\-\*\u2022]", re.MULTILINE)


def _score_section_structure(raw_text_lower: str) -> float:
    found = sum(1 for h in SECTION_HEADERS if h in raw_text_lower)
    # 5+ recognizable sections is considered a well-structured resume
    return min(100.0, round((found / 5) * 100, 1))


def _score_action_verbs(raw_text_lower: str) -> float:
    found = sum(1 for v in ACTION_VERBS if v in raw_text_lower)
    # 8+ distinct action verbs is a strong signal
    return min(100.0, round((found / 8) * 100, 1))


def _score_quantified_achievements(raw_text: str) -> float:
    numbers_found = len(NUMBER_RE.findall(raw_text))
    # 6+ numeric/percentage data points suggests quantified, results-driven bullets
    return min(100.0, round((numbers_found / 6) * 100, 1))


def _score_contact_info(raw_text: str) -> float:
    score = 0
    if EMAIL_RE.search(raw_text):
        score += 50
    if PHONE_RE.search(raw_text):
        score += 30
    if LINKEDIN_RE.search(raw_text):
        score += 20
    return float(score)


def _score_length(raw_text: str) -> float:
    word_count = len(raw_text.split())
    # Ideal resume length: roughly 400-1000 words (~1-2 pages)
    if 400 <= word_count <= 1000:
        return 100.0
    if word_count < 400:
        return round((word_count / 400) * 100, 1)
    # penalize overly long resumes gently
    overflow = word_count - 1000
    return max(40.0, round(100 - (overflow / 50), 1))


def calculate_ats_score(raw_text: str, skill_match_percentage: float) -> dict:
    """
    Compute the overall ATS score (0-100) plus a breakdown of sub-scores.

    Args:
        raw_text: the original extracted resume text (unprocessed).
        skill_match_percentage: from skill_extractor.compare_with_category().

    Returns:
        dict with 'overall_score' and 'breakdown' (each sub-score 0-100).
    """
    raw_text_lower = raw_text.lower()

    breakdown = {
        "skill_match": round(skill_match_percentage, 1),
        "section_structure": _score_section_structure(raw_text_lower),
        "action_verbs": _score_action_verbs(raw_text_lower),
        "quantified_achievements": _score_quantified_achievements(raw_text),
        "contact_info": _score_contact_info(raw_text),
        "length": _score_length(raw_text),
    }

    overall = sum(breakdown[key] * WEIGHTS[key] for key in WEIGHTS)

    return {
        "overall_score": round(overall, 1),
        "breakdown": breakdown,
        "has_bullet_points": bool(BULLET_RE.search(raw_text)),
    }


def score_label(score: float) -> str:
    """Human-readable label for an overall ATS score."""
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 50:
        return "Needs Improvement"
    return "Poor"
