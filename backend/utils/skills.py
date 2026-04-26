SKILLS = [
    # TECH
    "python", "java", "c++", "javascript", "html", "css",
    "react", "nodejs", "sql", "mongodb",
    "machine learning", "deep learning", "tensorflow",
    "pandas", "numpy", "docker", "linux",

    # NON-TECH
    "communication", "teaching", "presentation",
    "classroom management", "leadership",
    "teamwork", "time management"
]

SKILL_MAP = {
    "js": "javascript",
    "node": "nodejs",
    "ml": "machine learning",
    "dl": "deep learning"
}


def normalize_skill(skill):
    return SKILL_MAP.get(skill.lower(), skill.lower())


def extract_skills(text):
    text = text.lower()
    found = set()

    for skill in SKILLS:
        if skill in text:
            found.add(normalize_skill(skill))

    return list(found)