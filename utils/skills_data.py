"""
skills_data.py
----------------
Static knowledge base used across the app:
  * JOB_CATEGORIES     -> list of job categories the ML model predicts
  * CATEGORY_SKILLS    -> the "ideal" skill set expected for each category
  * ALL_SKILLS         -> flattened, de-duplicated master skill list (used by the skill extractor)
  * COURSE_RECOMMENDATIONS -> skill -> list of suggested learning resources
  * SECTION_HEADERS    -> common resume section titles (used by the ATS scorer)
  * ACTION_VERBS       -> strong resume action verbs (used by the ATS scorer)

Keeping this data in one module makes it trivial to extend the app with new
job categories or skills without touching the ML pipeline or Flask routes.
"""

JOB_CATEGORIES = [
    "Data Science",
    "Web Development",
    "Android Development",
    "Software Engineering",
    "DevOps Engineering",
    "Database Administration",
    "Network Engineering",
    "UI/UX Design",
    "Business Analysis",
    "Human Resources",
]

CATEGORY_SKILLS = {
    "Data Science": [
        "python", "r", "sql", "machine learning", "deep learning", "pandas",
        "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "data visualization", "matplotlib", "seaborn", "power bi", "tableau",
        "statistics", "nlp", "computer vision", "feature engineering",
        "big data", "spark", "hadoop", "jupyter", "data cleaning", "etl",
    ],
    "Web Development": [
        "html", "css", "javascript", "react", "angular", "vue", "node.js",
        "express", "django", "flask", "php", "laravel", "rest api",
        "graphql", "mongodb", "mysql", "postgresql", "git", "bootstrap",
        "tailwind css", "typescript", "webpack", "responsive design", "ajax",
    ],
    "Android Development": [
        "java", "kotlin", "android studio", "xml", "sqlite", "firebase",
        "rest api", "mvvm", "jetpack compose", "gradle", "material design",
        "retrofit", "room database", "android sdk", "git", "unit testing",
    ],
    "Software Engineering": [
        "java", "c++", "python", "data structures", "algorithms",
        "object oriented programming", "system design", "git", "agile",
        "unit testing", "design patterns", "microservices", "rest api",
        "docker", "ci/cd", "linux", "sql", "debugging", "multithreading",
    ],
    "DevOps Engineering": [
        "docker", "kubernetes", "jenkins", "ci/cd", "aws", "azure", "gcp",
        "terraform", "ansible", "linux", "bash scripting", "git",
        "prometheus", "grafana", "nginx", "load balancing", "monitoring",
        "shell scripting", "cloud computing",
    ],
    "Database Administration": [
        "sql", "mysql", "postgresql", "oracle", "mongodb", "database design",
        "indexing", "query optimization", "backup and recovery", "etl",
        "data modeling", "stored procedures", "replication", "sql server",
        "nosql", "database security",
    ],
    "Network Engineering": [
        "networking", "tcp/ip", "cisco", "routing", "switching", "firewall",
        "vpn", "network security", "dns", "dhcp", "lan", "wan", "ccna",
        "wireshark", "load balancing", "network monitoring", "linux",
    ],
    "UI/UX Design": [
        "figma", "adobe xd", "sketch", "wireframing", "prototyping",
        "user research", "usability testing", "design thinking",
        "interaction design", "photoshop", "illustrator", "typography",
        "color theory", "responsive design", "accessibility",
    ],
    "Business Analysis": [
        "requirements gathering", "sql", "excel", "power bi", "tableau",
        "stakeholder management", "business process modeling", "jira",
        "agile", "scrum", "data analysis", "swot analysis", "uml",
        "gap analysis", "documentation", "communication",
    ],
    "Human Resources": [
        "recruitment", "onboarding", "payroll", "performance management",
        "employee relations", "hr policies", "talent acquisition",
        "hris", "compensation and benefits", "labor law",
        "conflict resolution", "training and development",
        "communication", "excel",
    ],
}

# Flattened master list used by the skill extractor to scan resume text.
ALL_SKILLS = sorted({skill for skills in CATEGORY_SKILLS.values() for skill in skills})

# Generic, illustrative learning-resource suggestions per skill.
# Platform names are real; specific course titles are indicative placeholders,
# meant as a starting point for the user to search rather than a verified catalog.
COURSE_RECOMMENDATIONS = {
    skill: [
        f"{skill.title()} Fundamentals — Coursera",
        f"{skill.title()} Crash Course — Udemy",
        f"{skill.title()} Documentation & Official Tutorials",
    ]
    for skill in ALL_SKILLS
}

SECTION_HEADERS = [
    "experience", "work experience", "education", "skills",
    "projects", "certifications", "summary", "objective",
    "contact", "achievements", "publications", "languages",
]

ACTION_VERBS = [
    "achieved", "built", "created", "designed", "developed", "engineered",
    "implemented", "improved", "increased", "launched", "led", "managed",
    "optimized", "reduced", "resolved", "spearheaded", "streamlined",
    "collaborated", "automated", "delivered", "analyzed", "architected",
]
