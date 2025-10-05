from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sentence_transformers import SentenceTransformer
import joblib
import chromadb
import os
import sys
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

db = SQLAlchemy()
model = None
kmeans_model = None
chroma_client = None
jobs_collection = None
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    from instance.config import Config
    app.config.from_object(Config)

    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.config['CHROMA_PATH'] = os.path.join(os.path.dirname(__file__), '..', 'chroma_storage')
    
    db.init_app(app)
    
    global model, kmeans_model, chroma_client, jobs_collection
    init_ok = False
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        project_root = os.path.join(os.path.dirname(__file__), '..')
        kmeans_model = joblib.load(os.path.join(project_root, 'data', 'kmeans_model.pkl'))

        import chromadb
        chroma_path = os.path.join(project_root, 'chroma_storage')

        try:
            if os.environ.get('CHROMA_DISABLE_TELEMETRY', '1') == '1':
                patched = False
                try:
                    import importlib
                    candidates = [
                        'chromadb.telemetry',
                        'chromadb.telemetry.product',
                        'chromadb.telemetry.product.posthog',
                        'chromadb.telemetry.product.posthog_posthog',
                    ]
                    for mod_name in candidates:
                        try:
                            mod = importlib.import_module(mod_name)
                        except Exception:
                            continue

                        if hasattr(mod, 'capture'):
                            try:
                                setattr(mod, 'capture', lambda *a, **kw: None)
                                patched = True
                                logger.debug('Patched capture in module: %s', mod_name)
                            except Exception:
                                pass

                        for attr_name in dir(mod):
                            try:
                                attr = getattr(mod, attr_name)
                            except Exception:
                                continue
                            if isinstance(attr, type) and (('Telemetry' in attr.__name__) or ('Posthog' in attr.__name__) or ('Posthog' in attr_name)):
                                if hasattr(attr, 'capture'):
                                    try:
                                        setattr(attr, 'capture', lambda self, *a, **kw: None)
                                        patched = True
                                        logger.debug('Patched capture on class: %s.%s', mod_name, attr.__name__)
                                    except Exception:
                                        pass
                except Exception as _e:
                    logger.debug('Error while attempting aggressive telemetry patch: %s', _e)

                if patched:
                    logger.debug('ChromaDB telemetry disabled (CHROMA_DISABLE_TELEMETRY=1)')
        except Exception as _tele_err:
            logger.debug('Warning: could not patch chromadb telemetry: %s', _tele_err)

        chroma_client = chromadb.PersistentClient(path=chroma_path)
        jobs_collection = chroma_client.get_or_create_collection(name="jobs")
        app.config['CHROMA_PATH'] = chroma_path
        init_ok = True

    except Exception as e:
        err_str = str(e)
        if 'no such column' in err_str and 'collections.topic' in err_str:
            print("Error loading models: ChromaDB SQLite schema is incompatible (missing 'collections.topic').")
            print("Remediation: Remove 'chroma_storage/chroma.sqlite3' to recreate.")
            try:
                auto_reset = os.environ.get('CHROMA_AUTO_RESET', '0') == '1'
                if auto_reset:
                    sqlite_file = os.path.join(chroma_path, 'chroma.sqlite3')
                    if os.path.exists(sqlite_file):
                        import shutil, datetime
                        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                        backup = sqlite_file + f'.bak.{ts}'
                        shutil.copy2(sqlite_file, backup)
                        os.remove(sqlite_file)
                        print(f"Backed up to: {backup}")
                        chroma_client = chromadb.PersistentClient(path=chroma_path)
                        jobs_collection = chroma_client.get_or_create_collection(name="jobs")
                        print("ChromaDB reset and reinitialized successfully.")
                else:
                    print("Set CHROMA_AUTO_RESET=1 to auto-reset.")
            except Exception as ex_auto:
                print(f"Auto reset failed: {ex_auto}")
        else:
            if 'Posthog.capture' in err_str:
                logger.debug('Posthog telemetry error ignored.')
            else:
                print(f"Error loading models: {e}")

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
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(shortlist_bp, url_prefix='/api/shortlist')
    app.register_blueprint(matchmaking_bp, url_prefix='/api/matchmaking')
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()

    def _run_db_health_checks(app):
        sql_ok = False
        chroma_ok = False
        ncols = 0
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
            sql_ok = True
        except Exception as _sql_err:
            logger.debug('SQLAlchemy health check failed: %s', _sql_err)

        try:
            chroma_path_cfg = app.config.get('CHROMA_PATH')
            if chroma_path_cfg:
                try:
                    chk_client = chromadb.PersistentClient(path=chroma_path_cfg)
                    cols = chk_client.list_collections()
                    if isinstance(cols, (list, tuple)):
                        ncols = len(cols)
                    chroma_ok = True
                except Exception as _c_err:
                    logger.debug('ChromaDB health check failed: %s', _c_err)
        except Exception as _c_err_outer:
            if os.environ.get('CHROMA_VERBOSE', '0') == '1':
                print('ChromaDB health check failed:', _c_err_outer)

        if sql_ok and chroma_ok:
            print(f'Databases initialized OK: SQLAlchemy + ChromaDB ({ncols} collections)')

        return sql_ok, chroma_ok, ncols

    try:
        _run_db_health_checks(app)
    except Exception:
        pass
    
    return app