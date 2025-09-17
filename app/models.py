from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # 📝 Name fields
    last_name = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80))

    # 📧 Contact
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.Text)

    # 🔑 Security
    password_hash = db.Column(db.String(128))

    # 📄 Resume filename
    resume = db.Column(db.String(255))

    # 👑 Role
    is_admin = db.Column(db.Boolean, default=False)

    # 🕒 Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relationship
    applications = db.relationship('Application', backref='applicant', lazy=True)

    # --- Helpers ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Return full name in 'Last, First Middle' format."""
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.last_name}, {self.first_name}{middle}"

    def to_dict(self):
        return {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "resume": self.resume,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cluster_id = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='job', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "description": self.description,
            "cluster_id": self.cluster_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    cluster_id = db.Column(db.Integer)
    resume_text = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "cluster_id": self.cluster_id,
            "submission_date": self.submission_date.isoformat()
        }
