"""
preprocessing.py
-----------------
Lightweight text preprocessing for resume text, built with only the
standard library + regex so the app has zero heavyweight NLP dependencies
(no NLTK corpus downloads needed, which keeps Render deployments simple).

Pipeline:
  raw text -> lowercase -> strip emails/urls/phone numbers
           -> remove punctuation/digits -> remove stopwords -> tokens
"""

import re

# A compact English stopword list (kept local instead of NLTK's corpus
# so the project has no external data download requirement at deploy time).
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can",
    "could", "did", "do", "does", "doing", "down", "during", "each", "few",
    "for", "from", "further", "had", "has", "have", "having", "he", "her",
    "here", "hers", "herself", "him", "himself", "his", "how", "i", "if",
    "in", "into", "is", "it", "its", "itself", "just", "me", "more",
    "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on",
    "once", "only", "or", "other", "our", "ours", "ourselves", "out",
    "over", "own", "same", "she", "should", "so", "some", "such", "than",
    "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "we", "were", "what", "when",
    "where", "which", "while", "who", "whom", "why", "will", "with",
    "you", "your", "yours", "yourself", "yourselves",
}

EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
URL_RE = re.compile(r"http\S+|www\.\S+")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s()]{7,}\d)")
NON_ALPHA_RE = re.compile(r"[^a-z\s+#.]")
MULTI_SPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Normalize raw resume text: lowercase, strip PII-ish noise & punctuation."""
    text = text.lower()
    text = EMAIL_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    text = PHONE_RE.sub(" ", text)
    # keep +, #, . so tokens like "c++", "c#", "node.js" survive
    text = NON_ALPHA_RE.sub(" ", text)
    text = MULTI_SPACE_RE.sub(" ", text).strip()
    return text


def tokenize(text: str) -> list:
    """Split cleaned text into tokens."""
    return text.split()


def remove_stopwords(tokens: list) -> list:
    """Filter out common English stopwords."""
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def preprocess(text: str) -> str:
    """
    Full pipeline: clean -> tokenize -> remove stopwords -> rejoin.
    Returns a single space-joined string, ready for TF-IDF vectorization.
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    return " ".join(tokens)
