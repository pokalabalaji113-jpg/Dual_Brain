"""
utils/resume_parser.py
Extract text from uploaded resume PDF, DOCX, or TXT.
"""

import io
import streamlit as st


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract raw text from a PDF using PyMuPDF."""
    try:
        import pymupdf as fitz  # newer package name (pymupdf >= 1.24)
    except ImportError:
        try:
            import fitz  # older import style
        except ImportError:
            st.error("Run in terminal: pip install pymupdf")
            return ""

    try:
        uploaded_file.seek(0)
        data = uploaded_file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        st.error(f"PDF read error: {e}")
        return ""


def extract_text_from_docx(uploaded_file) -> str:
    """Extract text from a .docx file using python-docx."""
    try:
        import docx
    except ImportError:
        st.error("Run in terminal: pip install python-docx")
        return ""

    try:
        uploaded_file.seek(0)
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        return "\n".join([p.text for p in doc.paragraphs]).strip()
    except Exception as e:
        st.error(f"DOCX read error: {e}")
        return ""


def extract_resume_text(uploaded_file) -> str:
    """Route to correct extractor based on file type."""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    elif name.endswith(".txt"):
        uploaded_file.seek(0)
        return uploaded_file.read().decode("utf-8")
    else:
        st.warning("Unsupported file type. Upload PDF, DOCX, or TXT.")
        return ""
