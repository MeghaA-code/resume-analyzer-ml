"""
generate_dataset.py
--------------------
Generates a synthetic labeled resume dataset for training the job-category
classifier. Real resume datasets are copyrighted/PII-sensitive, so this
project builds synthetic-but-realistic resume snippets by combining
category-specific skills, summary templates, and experience phrases.

Run directly to (re)create data/resume_dataset.csv:
    python generate_dataset.py
"""

import csv
import random
from utils.skills_data import CATEGORY_SKILLS

random.seed(42)

SUMMARY_TEMPLATES = [
    "Result-driven {category} professional with {years} years of experience "
    "delivering high quality solutions using {skills}.",
    "Motivated {category} specialist skilled in {skills}, passionate about "
    "solving real world problems and collaborating with cross functional teams.",
    "Experienced {category} practitioner with a strong background in {skills}, "
    "proven track record of {achievement}.",
    "Detail oriented {category} candidate proficient in {skills} seeking to "
    "leverage {years} years of hands on experience.",
]

ACHIEVEMENTS = [
    "improving system performance by 30 percent",
    "reducing operational costs by 20 percent",
    "leading a team of 5 engineers to deliver projects on time",
    "increasing customer satisfaction scores by 25 percent",
    "automating manual workflows saving 15 hours per week",
    "successfully launching 3 major products",
]

EXPERIENCE_TEMPLATES = [
    "Developed and maintained applications using {skills} in an agile environment.",
    "Collaborated with stakeholders to gather requirements and implement {skills} "
    "based solutions.",
    "Utilized {skills} to design, build and deploy scalable systems.",
    "Responsible for {skills} related tasks including documentation, testing and "
    "code reviews.",
    "Applied {skills} to analyze data and generate actionable insights for "
    "leadership.",
]

SECTION_TEXT = (
    "Contact: jane.doe@example.com | +1-555-123-4567 | linkedin.com/in/janedoe\n"
    "Summary\n{summary}\n"
    "Skills\n{skills_list}\n"
    "Experience\n{experience}\n"
    "Education\nBachelor of Science in relevant field, University, {grad_year}\n"
    "Projects\nBuilt a project applying {project_skills} to a real world use case.\n"
    "Certifications\nCertified professional in {cert_skill}."
)


def _sample_skills(category: str, k: int) -> list:
    pool = CATEGORY_SKILLS[category]
    k = min(k, len(pool))
    return random.sample(pool, k)


def generate_resume_text(category: str) -> str:
    years = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
    skills = _sample_skills(category, random.randint(6, 10))
    skills_str = ", ".join(skills)

    summary = random.choice(SUMMARY_TEMPLATES).format(
        category=category,
        years=years,
        skills=skills_str,
        achievement=random.choice(ACHIEVEMENTS),
    )

    experience_lines = []
    for _ in range(random.randint(2, 3)):
        exp_skills = ", ".join(_sample_skills(category, random.randint(2, 4)))
        experience_lines.append(
            random.choice(EXPERIENCE_TEMPLATES).format(skills=exp_skills)
        )
    experience = "\n".join(f"- {line}" for line in experience_lines)

    project_skills = ", ".join(_sample_skills(category, random.randint(2, 3)))
    cert_skill = random.choice(CATEGORY_SKILLS[category])
    grad_year = random.choice(range(2012, 2023))

    return SECTION_TEXT.format(
        summary=summary,
        skills_list=", ".join(skills),
        experience=experience,
        grad_year=grad_year,
        project_skills=project_skills,
        cert_skill=cert_skill,
    )


def build_dataset(samples_per_category: int = 60) -> list:
    rows = []
    for category in CATEGORY_SKILLS:
        for _ in range(samples_per_category):
            text = generate_resume_text(category)
            rows.append({"category": category, "resume_text": text})
    random.shuffle(rows)
    return rows


def save_dataset(rows: list, path: str = "data/resume_dataset.csv") -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "resume_text"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    dataset_rows = build_dataset(samples_per_category=60)
    save_dataset(dataset_rows)
    print(f"Generated {len(dataset_rows)} synthetic resume samples -> data/resume_dataset.csv")
