from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sentence_transformers import SentenceTransformer
import joblib
import chromadb
import os
import sys

# Add the parent directory to the path so we can import from instance
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

db = SQLAlchemy()
model = None
kmeans_model = None
chroma_client = None
jobs_collection = None

def create_app():
    app = Flask(__name__)
    
    # Load configuration from the Config class
    from instance.config import Config
    app.config.from_object(Config)

    # ✅ Add upload folder config
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Initialize extensions
    db.init_app(app)
    
    # Load ML models (with error handling)
    global model, kmeans_model, chroma_client, jobs_collection
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Update paths to be relative to the project root
        project_root = os.path.join(os.path.dirname(__file__), '..')
        kmeans_model = joblib.load(os.path.join(project_root, 'data', 'kmeans_model.pkl'))
        chroma_client = chromadb.PersistentClient(path=os.path.join(project_root, 'chroma_storage'))
        jobs_collection = chroma_client.get_or_create_collection(name="jobs")
        print("ML models and ChromaDB initialized successfully")
    except Exception as e:
        print(f"Error loading models: {e}")
        # Set to None but allow app to run for testing
        model = None
        kmeans_model = None
        chroma_client = None
        jobs_collection = None
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.jobs import jobs_bp
    from app.routes.applications import applications_bp
    from app.routes.shortlist import shortlist_bp
    from app.routes.matchmaking import matchmaking_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(shortlist_bp, url_prefix='/api/shortlist')
    app.register_blueprint(matchmaking_bp, url_prefix='/api/matchmaking')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
