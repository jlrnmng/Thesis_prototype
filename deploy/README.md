# Deploy Configuration

This directory contains deployment configuration files for the Hirely application.

## Files Overview

### `Procfile`
Heroku/Render deployment process file that defines how to run the application.

```
web: gunicorn wsgi:app
```

- Specifies the web server command using Gunicorn WSGI server
- Points to `wsgi.py` module and the `app` application object

### `wsgi.py`
Web Server Gateway Interface (WSGI) entry point for production deployment.

**Purpose:**
- Provides the application instance for production WSGI servers (Gunicorn, uWSGI)
- Sets up the correct Python path for the Hirely application
- Handles production environment initialization

**Key Components:**
```python
from Hirely.app import create_app
app = create_app()
```

### `render.yaml`
Render.com deployment configuration file (Platform-as-a-Service).

**Typical Configuration:**
- Service type (web service)
- Build command (`pip install -r requirements.txt`)
- Start command (from Procfile)
- Environment variables
- Health check endpoints
- Auto-deploy settings

### `CNAME`
Custom domain configuration file for GitHub Pages or custom domain deployment.

**Contents:** Custom domain name (if applicable)

## Deployment Workflow

### 1. Local Development
```bash
cd Hirely
python main.py
```

### 2. Production Deployment

#### Option A: Render.com
1. Connect GitHub repository to Render
2. Render automatically detects `render.yaml`
3. Deploys using configuration specified in the file

#### Option B: Heroku
```bash
heroku create hirely-app
git push heroku main
```

#### Option C: Manual WSGI Server
```bash
pip install gunicorn
gunicorn wsgi:app --bind 0.0.0.0:8000
```

## Environment Variables Required

The following environment variables should be configured in your deployment platform:

- `FLASK_ENV`: Set to `production`
- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: Database connection string (if using external DB)

## Dependencies

Ensure `requirements.txt` in the root directory includes:
- `gunicorn` - WSGI HTTP Server
- `flask` - Web framework
- All other application dependencies

## Platform-Specific Notes

### Render.com
- Automatically builds from `render.yaml`
- Supports continuous deployment from GitHub
- Free tier available with limitations

### Heroku
- Requires `Procfile` in root directory
- May need `runtime.txt` for Python version specification
- Buildpack auto-detection based on `requirements.txt`

### Traditional VPS (DigitalOcean, AWS EC2, etc.)
- Use `wsgi.py` with Nginx + Gunicorn
- Set up systemd service for process management
- Configure reverse proxy with Nginx

## Testing Deployment Locally

Test the production WSGI setup locally:

```bash
# Install Gunicorn
pip install gunicorn

# Run using WSGI
cd /path/to/Thesis_Prototype
gunicorn deploy.wsgi:app --bind 127.0.0.1:8000

# Access at http://127.0.0.1:8000
```

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure `PYTHONPATH` includes the project root
- Verify `wsgi.py` correctly imports from `Hirely.app`

**Port Binding:**
- Check if the port is already in use
- Ensure firewall rules allow the port

**Static Files Not Loading:**
- Configure static file serving in production
- Consider using CDN or nginx for static assets

**Database Connection:**
- Verify database URL and credentials
- Ensure database is accessible from deployment server

## Security Considerations

1. **Never commit sensitive data:**
   - Use environment variables for secrets
   - Add `.env` to `.gitignore`

2. **HTTPS:**
   - Always use SSL/TLS in production
   - Most platforms (Render, Heroku) provide free SSL

3. **WSGI Server:**
   - Never use Flask development server in production
   - Use production-grade WSGI server (Gunicorn, uWSGI)

## Related Documentation

- [Hirely Application README](../Hirely/README.md)
- [Main Project README](../README.md)
- [Instance Configuration](../Hirely/instance/README.md)

## Deployment Checklist

- [ ] Environment variables configured
- [ ] `requirements.txt` up to date
- [ ] Database migrations applied
- [ ] Static files collected/configured
- [ ] HTTPS enabled
- [ ] Health check endpoint working
- [ ] Logs configured and accessible
- [ ] Backup strategy in place
