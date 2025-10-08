"""
Natural Language Preprocessing Utilities for Resume Text

This module provides comprehensive text preprocessing functions to improve
matching accuracy and consistency in the resume processing pipeline.
"""
import re
import string
from typing import Optional


class ResumeTextPreprocessor:
    """
    A comprehensive text preprocessor for resume content that standardizes
    text format while preserving meaningful information for matching algorithms.
    """
    
    def __init__(self):
        # Common stop words that don't add value to matching but preserve important keywords
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with'
        }
        
        # Skills and technical terms that should be preserved exactly
        self.preserve_terms = {
            'c++', 'c#', '.net', 'javascript', 'typescript', 'react.js', 'node.js',
            'vue.js', 'angular.js', 'asp.net', 'sql', 'mysql', 'postgresql',
            'mongodb', 'nosql', 'api', 'rest', 'restful', 'graphql', 'json',
            'xml', 'html', 'css', 'sass', 'scss', 'bootstrap', 'tailwind',
            'git', 'github', 'gitlab', 'docker', 'kubernetes', 'aws', 'azure',
            'gcp', 'linux', 'unix', 'windows', 'macos', 'ios', 'android',
            'python', 'java', 'kotlin', 'swift', 'golang', 'rust', 'php',
            'ruby', 'scala', 'r', 'matlab', 'sas', 'spss', 'tableau',
            'powerbi', 'excel', 'word', 'powerpoint', 'photoshop', 'illustrator',
            'figma', 'sketch', 'adobe', 'autocad', 'solidworks', 'catia'
        }
        
        # Degree abbreviations and certifications
        self.degree_patterns = {
            'bachelor': ['bachelor', 'bachelors', 'ba', 'bs', 'bsc', 'beng', 'btech'],
            'master': ['master', 'masters', 'ma', 'ms', 'msc', 'meng', 'mtech', 'mba'],
            'phd': ['phd', 'ph.d', 'doctorate', 'doctoral']
        }
    
    def preprocess_text(self, text: str, preserve_structure: bool = True) -> str:
        """
        Apply comprehensive preprocessing to resume text.
        
        Args:
            text (str): Raw resume text
            preserve_structure (bool): Whether to preserve some formatting structure
            
        Returns:
            str: Preprocessed text ready for matching algorithms
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Step 1: Basic cleaning
        text = self._basic_clean(text)
        
        # Step 2: Normalize whitespace and structure
        text = self._normalize_structure(text, preserve_structure)
        
        # Step 3: Standardize technical terms and skills
        text = self._standardize_technical_terms(text)
        
        # Step 4: Normalize education terms
        text = self._normalize_education_terms(text)
        
        # Step 5: Handle special characters and punctuation
        text = self._handle_special_characters(text)
        
        # Step 6: Final cleanup
        text = self._final_cleanup(text)
        
        return text.strip()
    
    def _basic_clean(self, text: str) -> str:
        """Remove unnecessary characters and artifacts from PDF/Word extraction."""
        # Remove common PDF extraction artifacts
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219]', '•', text)  # Normalize bullet points
        text = re.sub(r'[\u2013\u2014]', '-', text)  # Normalize dashes
        text = re.sub(r'[\u2018\u2019]', "'", text)  # Normalize single quotes
        text = re.sub(r'[\u201C\u201D]', '"', text)  # Normalize double quotes
        
        # Remove excessive spacing and non-printable characters
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Remove email addresses (keep @ symbol but remove full emails for privacy)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove phone numbers
        text = re.sub(r'[\+]?[1-9]?[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}', '[PHONE]', text)
        text = re.sub(r'\([0-9]{3}\)[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}', '[PHONE]', text)
        
        return text
    
    def _normalize_structure(self, text: str, preserve_structure: bool) -> str:
        """Normalize text structure while preserving important formatting."""
        if preserve_structure:
            # Normalize line breaks but preserve paragraph structure
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
            text = re.sub(r'\n\s+', '\n', text)  # Remove leading spaces on lines
            text = re.sub(r'[ \t]+', ' ', text)  # Normalize horizontal whitespace
        else:
            # Convert to single line with normalized spacing
            text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _standardize_technical_terms(self, text: str) -> str:
        """Standardize technical terms and programming languages."""
        # Convert to lowercase first for processing
        text_lower = text.lower()
        
        # Preserve important technical terms in their standard format
        for term in self.preserve_terms:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term.lower()) + r'\b'
            text_lower = re.sub(pattern, term, text_lower, flags=re.IGNORECASE)
        
        # Standardize common variations
        standardizations = {
            r'\bjavascript\b': 'JavaScript',
            r'\btypescript\b': 'TypeScript',
            r'\breact\.?js\b': 'React.js',
            r'\bnode\.?js\b': 'Node.js',
            r'\bvue\.?js\b': 'Vue.js',
            r'\bangular\.?js\b': 'Angular.js',
            r'\basp\.?net\b': 'ASP.NET',
            r'\bc\+\+\b': 'C++',
            r'\bc#\b': 'C#',
            r'\b\.net\b': '.NET',
            r'\bmysql\b': 'MySQL',
            r'\bpostgresql\b': 'PostgreSQL',
            r'\bmongodb\b': 'MongoDB',
            r'\bnosql\b': 'NoSQL',
            r'\brestful\b': 'RESTful',
            r'\bgraphql\b': 'GraphQL',
            r'\bgithub\b': 'GitHub',
            r'\bgitlab\b': 'GitLab',
            r'\bpowerbi\b': 'PowerBI'
        }
        
        for pattern, replacement in standardizations.items():
            text_lower = re.sub(pattern, replacement, text_lower, flags=re.IGNORECASE)
        
        return text_lower
    
    def _normalize_education_terms(self, text: str) -> str:
        """Normalize education-related terms and degrees."""
        # Normalize degree terms
        for standard, variations in self.degree_patterns.items():
            for variation in variations:
                pattern = r'\b' + re.escape(variation) + r'\b'
                text = re.sub(pattern, standard, text, flags=re.IGNORECASE)
        
        # Standardize common educational terms
        edu_standardizations = {
            r'\buniversity\b': 'university',
            r'\bcollege\b': 'college',
            r'\binstitute\b': 'institute',
            r'\bcertificat(e|ion)\b': 'certification',
            r'\bgpa\b': 'GPA',
            r'\bcum laude\b': 'cum laude',
            r'\bmagna cum laude\b': 'magna cum laude',
            r'\bsumma cum laude\b': 'summa cum laude'
        }
        
        for pattern, replacement in edu_standardizations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _handle_special_characters(self, text: str) -> str:
        """Handle special characters and punctuation consistently."""
        # Normalize punctuation that doesn't add semantic value
        text = re.sub(r'[•·▪▫‣⁃]', '•', text)  # Standardize bullets
        text = re.sub(r'[–—―]', '-', text)  # Standardize dashes
        
        # Remove excessive punctuation but preserve important ones
        text = re.sub(r'\.{2,}', '.', text)  # Multiple periods to single
        text = re.sub(r'\!{2,}', '!', text)  # Multiple exclamations to single
        text = re.sub(r'\?{2,}', '?', text)  # Multiple questions to single
        
        # Remove standalone special characters that don't add value
        text = re.sub(r'\s[^\w\s]\s', ' ', text)
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup and normalization."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Ensure proper spacing around punctuation
        text = re.sub(r'\s*([,.;:!?])\s*', r'\1 ', text)
        text = re.sub(r'\s*([()])\s*', r' \1 ', text)
        
        # Final whitespace cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def preprocess_for_matching(self, text: str) -> str:
        """
        Specialized preprocessing for matching algorithms.
        This version is optimized for BM25 and cosine similarity.
        """
        # Use standard preprocessing
        text = self.preprocess_text(text, preserve_structure=False)
        
        # Additional processing for matching
        # Convert to lowercase for consistent matching
        text = text.lower()
        
        # Remove common punctuation that doesn't help matching
        text = re.sub(r'[^\w\s.-]', ' ', text)
        
        # Normalize numbers and years
        text = re.sub(r'\b\d{4}\b', 'YEAR', text)  # Years
        text = re.sub(r'\b\d+\+?\b', 'NUMBER', text)  # Numbers and "5+" type patterns
        
        # Final cleanup
        text = ' '.join(text.split())
        
        return text


# Global preprocessor instance
_preprocessor = None

def get_preprocessor() -> ResumeTextPreprocessor:
    """Get or create a global preprocessor instance."""
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = ResumeTextPreprocessor()
    return _preprocessor

def preprocess_resume_text(text: str, for_matching: bool = False) -> str:
    """
    Convenience function for preprocessing resume text.
    
    Args:
        text (str): Raw resume text
        for_matching (bool): Whether to optimize for matching algorithms
        
    Returns:
        str: Preprocessed text
    """
    preprocessor = get_preprocessor()
    if for_matching:
        return preprocessor.preprocess_for_matching(text)
    else:
        return preprocessor.preprocess_text(text)