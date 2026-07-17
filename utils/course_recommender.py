"""
course_recommender.py
----------------------
Given a list of missing skills (skills required for the predicted category
but not found in the resume), suggest learning resources for each so the
user has a clear, actionable upskilling plan.
"""

from utils.skills_data import COURSE_RECOMMENDATIONS


def recommend_courses(missing_skills: list, limit_per_skill: int = 3, max_skills: int = 8) -> list:
    """
    Build a course recommendation list for the top missing skills.

    Args:
        missing_skills: skills required for the category but absent from the resume.
        limit_per_skill: max number of course suggestions per skill.
        max_skills: cap on how many missing skills to generate recommendations for
                    (keeps the UI focused on the highest-priority gaps).

    Returns:
        List of {"skill": str, "courses": [str, ...]} dicts.
    """
    recommendations = []
    for skill in missing_skills[:max_skills]:
        courses = COURSE_RECOMMENDATIONS.get(skill, [])[:limit_per_skill]
        if courses:
            recommendations.append({"skill": skill, "courses": courses})
    return recommendations
