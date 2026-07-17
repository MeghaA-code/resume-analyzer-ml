"""
app.py
------
Flask backend for the Resume Analyzer.

Routes:
    GET  /            -> upload form (index.html)
    POST /analyze      -> handles resume upload, runs the full analysis
                           pipeline, renders result.html
    GET  /api/health   -> simple health check (used by Render)
    POST /api/analyze  -> JSON API version of /analyze (for programmatic use)

Analysis pipeline (see utils/ for each stage):
    1. Save uploaded file securely, validate extension/size
    2. Extract raw text (PDF/DOCX)                -> text_extraction.py
    3. Preprocess text for the ML model             -> preprocessing.py
    4. Predict job category (TF-IDF + LogReg)        -> this file
    5. Extract skills found in the resume            -> skill_extractor.py
    6. Compare found vs. ideal skills for category    -> skill_extractor.py
    7. Compute ATS compatibility score                -> ats_score.py
    8. Recommend courses for missing skills           -> course_recommender.py
"""

import os
import uuid
import joblib
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from utils.text_extraction import extract_text, TextExtractionError
from utils.preprocessing import preprocess
from utils.skill_extractor import extract_skills, compare_with_category
from utils.ats_score import calculate_ats_score, score_label
from utils.course_recommender import recommend_courses
from utils.skills_data import JOB_CATEGORIES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "model", "resume_classifier.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "tfidf_vectorizer.pkl")

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Load the trained ML model + vectorizer once at startup ---------------
_model = None
_vectorizer = None
_model_load_error = None

try:
    _model = joblib.load(MODEL_PATH)
    _vectorizer = joblib.load(VECTORIZER_PATH)
except Exception as exc:  # noqa: BLE001
    _model_load_error = str(exc)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def predict_category(clean_text: str):
    """Predict job category + per-category confidence scores."""
    vec = _vectorizer.transform([clean_text])
    predicted = _model.predict(vec)[0]
    probabilities = _model.predict_proba(vec)[0]
    confidence_by_category = {
        category: round(float(prob) * 100, 1)
        for category, prob in zip(_model.classes_, probabilities)
    }
    confidence_by_category = dict(
        sorted(confidence_by_category.items(), key=lambda kv: kv[1], reverse=True)
    )
    top_confidence = confidence_by_category[predicted]
    return predicted, top_confidence, confidence_by_category


def run_analysis(raw_text: str) -> dict:
    """Run the full analysis pipeline on extracted resume text and return results."""
    clean = preprocess(raw_text)

    predicted_category, confidence, confidence_by_category = predict_category(clean)

    found_skills = extract_skills(raw_text)
    skill_comparison = compare_with_category(found_skills, predicted_category)

    ats = calculate_ats_score(raw_text, skill_comparison["match_percentage"])
    courses = recommend_courses(skill_comparison["missing_skills"])

    return {
        "predicted_category": predicted_category,
        "confidence": confidence,
        "confidence_by_category": confidence_by_category,
        "found_skills": found_skills,
        "matched_skills": skill_comparison["matched_skills"],
        "missing_skills": skill_comparison["missing_skills"],
        "match_percentage": skill_comparison["match_percentage"],
        "total_required_skills": skill_comparison["total_required"],
        "ats_score": ats["overall_score"],
        "ats_label": score_label(ats["overall_score"]),
        "ats_breakdown": ats["breakdown"],
        "has_bullet_points": ats["has_bullet_points"],
        "course_recommendations": courses,
        "word_count": len(raw_text.split()),
    }


@app.route("/")
def index():
    if _model_load_error:
        flash(
            "The ML model isn't trained yet. Run `python train_model.py` "
            "on the server before analyzing resumes.",
            "warning",
        )
    return render_template("index.html", categories=JOB_CATEGORIES)


@app.route("/analyze", methods=["POST"])
def analyze():
    if _model is None or _vectorizer is None:
        flash("Model not available. Please train the model first (see README).", "danger")
        return redirect(url_for("index"))

    if "resume" not in request.files:
        flash("No file was uploaded.", "danger")
        return redirect(url_for("index"))

    file = request.files["resume"]

    if file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Unsupported file type. Please upload a PDF or DOCX file.", "danger")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(file_path)

    try:
        raw_text = extract_text(file_path)
        results = run_analysis(raw_text)
    except TextExtractionError as exc:
        flash(f"Could not read the resume: {exc}", "danger")
        return redirect(url_for("index"))
    except Exception as exc:  # noqa: BLE001
        flash(f"Something went wrong while analyzing the resume: {exc}", "danger")
        return redirect(url_for("index"))
    finally:
        # Clean up the uploaded file — we don't persist resumes on disk.
        if os.path.exists(file_path):
            os.remove(file_path)

    return render_template("result.html", filename=filename, **results)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """JSON API version of the analysis pipeline."""
    if _model is None or _vectorizer is None:
        return jsonify({"error": "Model not available. Train it first."}), 503

    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded under field name 'resume'."}), 400

    file = request.files["resume"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or unsupported file. Use PDF or DOCX."}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(file_path)

    try:
        raw_text = extract_text(file_path)
        results = run_analysis(raw_text)
    except TextExtractionError as exc:
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify(results)


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": _model is not None,
    })


@app.errorhandler(413)
def file_too_large(_error):
    flash("File is too large. Maximum upload size is 5 MB.", "danger")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("index.html", categories=JOB_CATEGORIES), 404


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
