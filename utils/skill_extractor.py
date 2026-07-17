"""
skill_extractor.py
-------------------
Finds which known skills (from skills_data.ALL_SKILLS) appear in a resume,
and compares them against the ideal skill set for a predicted job category
to find matched vs. missing skills.
"""

import re
from utils.skills_data import ALL_SKILLS, CATEGORY_SKILLS


def _build_pattern(skill: str) -> re.Pattern:
    """Build a whole-word/phrase regex pattern for a skill (handles multi-word skills)."""
    escaped = re.escape(skill)
    # allow the skill to match as a whole word/phrase, case-insensitive
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)


# Pre-compile patterns once at import time for performance.
_SKILL_PATTERNS = {skill: _build_pattern(skill) for skill in ALL_SKILLS}


def extract_skills(raw_text: str) -> list:
    """Scan raw (unprocessed) resume text and return the list of recognized skills found."""
    found = []
    for skill, pattern in _SKILL_PATTERNS.items():
        if pattern.search(raw_text):
            found.append(skill)
    return sorted(found)


def compare_with_category(found_skills: list, category: str) -> dict:
    """
    Compare the skills found in a resume against the ideal skill set for
    the predicted job category.

    Returns a dict with matched_skills, missing_skills, and match_percentage.
    """
    ideal_skills = set(CATEGORY_SKILLS.get(category, []))
    found_set = set(found_skills)

    matched = sorted(ideal_skills & found_set)
    missing = sorted(ideal_skills - found_set)

    match_percentage = round((len(matched) / len(ideal_skills)) * 100, 1) if ideal_skills else 0.0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": match_percentage,
        "total_required": len(ideal_skills),
    }
