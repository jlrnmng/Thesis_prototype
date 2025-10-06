from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # 📛 Name fields
    last_name = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80))

    # 📧 Contact
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.Text)

    # 🔒 Security
    password_hash = db.Column(db.String(128))

    # 📄 Resume filename
    resume = db.Column(db.String(255))

    # 👑 Role
    is_admin = db.Column(db.Boolean, default=False)

    # 🕐 Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relationship
    applications = db.relationship('Application', backref='applicant', lazy=True)

    # --- Helpers ---
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    # ----------------------------
    # Serialization helper
    # ----------------------------
    def to_dict(self):
        """Convert user object to dictionary for API responses"""
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
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.full_name} ({self.email})>'

    @property
    def full_name(self):
        """Compose and return the user's full name.

        Format: First Middle Last (middle omitted if not set).
        """
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join([p for p in parts if p])


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cluster_id = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 👤 Link job to the admin who created it
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 🔗 Relationships
    applications = db.relationship('Application', backref='job', lazy=True)
    creator = db.relationship('User', backref='jobs_created', lazy=True)

    def to_dict(self):
        """Convert job object to dictionary for API responses"""
        return {
            "id": self.id,
            "role": self.role,
            "description": self.description,
            "cluster_id": self.cluster_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "creator_name": self.creator.full_name if self.creator else None,
            "application_count": len(self.applications)
        }

    def __repr__(self):
        return f'<Job {self.role} (ID: {self.id})>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    cluster_id = db.Column(db.Integer)
    resume_text = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Add unique constraint to prevent duplicate applications
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_user_job_application'),)

    def to_dict(self):
        """Convert application object to dictionary for API responses"""
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