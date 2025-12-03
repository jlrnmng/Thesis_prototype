from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    # Database model for users (both job seekers and admins/employers)
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # 📛 Name fields
    last_name = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80))

    # 📧 Contact information
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.Text)

    # 🔒 Security - hashed password
    password_hash = db.Column(db.String(128))

    # 📄 Resume filename (for job seekers)
    resume = db.Column(db.String(255))

    # 👑 Role - True for admin/employer, False for job seeker
    is_admin = db.Column(db.Boolean, default=False)

    # 🏢 Company info (for admins/employers only)
    company_name = db.Column(db.String(200))
    company_address = db.Column(db.Text)

    # 🕐 Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relationship - applications submitted by this user
    applications = db.relationship('Application', backref='applicant', lazy=True)

    # --- Helpers ---
    def set_password(self, password):
        # Hash and set password using werkzeug security
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Check if provided password matches stored hash
        return check_password_hash(self.password_hash, password)

    # ----------------------------
    # Serialization helper
    # ----------------------------
    def to_dict(self):
        # Convert user object to dictionary for API responses
        return {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "resume": self.resume,
            "is_admin": self.is_admin,
            "company_name": self.company_name,
            "company_address": self.company_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.full_name} ({self.email})>'

    @property
    def full_name(self):
        # Compose user's full name: First Middle Last (middle omitted if not set)
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join([p for p in parts if p])


class Job(db.Model):
    # Database model for job postings
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)  # Job title
    description = db.Column(db.Text, nullable=False)  # Job description
    cluster_id = db.Column(db.Integer)  # K-means cluster category
    is_active = db.Column(db.Boolean, default=True)  # Active/inactive status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 👤 Link job to the admin who created it
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 🔗 Relationships
    applications = db.relationship('Application', backref='job', lazy=True)  # Applications for this job
    creator = db.relationship('User', backref='jobs_created', lazy=True)  # Admin who posted job

    def to_dict(self):
        # Convert job object to dictionary for API responses
        return {
            "id": self.id,
            "role": self.role,
            "description": self.description,
            "cluster_id": self.cluster_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "creator_name": self.creator.full_name if self.creator else None,
            "company_name": self.creator.company_name if self.creator else None,
            "application_count": len(self.applications)
        }

    def __repr__(self):
        return f'<Job {self.role} (ID: {self.id})>'


class Application(db.Model):
    # Database model for job applications (links users to jobs)
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Applicant
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)  # Job applied to
    cluster_id = db.Column(db.Integer)  # Predicted cluster for resume
    resume_text = db.Column(db.Text, nullable=False)  # Extracted resume text
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Prevent duplicate applications (same user can't apply to same job twice)
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_user_job_application'),)

    def to_dict(self):
        # Convert application object to dictionary for API responses
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "cluster_id": self.cluster_id,
            "submission_date": self.submission_date.isoformat() if self.submission_date else None,
            "applicant_name": self.applicant.full_name if self.applicant else None,
            "job_role": self.job.role if self.job else None
        }

    def __repr__(self):
        return f'<Application {self.id}: User {self.user_id} -> Job {self.job_id}>'