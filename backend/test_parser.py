from utils.parser import extract_text
from utils.skills import extract_skills
from services.matcher import get_similarity
from services.gap import skill_gap
from services.score import calculate_score
from models.ann_model import train_model, predict_score

import os
print("Running file from:", os.path.abspath(__file__))


# Step 1: Extract resume text
resume_text = extract_text("resume.pdf")

# Step 2: Extract user skills
user_skills = extract_skills(resume_text)

# Step 3: Job description
job_desc = """
Looking for a Machine Learning Engineer with experience in Python,
Deep Learning, TensorFlow, and SQL.
"""

# Step 4: Extract job skills
job_skills = extract_skills(job_desc)

# Step 5: Similarity
similarity = get_similarity(resume_text, job_desc)

# Step 6: Skill gap
matched, missing = skill_gap(user_skills, job_skills)

# Step 7: Rule-based score
score = calculate_score(similarity, matched, len(job_skills))


# ================= ANN =================

print("\n===== ANN START =====")

model = train_model()
print("Model trained")

skill_match_ratio = len(matched) / len(job_skills) if len(job_skills) > 0 else 0
print("Skill ratio:", skill_match_ratio)

ann_score = predict_score(model, similarity, skill_match_ratio)
print("Raw ANN output:", ann_score)

print("===== ANN END =====\n")


# ================= OUTPUT =================

print("===== FINAL RESULT =====")
print("User Skills:", user_skills)
print("Job Skills:", job_skills)
print("Matched Skills:", matched)
print("Missing Skills:", missing)
print("Match Score:", round(similarity, 3))
print("Final Score:", score)
print("ANN Score:", round(ann_score * 100, 2))