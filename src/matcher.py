from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.lower().strip()

def calculate_match_score(resume_text: str, jd_text: str) -> float:
    """
    Calculates the TF-IDF cosine similarity match score between the resume and job description.
    Returns a percentage from 0.0 to 100.0.
    """
    if not resume_text or not jd_text:
        return 0.0

    r_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    # Use a basic TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')

    try:
        tfidf_matrix = vectorizer.fit_transform([r_clean, jd_clean])
        # Calculate cosine similarity between resume (index 0) and JD (index 1)
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim * 100.0)
    except ValueError:
        # Happens if vocab is empty (e.g., only stop words)
        return 0.0
