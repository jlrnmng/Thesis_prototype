"""Wrapper resume extractor for package imports.

This module provides `extract_resume_text(path)` and centralizes
fallback logic so other modules can reliably import from
`app.utils.resume_extractor`.
"""
import os
import traceback

# Try to import top-level extractor if present (for backwards compatibility)
try:
    # top-level module at project root
    from resume_extractor import extract_resume_text as _top_extract
    def extract_resume_text(path: str, preprocess: bool = True) -> str:
        # Use top-level resume extractor from project root
        try:
            return _top_extract(path, preprocess=preprocess)
        except Exception:
            traceback.print_exc()
            return ""
except Exception:
    # Fallback to pdf processor if top-level extractor not available
    try:
        from .pdf_processor import extract_text_from_pdf

        def extract_resume_text(path: str, preprocess: bool = True) -> str:
            # Fallback extractor - extracts text from PDF files using pdf_processor
            # Returns empty string if file doesn't exist or format unsupported
            if not os.path.exists(path):
                print(f"Resume extractor fallback: file not found: {path}")
                return ""

            # Check file extension
            _, ext = os.path.splitext(path)
            ext = ext.lower()
            if ext == '.pdf':
                try:
                    # Extract text from PDF
                    return extract_text_from_pdf(open(path, 'rb'))
                except Exception as e:
                    print(f"Error extracting PDF via fallback extractor: {e}")
                    traceback.print_exc()
                    return ""
            else:
                # Other formats not supported by fallback
                print(f"Resume extractor fallback: unsupported format {ext}")
                return ""

    except Exception:
        # As a last resort provide a no-op extractor
        def extract_resume_text(path: str, preprocess: bool = True) -> str:
            # Final fallback - no extractor available
            print("No resume extractor available (final fallback)")
            return ""
