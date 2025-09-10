
from typing import Optional
from pdfminer.high_level import extract_text as pdf_extract
from docx import Document

def extract_text(path: str, content_type: Optional[str] = None) -> str:
    if content_type == "application/pdf" or path.lower().endswith(".pdf"):
        return pdf_extract(path)
    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or path.lower().endswith(".docx"):
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file type")
