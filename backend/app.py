from flask import Flask, request, jsonify, send_from_directory
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.parser import extract_text
from utils.skills import extract_skills
from services.gap import skill_gap
from models.ann_model import train_model, predict_score

app = Flask(__name__, static_folder="static")

# 🔥 Train ANN model once
model = train_model()


# ✅ Resume validation
def is_resume(text):
    text = text.lower()
    keywords = ["education", "experience", "skills", "projects"]
    return sum(k in text for k in keywords) >= 2


# ✅ Lightweight similarity (NO heavy models)
def get_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(vectors[0], vectors[1])[0][0]


# ✅ Role expansion (custom roles supported)
def expand_role(text):
    mapping = {
        "data scientist": "python pandas machine learning sql",
        "web developer": "html css javascript react nodejs",
        "software developer": "python java sql",
        "teacher": "communication teaching classroom management",
        "manager": "leadership communication planning",
        "cybersecurity": "network security linux cryptography"
    }
    return mapping.get(text.lower().strip(), text)


# ✅ Skill weighting
IMPORTANT = {"python", "sql", "machine learning", "communication"}


def weighted_score(matched, total):
    if total == 0:
        return 0
    score = sum(2 if s in IMPORTANT else 1 for s in matched)
    return round((score / (total * 2)) * 100, 2)


# ✅ Feedback system
def feedback(score):
    if score > 70:
        return "🔥 Strong profile"
    elif score > 40:
        return "👍 Average profile"
    else:
        return "⚠️ Needs improvement"


# 🔥 Home route
@app.route("/")
def home():
    return send_from_directory("static", "index.html")


# 🚀 MAIN ANALYZE API
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("resume")
        role = request.form.get("role")
        job_desc = request.form.get("job_desc")

        if not file:
            return jsonify({"error": "Upload resume"}), 400

        # Save file temporarily
        path = "temp.pdf"
        file.save(path)

        # Extract text
        text = extract_text(path)

        # Validate resume
        if not is_resume(text):
            os.remove(path)
            return jsonify({"error": "⚠️ Upload a valid resume"}), 400

        # Expand role
        job_desc = expand_role(job_desc)

        # Extract skills
        user_skills = extract_skills(text)
        job_skills = extract_skills(job_desc)

        # Similarity
        similarity = get_similarity(text, job_desc)

        # Skill gap
        matched, missing = skill_gap(user_skills, job_skills)

        # Rule-based score
        rule_score = weighted_score(matched, len(job_skills))

        # ANN score
        ratio = len(matched) / len(job_skills) if job_skills else 0
        ann_score = predict_score(model, similarity, ratio)

        # Cleanup
        os.remove(path)

        return jsonify({
            "role": job_desc,
            "matched_skills": matched,
            "missing_skills": missing,
            "similarity": round(similarity, 3),
            "rule_score": rule_score,
            "ann_score": round(ann_score * 100, 2),
            "feedback": feedback(ann_score * 100)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🚀 RUN APP
if __name__ == "__main__":
    app.run()