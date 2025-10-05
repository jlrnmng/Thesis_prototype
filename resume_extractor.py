"""
Utility for extracting text from resume files
"""
import os
import PyPDF2
import docx
import mammoth

def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        try:
            with open(file_path, "rb") as file:
                result = mammoth.extract_raw_text(file)
                return result.value.strip()
        except Exception as e2:
            print(f"Error extracting text from DOCX with mammoth: {e2}")
            return ""

def extract_text_from_txt(file_path):
    """Extract text from TXT"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return ""
    except Exception as e:
        print(f"Error extracting text from TXT: {e}")
        return ""

def extract_resume_text(file_path):
    """Extract text based on file extension"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return ""
    
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        print(f"Unsupported file format: {ext}")
        return ""

def clean_resume_text(text):
    """Clean extracted resume text"""
    if not text:
        return ""
    
    text = ' '.join(text.split())
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    return text