#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p instance/uploads
mkdir -p chroma_storage
mkdir -p data

# Run database initialization
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Start the application with Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 run:app