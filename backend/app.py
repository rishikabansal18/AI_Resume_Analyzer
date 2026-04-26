from flask import Flask, request, jsonify, send_from_directory
import os

from utils.parser import extract_text
from utils.skills import extract_skills
from services.matcher import get_similarity
from services.gap import skill_gap
from models.ann_model import train_model, predict_score

app = Flask(__name__, static_folder="static")

print("Training ANN...")
model = train_model()
print("Model ready ✅")


# 🔥 Resume validation
def is_resume(text):
    text = text.lower()

    keywords = [
        "education", "experience", "skills",
        "projects", "internship", "summary",
        "profile", "certification"
    ]

    score = sum(1 for k in keywords if k in text)

    return score >= 2


# 🔥 Role expansion (tech + non-tech)
def expand_role(text):
    mapping = {
        "software developer": "python java sql algorithms",
        "web developer": "html css javascript react nodejs",
        "data scientist": "python pandas machine learning sql",

        "teacher": "communication teaching presentation classroom management",
        "hr": "communication recruitment leadership teamwork",
        "manager": "leadership management communication planning"
    }

    return mapping.get(text.lower().strip(), text)


# 🔥 Skill importance
IMPORTANT_SKILLS = {
    "python", "machine learning", "sql", "javascript", "communication"
}


def weighted_score(matched, total):
    if total == 0:
        return 0

    score = 0
    for skill in matched:
        if skill in IMPORTANT_SKILLS:
            score += 2
        else:
            score += 1

    return round((score / (total * 2)) * 100, 2)


# 🔥 Skill explanations
SKILL_INFO = {
    "python": "Programming Language",
    "sql": "Database Language",
    "tensorflow": "Deep Learning Framework",
    "docker": "Container Tool",
    "communication": "Soft Skill",
    "leadership": "Management Skill"
}


def feedback(score):
    if score > 70:
        return "🔥 Strong profile"
    elif score > 40:
        return "👍 Average profile"
    else:
        return "⚠️ Needs improvement"


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("resume")
        role = request.form.get("role")
        custom_job = request.form.get("job_desc")

        if not file:
            return jsonify({"error": "Upload resume first"}), 400

        filepath = "temp_resume.pdf"
        file.save(filepath)

        resume_text = extract_text(filepath)

        # 🔥 Resume validation
        if not is_resume(resume_text):
            os.remove(filepath)
            return jsonify({
                "error": "⚠️ Please upload a valid resume"
            }), 400

        # Job description
        if role == "ml":
            job_desc = "machine learning python tensorflow sql deep learning"
        elif role == "web":
            job_desc = "html css javascript react nodejs"
        elif role == "data":
            job_desc = "python pandas sql machine learning"
        elif role == "other":
            job_desc = expand_role(custom_job)
        else:
            return jsonify({"error": "Select a valid role"}), 400

        # Pipeline
        user_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_desc)

        similarity = get_similarity(resume_text, job_desc)

        if len(job_skills) == 0:
            matched, missing = [], []
        else:
            matched, missing = skill_gap(user_skills, job_skills)

        rule_score = weighted_score(matched, len(job_skills))

        skill_ratio = len(matched) / len(job_skills) if job_skills else 0
        ann_score = predict_score(model, similarity, skill_ratio)

        os.remove(filepath)

        missing_detailed = [
            f"{s} ({SKILL_INFO.get(s,'Skill')})"
            for s in missing
        ]

        return jsonify({
            "role": role,
            "matched_skills": matched,
            "missing_skills": missing_detailed,
            "similarity": round(similarity, 3),
            "rule_score": rule_score,
            "ann_score": round(ann_score * 100, 2),
            "feedback": feedback(ann_score * 100)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()