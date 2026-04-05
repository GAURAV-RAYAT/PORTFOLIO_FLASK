import fitz  # PyMuPDF
import re
import os
import functools
from langchain_community.document_loaders import PyMuPDFLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@functools.lru_cache(maxsize=1)
def get_beautified_resume():
    """Extract and beautify resume text from PDF (cached for the process lifetime)"""
    pdf_path = os.path.join(BASE_DIR, "static", "assets", "RESUME.pdf")

    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")

        clean_text = re.sub(r'\n+', '\n', full_text)
        clean_text = re.sub(r' +', ' ', clean_text)
        clean_text = clean_text.strip()

        return clean_text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return "Resume data currently unavailable."


@functools.lru_cache(maxsize=1)
def get_trained_context():
    """Load and combine content from multiple PDF files (cached for the process lifetime)"""
    files = [
        os.path.join(BASE_DIR, "static", "assets", "RESUME.pdf"),
        os.path.join(BASE_DIR, "static", "assets", "LINKEDIN_SUMMARY.pdf")
    ]

    all_content = ""
    for file_path in files:
        if os.path.exists(file_path):
            try:
                loader = PyMuPDFLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    all_content += doc.page_content + "\n"
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")

    return all_content
