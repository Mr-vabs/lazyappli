import fitz  # PyMuPDF
import os

def parse_resume(file_path: str) -> str:
    """
    Parses a PDF resume and extracts all text.
    """
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("Only PDF files are currently supported.")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text() + "\n"
    except Exception as e:
        raise RuntimeError(f"Error parsing PDF: {e}")

    return text.strip()
