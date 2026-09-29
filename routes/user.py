import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from werkzeug.utils import secure_filename

from config import Config
from database.db import db
from models.database_models import News
from llm.news_generator import generate_news_draft

user = Blueprint("user", __name__, url_prefix="/user")

# ==================================================
# UPLOAD CONFIGURATION
# ==================================================

UPLOAD_FOLDER = Path(Config.UPLOAD_FOLDER)

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp"
}

ALLOWED_VIDEO_EXTENSIONS = {
    "mp4",
    "mov",
    "avi",
    "webm"
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024       # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024      # 100 MB


# ==================================================
# FILE VALIDATION HELPERS
# ==================================================

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def get_file_size(file_storage) -> int:
    """Return uploaded file size in bytes without losing stream position."""
    try:
        current_position = file_storage.stream.tell()
        file_storage.stream.seek(0, 2)
        file_size = file_storage.stream.tell()
        file_storage.stream.seek(current_position)
        return file_size
    except Exception:
        return 0


def generate_unique_filename(filename: str) -> str | None:
    """Generate a sanitized, collision-resistant unique filename."""
    safe_filename = secure_filename(filename)
    if not safe_filename:
        return None
    unique_id = uuid.uuid4().hex
    return f"{unique_id}_{safe_filename}"


def get_requested_fields(admin_comment: str | None) -> dict[str, bool]:
    """Parse admin review comments to detect required update fields."""
    comment = (admin_comment or "").lower()
    requested_fields = {
        "additional_information": False,
        "url": False,
        "image": False,
        "video": False
    }

    url_keywords = ["url", "link", "website", "source"]
    if any(keyword in comment for keyword in url_keywords):
        requested_fields["url"] = True

    image_keywords = ["photo", "image", "picture", "pic"]
    if any(keyword in comment for keyword in image_keywords):
        requested_fields["image"] = True

    video_keywords = ["video", "recording", "footage", "clip"]
    if any(keyword in comment for keyword in video_keywords):
        requested_fields["video"] = True

    info_keywords = [
        "information", "details", "detail", "proof",
        "evidence", "explain", "explanation", "more info",
        "clarify", "clarification"
    ]
    if any(keyword in comment for keyword in info_keywords):
        requested_fields["additional_information"] = True

    # Default to requiring additional information if no specific keyword matched
    if not any(requested_fields.values()):
        requested_fields["additional_information"] = True

    return requested_fields


# ==================================================
# USER DASHBOARD
# ==================================================

@user.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.user_login", next=request.path))

    if session.get("user_role") != "user":
        flash("Administrators have access to the Admin Dashboard.", "error")
        return redirect(url_for("admin.dashboard"))

    user_id = session["user_id"]
    total_submissions = News.query.filter_by(user_id=user_id).count()
    published_count = News.query.filter_by(user_id=user_id, status="PUBLISHED").count()
    pending_count = News.query.filter_by(user_id=user_id, status="PENDING_REVIEW").count()
    needs_info_count = News.query.filter_by(user_id=user_id, status="NEEDS_INFORMATION").count()

    return render_template(
        "user_dashboard.html",
        user_name=session.get("user_name"),
        total_submissions=total_submissions,
        published_count=published_count,
        pending_count=pending_count,
        needs_info_count=needs_info_count
    )


# ==================================================
# MY NEWS
# ==================================================

@user.route("/my-news")
def my_news():
    if "user_id" not in session:
        return redirect(url_for("auth.user_login", next=request.path))

    if session.get("user_role") != "user":
        return redirect(url_for("admin.dashboard"))

    user_news = (
        News.query
        .filter_by(user_id=session["user_id"])
        .order_by(News.created_at.desc())
        .all()
    )

    return render_template("my_news.html", news_list=user_news)


# ==================================================
# SUBMIT NEWS
# ==================================================

@user.route("/submit-news", methods=["GET", "POST"])
def submit_news():
    if "user_id" not in session:
        return redirect(url_for("auth.user_login", next=request.path))

    if session.get("user_role") != "user":
        flash("Administrators manage news from the Admin Dashboard.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        title = request.form.get("title", "").strip()
        location = request.form.get("location", "").strip()
        incident_date = request.form.get("incident_date", "").strip()
        incident_time = request.form.get("incident_time", "").strip()
        bullet_points = request.form.get("bullet_points", "").strip()
        additional_description = request.form.get("additional_description", "").strip()
        source_url = request.form.get("source_url", "").strip()
        supporting_information = request.form.get("supporting_information", "").strip()
        action = request.form.get("action", "draft")

        # Required validation
        if not category or not title or not bullet_points:
            flash("Category, title and bullet points are required.", "error")
            return redirect(url_for("user.submit_news"))

        if len(title) > 255:
            flash("Title must be 255 characters or fewer.", "error")
            return redirect(url_for("user.submit_news"))

        # Date conversion
        parsed_date = None
        if incident_date:
            try:
                parsed_date = datetime.strptime(incident_date, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid incident date format. Please use YYYY-MM-DD.", "error")
                return redirect(url_for("user.submit_news"))

        # Time conversion
        parsed_time = None
        if incident_time:
            for time_fmt in ("%H:%M", "%H:%M:%S"):
                try:
                    parsed_time = datetime.strptime(incident_time, time_fmt).time()
                    break
                except ValueError:
                    continue
            if not parsed_time:
                flash("Invalid incident time format. Please use HH:MM.", "error")
                return redirect(url_for("user.submit_news"))

        # Create upload folder
        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

        image_path = None
        video_path = None

        # Image upload
        image = request.files.get("image")
        if image and image.filename:
            if not allowed_file(image.filename, ALLOWED_IMAGE_EXTENSIONS):
                flash("Invalid image file type. Allowed formats: JPG, JPEG, PNG, GIF, WEBP.", "error")
                return redirect(url_for("user.submit_news"))

            if get_file_size(image) > MAX_IMAGE_SIZE:
                flash("Image file exceeds maximum allowed size of 10 MB.", "error")
                return redirect(url_for("user.submit_news"))

            filename = generate_unique_filename(image.filename)
            if not filename:
                flash("Invalid image filename.", "error")
                return redirect(url_for("user.submit_news"))

            image_path = f"uploads/{filename}"
            image.save(UPLOAD_FOLDER / filename)

        # Video upload
        video = request.files.get("video")
        if video and video.filename:
            if not allowed_file(video.filename, ALLOWED_VIDEO_EXTENSIONS):
                flash("Invalid video file type. Allowed formats: MP4, MOV, AVI, WEBM.", "error")
                return redirect(url_for("user.submit_news"))

            if get_file_size(video) > MAX_VIDEO_SIZE:
                flash("Video file exceeds maximum allowed size of 100 MB.", "error")
                return redirect(url_for("user.submit_news"))

            filename = generate_unique_filename(video.filename)
            if not filename:
                flash("Invalid video filename.", "error")
                return redirect(url_for("user.submit_news"))

            video_path = f"uploads/{filename}"
            video.save(UPLOAD_FOLDER / filename)

        # Determine initial status
        status = "AI_PROCESSING" if action == "submit" else "DRAFT"

        news_record = News(
            user_id=session["user_id"],
            category=category,
            title=title,
            location=location,
            incident_date=parsed_date,
            incident_time=parsed_time,
            bullet_points=bullet_points,
            additional_description=additional_description,
            image_path=image_path,
            video_path=video_path,
            source_url=source_url,
            supporting_information=supporting_information,
            status=status
        )

        db.session.add(news_record)
        db.session.commit()

        if action != "submit":
            flash("News saved as draft successfully.", "success")
            return redirect(url_for("user.my_news"))

        # AI News Generation
        try:
            ai_result = generate_news_draft(news_record)

            news_record.ai_headline = ai_result.get("headline")
            news_record.ai_subheading = ai_result.get("subheading")
            news_record.ai_summary = ai_result.get("summary")
            news_record.ai_article = ai_result.get("article")

            key_facts = ai_result.get("key_facts", [])
            news_record.key_facts = json.dumps(key_facts, ensure_ascii=False) if isinstance(key_facts, list) else str(key_facts)

            tags = ai_result.get("tags", [])
            news_record.tags = json.dumps(tags, ensure_ascii=False) if isinstance(tags, list) else str(tags)

            news_record.status = "PENDING_REVIEW"
            db.session.commit()

            flash("News submitted successfully and AI draft generated. Waiting for admin review.", "success")
        except Exception as error:
            print(f"[AI GENERATION ERROR] News ID {news_record.id}: {error}")
            news_record.status = "AI_PROCESSING_FAILED"
            db.session.commit()
            flash("News was saved, but AI draft generation encountered an issue. You can retry from My News.", "error")

        return redirect(url_for("user.my_news"))

    return render_template("submit_news.html")


# ==================================================
# VIEW SUBMISSION STATUS
# ==================================================

@user.route("/news/<int:news_id>")
def view_news_status(news_id):
    if "user_id" not in session:
        return redirect(url_for("auth.user_login", next=request.path))

    if session.get("user_role") != "user":
        return redirect(url_for("admin.dashboard"))

    news_record = db.get_or_404(News, news_id)
    if news_record.user_id != session["user_id"]:
        flash("You are not authorized to view this submission.", "error")
        return redirect(url_for("user.my_news"))

    return redirect(url_for("user.my_news"))


# ==================================================
# PROVIDE ADDITIONAL INFORMATION
# ==================================================

@user.route("/news/<int:news_id>/provide-info", methods=["GET", "POST"])
@user.route("/provide-information/<int:news_id>", methods=["GET", "POST"])
def provide_information(news_id):
    if "user_id" not in session:
        return redirect(url_for("auth.user_login", next=request.path))

    if session.get("user_role") != "user":
        return redirect(url_for("admin.dashboard"))

    news_record = db.get_or_404(News, news_id)

    if news_record.user_id != session["user_id"]:
        flash("You are not authorized to update this news submission.", "error")
        return redirect(url_for("user.my_news"))

    if news_record.status != "NEEDS_INFORMATION":
        flash("Additional information is not currently requested for this news.", "error")
        return redirect(url_for("user.my_news"))

    requested_fields = get_requested_fields(news_record.admin_comment)

    if request.method == "POST":
        additional_info = request.form.get("additional_information", "").strip()
        new_source_url = request.form.get("source_url", "").strip()

        # Validation based on requested fields
        if requested_fields["additional_information"] and not additional_info:
            flash("Please provide the requested additional information.", "error")
            return redirect(url_for("user.provide_information", news_id=news_record.id))

        if requested_fields["url"] and not new_source_url:
            flash("Please provide the requested source URL.", "error")
            return redirect(url_for("user.provide_information", news_id=news_record.id))

        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

        # Optional or required Image
        image = request.files.get("image")
        if image and image.filename:
            if not allowed_file(image.filename, ALLOWED_IMAGE_EXTENSIONS):
                flash("Invalid image file type.", "error")
                return redirect(url_for("user.provide_information", news_id=news_record.id))

            if get_file_size(image) > MAX_IMAGE_SIZE:
                flash("Image file exceeds maximum allowed size of 10 MB.", "error")
                return redirect(url_for("user.provide_information", news_id=news_record.id))

            filename = generate_unique_filename(image.filename)
            if filename:
                image.save(UPLOAD_FOLDER / filename)
                news_record.image_path = f"uploads/{filename}"
        elif requested_fields["image"] and not news_record.image_path:
            flash("Please upload the requested photo/image.", "error")
            return redirect(url_for("user.provide_information", news_id=news_record.id))

        # Optional or required Video
        video = request.files.get("video")
        if video and video.filename:
            if not allowed_file(video.filename, ALLOWED_VIDEO_EXTENSIONS):
                flash("Invalid video file type.", "error")
                return redirect(url_for("user.provide_information", news_id=news_record.id))

            if get_file_size(video) > MAX_VIDEO_SIZE:
                flash("Video file exceeds maximum allowed size of 100 MB.", "error")
                return redirect(url_for("user.provide_information", news_id=news_record.id))

            filename = generate_unique_filename(video.filename)
            if filename:
                video.save(UPLOAD_FOLDER / filename)
                news_record.video_path = f"uploads/{filename}"
        elif requested_fields["video"] and not news_record.video_path:
            flash("Please upload the requested video.", "error")
            return redirect(url_for("user.provide_information", news_id=news_record.id))

        if new_source_url:
            news_record.source_url = new_source_url

        if additional_info:
            existing = (news_record.supporting_information or "").strip()
            if existing:
                news_record.supporting_information = (
                    f"{existing}\n\n[User Response]:\n{additional_info}"
                )
            else:
                news_record.supporting_information = f"[User Response]:\n{additional_info}"

        news_record.status = "AI_PROCESSING"
        news_record.admin_comment = None
        db.session.commit()

        # Regenerate AI draft
        try:
            ai_result = generate_news_draft(news_record)

            news_record.ai_headline = ai_result.get("headline")
            news_record.ai_subheading = ai_result.get("subheading")
            news_record.ai_summary = ai_result.get("summary")
            news_record.ai_article = ai_result.get("article")

            key_facts = ai_result.get("key_facts", [])
            news_record.key_facts = json.dumps(key_facts, ensure_ascii=False) if isinstance(key_facts, list) else str(key_facts)

            tags = ai_result.get("tags", [])
            news_record.tags = json.dumps(tags, ensure_ascii=False) if isinstance(tags, list) else str(tags)

            news_record.status = "PENDING_REVIEW"
            db.session.commit()

            flash("Additional information submitted and AI draft updated. Sent for admin review.", "success")
        except Exception as error:
            print(f"[AI REGENERATION ERROR] News ID {news_record.id}: {error}")
            news_record.status = "AI_PROCESSING_FAILED"
            db.session.commit()
            flash("Information saved, but AI draft regeneration failed. Please try again later.", "error")

        return redirect(url_for("user.my_news"))

    return render_template(
        "provide_information.html",
        news=news_record,
        requested_fields=requested_fields
    )