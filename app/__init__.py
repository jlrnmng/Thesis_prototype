from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sentence_transformers import SentenceTransformer
import joblib
import chromadb
import os
import sys
import logging

# Add the parent directory to the path so we can import from instance
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

db = SQLAlchemy()
model = None
kmeans_model = None
chroma_client = None
jobs_collection = None
logger = logging.getLogger(__name__)

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
    init_ok = False
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Update paths to be relative to the project root
        project_root = os.path.join(os.path.dirname(__file__), '..')
        kmeans_model = joblib.load(os.path.join(project_root, 'data', 'kmeans_model.pkl'))

        # Initialize ChromaDB (Persistent SQLite storage)
        # Import chromadb here so we can optionally disable its telemetry
        import chromadb
        chroma_path = os.path.join(project_root, 'chroma_storage')

        # By default disable Chroma telemetry to avoid telemetry.capture signature
        # mismatches across chromadb releases. Set CHROMA_DISABLE_TELEMETRY=0 to
        # opt back in if you need telemetry.
        try:
            if os.environ.get('CHROMA_DISABLE_TELEMETRY', '1') == '1':
                patched = False
                # Try several known locations for telemetry/capture
                # Try to locate Posthog or other telemetry implementations and
                # replace their capture implementations with permissive no-ops.
                try:
                    import importlib
                    # Verbose flag (set CHROMA_VERBOSE=1 to enable telemetry debug prints)
                    _chroma_verbose = os.environ.get('CHROMA_VERBOSE', '0') == '1'
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

                        # Patch module-level capture
                        if hasattr(mod, 'capture'):
                            try:
                                setattr(mod, 'capture', lambda *a, **kw: None)
                                patched = True
                                logger.debug('Patched capture in module: %s', mod_name)
                            except Exception:
                                pass

                        # Patch client classes that implement capture
                        for attr_name in dir(mod):
                            try:
                                attr = getattr(mod, attr_name)
                            except Exception:
                                continue
                            # Heuristic: classes containing 'Telemetry' or 'Posthog'
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
                else:
                    logger.debug('Could not locate chromadb telemetry to patch; telemetry errors may still appear')
        except Exception as _tele_err:
            # Non-fatal: continue and try to create the client anyway
            logger.debug('Warning: could not patch chromadb telemetry: %s', _tele_err)

        chroma_client = chromadb.PersistentClient(path=chroma_path)
        jobs_collection = chroma_client.get_or_create_collection(name="jobs")

        # Persist chroma_path into app config so post-init checks can create an
        # independent client (avoids relying on module globals which may be
        # overwritten in some import flows).
        app.config['CHROMA_PATH'] = chroma_path
        init_ok = True

    except Exception as e:
        # Detect a common compatibility error: older Chroma DB schema missing 'collections.topic'
        err_str = str(e)
        if 'no such column' in err_str and 'collections.topic' in err_str:
            print("Error loading models: ChromaDB SQLite schema is incompatible (missing 'collections.topic').")
            print("This typically happens when the chroma.sqlite3 file was created by an older/newer chromadb version.")
            print("")
            print("Remediation options:")
            print("  1) Remove or move the existing 'chroma_storage/chroma.sqlite3' so ChromaDB can recreate a fresh DB.")
            print("     - Backup first if you want to preserve the data: copy 'chroma_storage/chroma.sqlite3' to a safe location.")
            print("  2) Use a matching chromadb package version that created the DB (pin the package in your venv).")
            print("")
            # Optionally perform a safe automatic reset if the user opted in via environment variable
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
                        print(f"Backed up existing Chroma DB to: {backup} and removed the original file.")
                        # Retry initialization once
                        chroma_client = chromadb.PersistentClient(path=chroma_path)
                        jobs_collection = chroma_client.get_or_create_collection(name="jobs")
                        print("ChromaDB reset and reinitialized successfully after auto-reset.")
                    else:
                        print("Expected chroma.sqlite3 file not found for auto-reset; nothing to do.")
                else:
                    print("Set environment variable CHROMA_AUTO_RESET=1 to let the app backup+reset the Chroma DB automatically (use with caution).")
            except Exception as ex_auto:
                print(f"Automatic reset attempt failed: {ex_auto}")

        else:
            # Some chromadb Posthog telemetry wrappers raise a benign message
            # about missing kw args; treat that as non-fatal when telemetry is
            # intentionally disabled.
            if 'Posthog.capture' in err_str or 'Posthog.capture:' in err_str or 'Posthog.capture' in err_str:
                logger.debug('Posthog telemetry error encountered and ignored (telemetry disabled).')
            else:
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

    def _run_db_health_checks(app):
        """Return (sql_ok, chroma_ok, ncols) and print success message if both OK."""
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
                # Print a single concise success line when both DBs are connected
                print(f'Databases initialized and connected: SQLAlchemy + ChromaDB ({ncols} collections)')

        return sql_ok, chroma_ok, ncols

    # Post-initialization health checks: only run when init_ok is True
    try:
        if init_ok:
            # Defer to the centralized _run_db_health_checks to avoid duplicate
            # and noisy startup output; that helper will print a single concise
            # success line when both DBs are OK.
            pass
    except Exception:
        # avoid bubbling unexpected errors during final health checks
        pass

    # Run final health checks and print a single concise success line if both OK.
    try:
        _run_db_health_checks(app)
    except Exception:
        pass
    
    return app