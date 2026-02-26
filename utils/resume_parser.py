import fitz  # PyMuPDF
import re
import os
from langchain_community.document_loaders import PyMuPDFLoader

def get_beautified_resume():
    """Extract and beautify resume text from PDF"""
    pdf_path = "static/assets/RESUME.pdf"
    
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")
        
        # --- Beautification Logic ---
        # 1. Remove excessive newlines
        clean_text = re.sub(r'\n+', '\n', full_text)
        # 2. Remove multiple spaces
        clean_text = re.sub(r' +', ' ', clean_text)
        # 3. Strip whitespace from start/end
        clean_text = clean_text.strip()
        
        return clean_text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return "Resume data currently unavailable."


def get_trained_context():
    """Load and combine content from multiple PDF files"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    files = [
        os.path.join(base_path, "static", "assets", "RESUME.pdf"),
        os.path.join(base_path, "static", "assets", "LINKEDIN_SUMMARY.pdf")
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
