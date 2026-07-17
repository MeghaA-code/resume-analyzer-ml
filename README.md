# Resume Analyzer — ML-Powered Resume & ATS Insights

A Flask web app that analyzes resumes (PDF/DOCX) using classic NLP + machine
learning: predicts the most likely job category, extracts skills, computes
an ATS (Applicant Tracking System) compatibility score, flags missing
skills, and recommends courses to close the gaps.

## Features

- **Resume upload** — PDF or DOCX, drag-and-drop UI
- **Text extraction** — `pdfplumber`/`pypdf` for PDFs, `python-docx` for Word files
- **NLP preprocessing** — lowercasing, noise removal, stopword filtering (no external corpus downloads)
- **TF-IDF + Logistic Regression** — classifies the resume into one of 10 job categories
- **Skill extraction** — regex-based matching against a curated skill dictionary
- **ATS score** — weighted heuristic covering skill match, section structure, action verbs, quantified achievements, contact info, and resume length
- **Missing skill detection** — compares extracted skills against the ideal set for the predicted category
- **Course recommendations** — suggested resources per missing skill
- **Charts & analytics** — Chart.js gauge, radar, and bar charts on the results page
- **JSON API** — `POST /api/analyze` for programmatic use
- **Deployment-ready** — Procfile, render.yaml, runtime.txt for Render

## Tech Stack

| Layer      | Tech                                             |
|------------|---------------------------------------------------|
| Backend    | Flask, Gunicorn                                    |
| ML/NLP     | scikit-learn (TF-IDF + Logistic Regression), pandas, numpy |
| Parsing    | pdfplumber, pypdf, python-docx                     |
| Frontend   | HTML, Bootstrap 5, Chart.js, vanilla JS             |
| Deployment | Render (free tier)                                 |

## Project Structure

```
resume_analyzer/
├── app.py                     # Flask app & routes
├── train_model.py             # Trains TF-IDF + Logistic Regression, saves to model/
├── generate_dataset.py        # Builds the synthetic training dataset
├── requirements.txt
├── Procfile                   # gunicorn start command (Render)
├── render.yaml                # Render deployment blueprint
├── runtime.txt                # Pinned Python version
├── data/
│   └── resume_dataset.csv     # Generated training data
├── model/
│   ├── resume_classifier.pkl  # Trained Logistic Regression model
│   └── tfidf_vectorizer.pkl   # Fitted TF-IDF vectorizer
├── utils/
│   ├── skills_data.py         # Job categories, skills, courses, ATS reference data
│   ├── text_extraction.py     # PDF/DOCX -> raw text
│   ├── preprocessing.py       # Text cleaning pipeline
│   ├── skill_extractor.py     # Skill detection + matched/missing comparison
│   ├── ats_score.py           # ATS scoring heuristic
│   └── course_recommender.py  # Skill -> course suggestions
├── templates/
│   ├── base.html
│   ├── index.html             # Upload page
│   └── result.html            # Results dashboard with charts
├── static/
│   ├── css/style.css
│   └── js/main.js             # Drag-and-drop upload UX
└── uploads/                   # Temporary storage (files deleted after analysis)
```

## ⚠️ About the Training Data

Real resume datasets are copyrighted and contain PII, so this project trains
on a **synthetic dataset** (`generate_dataset.py`) built by combining
category-specific skills into template sentences — 600 samples across 10
job categories. This is enough to demonstrate the full ML pipeline
end-to-end, but because the synthetic resumes are template-generated, the
model scores ~100% test accuracy — that reflects the synthetic data, not
real-world resume classification difficulty.

**To make this production-grade**, swap in a real, licensed resume dataset
(e.g. from Kaggle, with appropriate usage rights) and retrain — the pipeline
(`train_model.py`) will work unchanged; only `data/resume_dataset.csv`
needs to be replaced with real `category,resume_text` rows.

## Local Setup

```bash
# 1. Clone / unzip the project, then create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the synthetic dataset and train the model
python generate_dataset.py
python train_model.py

# 4. Run the app
python app.py
```

Visit `http://localhost:5000` in your browser.

## Deploying to Render

1. Push this project to a GitHub repository.
2. Go to [render.com](https://render.com) → **New** → **Blueprint**, and point it at your repo (Render will detect `render.yaml` automatically).
   - Alternatively: **New** → **Web Service**, connect the repo, and set:
     - **Build Command:** `pip install -r requirements.txt && python generate_dataset.py && python train_model.py`
     - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
3. Render installs dependencies, regenerates the dataset, and trains the model automatically during the build step (so `model/*.pkl` doesn't need to be committed).
4. Once deployed, your app will be live at `https://<your-service-name>.onrender.com`.

**Free tier note:** Render's free web services spin down after inactivity, so the first request after idle time may take ~30-60 seconds to respond while the instance wakes up.

## Retraining the Model

If you edit `utils/skills_data.py` (add/remove categories or skills), regenerate the dataset and retrain:

```bash
python generate_dataset.py
python train_model.py
```

## API Usage

```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "resume=@/path/to/resume.pdf"
```

Returns a JSON object with `predicted_category`, `confidence`, `ats_score`,
`matched_skills`, `missing_skills`, `course_recommendations`, and more.

## Future Improvements

- Swap in a real, licensed resume dataset for production-grade accuracy
- Add job-description matching (paste a JD, get a tailored match score)
- Support scanned/image-based PDFs via OCR
- User accounts + resume history
- Multi-language resume support

## License

This project is provided as-is for educational/portfolio purposes.

## 🚀 Live Demo

https://resume-analyzer-ml-17uw.onrender.com
