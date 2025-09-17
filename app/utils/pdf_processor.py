import PyPDF2
import io

def extract_text_from_pdf(file):
    """
    Extract text from a PDF file
    
    Args:
        file: FileStorage object from Flask request
    
    Returns:
        str: Extracted text from the PDF
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")