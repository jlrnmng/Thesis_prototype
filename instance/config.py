import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'resume_matcher.db')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-thesis-only-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{SQLITE_DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # ChromaDB path is relative to Hirely root
    CHROMA_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'chroma_storage'))