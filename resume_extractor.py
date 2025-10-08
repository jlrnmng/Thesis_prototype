"""
Utility for extracting text from resume files with NLP preprocessing
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

def extract_resume_text(file_path, preprocess=True):
    """
    Extract text based on file extension with optional preprocessing
    
    Args:
        file_path (str): Path to the resume file
        preprocess (bool): Whether to apply NLP preprocessing
        
    Returns:
        str: Extracted (and optionally preprocessed) resume text
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return ""
    
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Extract raw text based on file type
    if ext == '.pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        raw_text = extract_text_from_docx(file_path)
    elif ext == '.txt':
        raw_text = extract_text_from_txt(file_path)
    else:
        print(f"Unsupported file format: {ext}")
        return ""
    
    # Apply basic cleaning first
    cleaned_text = clean_resume_text(raw_text)
    
    # Apply NLP preprocessing if requested
    if preprocess and cleaned_text:
        try:
            from app.utils.text_preprocessing import preprocess_resume_text
            processed_text = preprocess_resume_text(cleaned_text, for_matching=False)
            print(f"Applied NLP preprocessing to resume text (length: {len(raw_text)} -> {len(processed_text)})")
            return processed_text
        except ImportError:
            print("Warning: Text preprocessing module not available, using basic cleaning only")
            return cleaned_text
        except Exception as e:
            print(f"Warning: Error during text preprocessing: {e}, using basic cleaning only")
            return cleaned_text
    
    return cleaned_text

def clean_resume_text(text):
    """Clean extracted resume text"""
    if not text:
        return ""
    
    text = ' '.join(text.split())
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    return text

def extract_resume_text_for_matching(file_path):
    """
    Extract and preprocess resume text specifically optimized for matching algorithms.
    This version applies aggressive preprocessing for better BM25 and cosine similarity results.
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        str: Preprocessed text optimized for matching
    """
    # First extract the raw text
    raw_text = extract_resume_text(file_path, preprocess=False)
    
    if not raw_text:
        return ""
    
    # Apply matching-optimized preprocessing
    try:
        from app.utils.text_preprocessing import preprocess_resume_text
        processed_text = preprocess_resume_text(raw_text, for_matching=True)
        print(f"Applied matching-optimized preprocessing (length: {len(raw_text)} -> {len(processed_text)})")
        return processed_text
    except ImportError:
        print("Warning: Text preprocessing module not available for matching optimization")
        return clean_resume_text(raw_text)
    except Exception as e:
        print(f"Warning: Error during matching preprocessing: {e}")
        return clean_resume_text(raw_text)