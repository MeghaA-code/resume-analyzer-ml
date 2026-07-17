"""
train_model.py
---------------
Trains the job-category classifier:
    raw resume text -> preprocess -> TF-IDF vectorize -> Logistic Regression

Saves two artifacts to model/:
    tfidf_vectorizer.pkl
    resume_classifier.pkl

Run:
    python generate_dataset.py   # (re)build the synthetic dataset, if needed
    python train_model.py        # train + evaluate + save the model
"""

import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from utils.preprocessing import preprocess
from generate_dataset import build_dataset, save_dataset

DATA_PATH = "data/resume_dataset.csv"
VECTORIZER_PATH = "model/tfidf_vectorizer.pkl"
MODEL_PATH = "model/resume_classifier.pkl"


def load_or_create_dataset() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        print("No dataset found — generating synthetic dataset...")
        rows = build_dataset(samples_per_category=60)
        save_dataset(rows, DATA_PATH)
    return pd.read_csv(DATA_PATH)


def train():
    df = load_or_create_dataset()
    print(f"Loaded {len(df)} resume samples across {df['category'].nunique()} categories.")

    print("Preprocessing text...")
    df["clean_text"] = df["resume_text"].apply(preprocess)

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"], df["category"], test_size=0.2,
        random_state=42, stratify=df["category"],
    )

    print("Vectorizing with TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=3000,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training Logistic Regression classifier...")
    model = LogisticRegression(
        max_iter=1000,
        C=5.0,
        solver="lbfgs",
    )
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest accuracy: {acc:.4f}\n")
    print(classification_report(y_test, y_pred))

    os.makedirs("model", exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved vectorizer -> {VECTORIZER_PATH}")
    print(f"Saved model      -> {MODEL_PATH}")


if __name__ == "__main__":
    train()
