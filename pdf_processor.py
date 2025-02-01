import fitz
import re
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"

    text = re.sub(r"\s+", " ", text)
    return text.strip()
