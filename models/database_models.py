from datetime import datetime
from database.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    # Email verification fields
    is_verified = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    verification_token = db.Column(db.String(255), nullable=True)
    verification_token_expiry = db.Column(db.DateTime, nullable=True)

    # Password reset fields
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # Additional profile fields
    google_id = db.Column(db.String(255), nullable=True)
    mobile_number = db.Column(db.String(20), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    news = db.relationship(
        "News",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    admin_actions = db.relationship(
        "AdminAction",
        backref="admin",
        lazy=True
    )

    comments = db.relationship(
        "NewsComment",
        backref="author",
        lazy=True,
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "NewsLike",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)

    location = db.Column(db.String(255))

    incident_date = db.Column(db.Date)
    incident_time = db.Column(db.Time)

    bullet_points = db.Column(db.Text)
    additional_description = db.Column(db.Text)

    image_path = db.Column(db.String(500))
    video_path = db.Column(db.String(500))

    source_url = db.Column(db.String(500))
    supporting_information = db.Column(db.Text)

    # AI-generated content
    ai_headline = db.Column(db.String(255))
    ai_subheading = db.Column(db.Text)
    ai_summary = db.Column(db.Text)
    ai_article = db.Column(db.Text)
    key_facts = db.Column(db.Text)
    tags = db.Column(db.Text)

    # Admin-edited/published content
    final_headline = db.Column(db.String(255))
    final_subheading = db.Column(db.Text)
    final_summary = db.Column(db.Text)
    final_article = db.Column(db.Text)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="DRAFT"
    )

    admin_comment = db.Column(db.Text)

    is_breaking = db.Column(
        db.Boolean,
        default=False
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    published_at = db.Column(db.DateTime)
    views_count = db.Column(db.Integer, default=0)

    admin_actions = db.relationship(
        "AdminAction",
        backref="news",
        lazy=True,
        cascade="all, delete-orphan"
    )

    comments = db.relationship(
        "NewsComment",
        backref="news",
        lazy=True,
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "NewsLike",
        backref="news",
        lazy=True,
        cascade="all, delete-orphan"
    )


class AdminAction(db.Model):
    __tablename__ = "admin_actions"

    id = db.Column(db.Integer, primary_key=True)

    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    news_id = db.Column(
        db.Integer,
        db.ForeignKey("news.id"),
        nullable=False
    )

    action = db.Column(
        db.String(50),
        nullable=False
    )

    comment = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class OTPVerification(db.Model):
    __tablename__ = "otp_verifications"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, index=True)
    otp_hash = db.Column(db.String(255), nullable=False)
    otp_type = db.Column(db.String(50), default="registration", nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    resend_available_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class NewsComment(db.Model):
    __tablename__ = "news_comments"

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class NewsLike(db.Model):
    __tablename__ = "news_likes"

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)