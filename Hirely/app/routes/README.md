# Routes Directory

This directory contains all Flask route blueprints for the Hirely application.

## Route Modules

### Main Routes (`main.py`)
**Purpose:** Core web interface routes for user and admin interactions

**Routes:**
- `GET /` - Home page with job listings
- `GET /register` - User registration page
- `GET /admin_register` - Admin registration page
- `POST /admin_register` - Handle admin registration
- `GET/POST /login` - User/admin authentication
- `GET /logout` - Logout and session cleanup
- `GET /user_dashboard` - User dashboard with job recommendations
- `GET /admin_dashboard` - Admin dashboard with job management
- `GET/POST /update_profile` - Update user profile and resume
- `GET /profile` - View user profile

**Security:** All dashboard routes use `@secure_route` decorator

---

### Authentication Routes (`auth.py`)
**Purpose:** API endpoints for authentication

**Routes:**
- API authentication endpoints
- Token-based authentication (if implemented)
- Session management APIs

---

### Job Management Routes (`jobs.py`)
**Purpose:** Job posting CRUD operations

**Routes:**
- `GET/POST /post_job` - Create new job posting
- `GET/POST /edit_job/<int:job_id>` - Edit existing job
- `POST /delete_job/<int:job_id>` - Delete/deactivate job
- `GET /view_job/<int:job_id>` - View job details

**Access Control:** 
- Only admins can create/edit/delete jobs
- Each admin can only manage their own jobs

---

### Application Routes (`applications.py`)
**Purpose:** Handle job applications

**Routes:**
- `POST /apply/<int:job_id>` - Submit job application
- `GET /my_applications` - View user's applications
- `GET /applications/<int:job_id>` - View applicants for a job (admin)

**Features:**
- Duplicate application prevention
- Resume text extraction and storage
- Match score calculation

---

### Matchmaking Routes (`matchmaking.py`)
**Purpose:** AI-powered job-resume matching

**Routes:**
- `GET /api/job_matches` - Get job recommendations with match scores
- `GET /api/matchmaking/explain/<int:job_id>` - Get detailed match explanation
- `POST /api/matchmaking/refresh` - Refresh match scores

**Algorithm:**
- BM25 ranking for keyword matching
- Cosine similarity for semantic matching
- Hybrid scoring system

---

### Shortlist Routes (`shortlist.py`)
**Purpose:** Candidate shortlisting for admins

**Routes:**
- `POST /shortlist/add` - Add candidate to shortlist
- `GET /shortlist/<int:job_id>` - View shortlisted candidates
- `DELETE /shortlist/remove/<int:application_id>` - Remove from shortlist

---

## Route Organization

### Security Levels
1. **Public Routes:** `/`, `/register`, `/login`
2. **User Routes:** `/user_dashboard`, `/apply`, `/my_applications`
3. **Admin Routes:** `/admin_dashboard`, `/post_job`, `/edit_job`, `/delete_job`

### Authentication Flow
```
Login → Session Created → @secure_route → Route Handler
                ↓
         Session Timeout Check
                ↓
         CSRF Protection
                ↓
         Cache Prevention
```

## Adding New Routes

To add a new route:

1. **Create the route function:**
   ```python
   @main_bp.route('/new_route')
   @secure_route
   def new_route():
       # Your code here
       return render_template('new_template.html')
   ```

2. **Register in blueprint** (if new blueprint)
3. **Add security decorator** if authentication required
4. **Create corresponding template** in `app/templates/`
5. **Update this README** with route documentation

## Testing Routes

```bash
# Run the application
python main.py

# Test routes with curl
curl http://localhost:5000/
curl -X POST http://localhost:5000/login -d "email=user@test.com&password=pass"
```

## API Response Format

Most API routes return JSON:
```json
{
    "success": true,
    "message": "Operation successful",
    "data": {}
}
```

Or on error:
```json
{
    "success": false,
    "error": "Error message"
}
```
