import os
import sys
import sqlite3
from sqlalchemy import text
from flask import render_template, request, session, redirect
from app import create_app, db  # Import your factory + db
import logging
import warnings

# Ensure parent dir is importable
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Disable oneDNN optimizations for TF
import importlib.util
# Only set TensorFlow-related environment variables if TensorFlow is present
if importlib.util.find_spec('tensorflow') is not None:
    # Disable oneDNN optimizations for TF (optional safety)
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    # Reduce TensorFlow logging of INFO/WARNING messages (optional)
    # 0 = all logs, 1 = filter INFO, 2 = filter WARNING, 3 = filter ERROR
    os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')
    # Also set Python logging to suppress TF/absl warnings originating from
    # Python logging (these suppress the 'WARNING:tensorflow:From ...' lines).
    logging.getLogger('tensorflow').setLevel(logging.ERROR)
    logging.getLogger('absl').setLevel(logging.ERROR)
    # Silence DeprecationWarning coming from TensorFlow modules
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='tensorflow')

# Create Flask app instance
app = create_app()

# Initialize database tables if not created
with app.app_context():
    db.create_all()


# -------------------------------
# Health check for DBs
# -------------------------------
def check_databases(app):
    """Check SQLAlchemy + ChromaDB connectivity status."""
    sql_ok = False
    chroma_ok = False
    ncols = 0

    # SQLAlchemy check
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
        sql_ok = True
    except Exception as e:
        print('SQLAlchemy connection: FAIL ->', e)

    # ChromaDB check
    try:
        chroma_path = app.config.get('CHROMA_PATH')
        if not chroma_path:
            project_root = os.path.dirname(os.path.abspath(__file__))
            candidates = [
                os.path.join(project_root, 'chroma_storage'),
                os.path.join(project_root, '..', 'chroma_storage'),
                os.path.join(project_root, '..', '..', 'chroma_storage'),
            ]
            for c in candidates:
                if os.path.exists(c):
                    chroma_path = c
                    break

        if not chroma_path:
            print('ChromaDB connection: SKIPPED (no path)')
        else:
            sqlite_file = os.path.join(chroma_path, 'chroma.sqlite3')
            if not os.path.exists(sqlite_file):
                print(f"ChromaDB connection: SKIPPED (file not found at {sqlite_file})")
            else:
                try:
                    conn = sqlite3.connect(sqlite_file)
                    cur = conn.cursor()
                    cur.execute("PRAGMA table_info('collections')")
                    cols = cur.fetchall()
                    if not cols:
                        print("ChromaDB connection: FAIL -> 'collections' table missing")
                    else:
                        try:
                            cur.execute('SELECT COUNT(*) FROM collections')
                            ncols = cur.fetchone()[0]
                        except Exception:
                            ncols = -1
                        chroma_ok = True
                    conn.close()
                except Exception as e:
                    print('ChromaDB connection: FAIL ->', e)
    except Exception as e:
        print('ChromaDB connection: FAIL ->', e)

    # Final concise status
    if sql_ok and chroma_ok:
        print(f'Databases initialized OK: SQLAlchemy + ChromaDB ({ncols} collections)')
    else:
        if not sql_ok:
            print('Databases status: SQLAlchemy NOT CONNECTED')
        if not chroma_ok:
            print('Databases status: ChromaDB NOT CONNECTED')


# -------------------------------
# Routes
# -------------------------------
from app.models import Job


@app.route('/')
def index():
    jobs = db.session.query(Job).all()
    return render_template('index.html', jobs=jobs)


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/admin_register')
def register_admin():
    return render_template('admin_register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"User tried to login: {username} | {password}")
        return redirect('/apply')
    return render_template('login.html')


@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/login")
    return redirect("/admin_dashboard" if session["role"] == "admin" else "/user_dashboard")


@app.route("/user_dashboard")
def user_dashboard():
    if "role" not in session or session["role"] != "user":
        return redirect("/login")
    return render_template("dashboard_user.html")


@app.route("/admin_dashboard")
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        return redirect("/login")
    return render_template("dashboard_admin.html")


@app.route('/apply')
def apply_page():
    return "<h1>Welcome! You are logged in.</h1>"


# -------------------------------
# Main entry
# -------------------------------
if __name__ == '__main__':
    with app.app_context():
        print("\n=== Registered Routes ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint:30s} -> {rule}")

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Run DB health check
    try:
        check_databases(app)
    except Exception:
        pass

    # Start server
    app.run(debug=True, host='0.0.0.0', port=5000)
