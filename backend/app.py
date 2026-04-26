from flask import Flask, request, jsonify, render_template
import pdfplumber
import re

app = Flask(__name__)

# 📄 Extract text
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

# ✅ Resume validation
def is_valid_resume(text):
    keywords = ["education", "experience", "skills", "projects"]
    return sum(1 for k in keywords if k in text) >= 2

# 🔍 Skill match
def skill_match(skill, text):
    return re.search(r"\b" + re.escape(skill) + r"\b", text) is not None

# 🧠 Domain-aware role → skills
def get_expected_skills(role):
    role = role.lower()

    if "electrical" in role:
        return ["circuit design", "matlab", "electronics", "power systems"]

    if "embedded" in role:
        return ["c", "microcontroller", "embedded systems", "arduino"]

    if "electronics" in role:
        return ["embedded systems", "verilog", "vhdl", "fpga"]

    if "mechanical" in role:
        return ["cad", "solidworks", "thermodynamics"]

    if "civil" in role:
        return ["autocad", "construction", "structural analysis"]

    if "ai" in role or "ml" in role:
        return ["python", "machine learning", "deep learning", "tensorflow"]

    if "data" in role:
        return ["python", "sql", "data analysis", "pandas"]

    if "web" in role:
        return ["html", "css", "javascript", "react"]

    if "project engineer" in role:
        return ["project management", "coordination", "technical documentation"]

    return ["communication", "teamwork", "problem solving"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("resume")
        role_input = request.form.get("job_desc")

        if not file or not role_input:
            return jsonify({"error": "Upload resume and enter job role"})

        text = extract_text(file)

        if not is_valid_resume(text):
            return jsonify({"error": "This does not look like a resume"})

        expected_skills = get_expected_skills(role_input)

        matched = [s for s in expected_skills if skill_match(s, text)]
        missing = [s for s in expected_skills if s not in matched]

        score = int((len(matched) / len(expected_skills)) * 100)

        # 🎯 feedback
        if score == 0:
            feedback = "No match ❌"
        elif score >= 75:
            feedback = "Excellent match 🎯"
        elif score >= 50:
            feedback = "Good match 👍"
        elif score >= 30:
            feedback = "Average ⚠️"
        else:
            feedback = "Needs improvement ❌"

        # 💡 strength insight
        strength = "Strong" if score >= 70 else "Moderate" if score >= 40 else "Weak"

        return jsonify({
            "score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "feedback": feedback,
            "strength": strength
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)