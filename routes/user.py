from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from database.db import db
from models.database_models import News
from llm.news_generator import generate_news_draft

from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

import json
import uuid


# ==================================================
# USER BLUEPRINT
# ==================================================

user = Blueprint(
    "user",
    __name__,
    url_prefix="/user"
)


# ==================================================
# UPLOAD CONFIGURATION
# ==================================================

UPLOAD_FOLDER = Path("static/uploads")

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


# Maximum individual file sizes
MAX_IMAGE_SIZE = 10 * 1024 * 1024       # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024      # 100 MB


# ==================================================
# FILE VALIDATION
# ==================================================

def allowed_file(filename, allowed_extensions):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in allowed_extensions
    )


def get_file_size(file):

    """
    Return uploaded file size in bytes
    without permanently changing the stream position.
    """

    try:

        current_position = file.stream.tell()

        file.stream.seek(0, 2)

        file_size = file.stream.tell()

        file.stream.seek(current_position)

        return file_size

    except Exception:

        return 0


def generate_unique_filename(filename):

    """
    Create a secure and unique filename.

    Example:
    photo.jpg
    ->
    8f9c2a7b3e1d4f6a_photo.jpg
    """

    safe_filename = secure_filename(filename)

    if not safe_filename:

        return None

    unique_id = uuid.uuid4().hex

    return f"{unique_id}_{safe_filename}"


# ==================================================
# DETECT REQUIRED INFORMATION FROM ADMIN COMMENT
# ==================================================

def get_requested_fields(admin_comment):

    comment = (admin_comment or "").lower()

    requested_fields = {
        "additional_information": False,
        "url": False,
        "image": False,
        "video": False
    }


    # ----------------------------------------------
    # URL / LINK
    # ----------------------------------------------

    url_keywords = [
        "url",
        "link",
        "website",
        "source"
    ]

    if any(keyword in comment for keyword in url_keywords):

        requested_fields["url"] = True


    # ----------------------------------------------
    # PHOTO / IMAGE
    # ----------------------------------------------

    image_keywords = [
        "photo",
        "image",
        "picture",
        "pic"
    ]

    if any(keyword in comment for keyword in image_keywords):

        requested_fields["image"] = True


    # ----------------------------------------------
    # VIDEO
    # ----------------------------------------------

    video_keywords = [
        "video",
        "recording",
        "footage"
    ]

    if any(keyword in comment for keyword in video_keywords):

        requested_fields["video"] = True


    # ----------------------------------------------
    # ADDITIONAL INFORMATION
    # ----------------------------------------------

    information_keywords = [
        "information",
        "details",
        "detail",
        "proof",
        "evidence",
        "explain",
        "explanation"
    ]

    if any(
        keyword in comment
        for keyword in information_keywords
    ):

        requested_fields["additional_information"] = True


    return requested_fields


# ==================================================
# USER DASHBOARD
# ==================================================

@user.route("/dashboard")
def dashboard():

    # Only normal users can access user dashboard
    if (
        "user_id" not in session
        or session.get("user_role") != "user"
    ):
        return redirect(
            url_for("auth.user_login")
        )

    return render_template(
        "user_dashboard.html",
        user_name=session.get("user_name")
    )
# ==================================================
# MY NEWS
# ==================================================

@user.route("/my-news")
def my_news():

    # ----------------------------------------------
    # User Authentication
    # ----------------------------------------------

    if (
        "user_id" not in session
        or session.get("user_role") != "user"
    ):
        return redirect(
            url_for("auth.user_login")
        )

    # ----------------------------------------------
    # Get Current User's News
    # ----------------------------------------------

    user_news = (
        News.query
        .filter_by(user_id=session["user_id"])
        .order_by(News.created_at.desc())
        .all()
    )

    # ----------------------------------------------
    # Render My News Page
    # ----------------------------------------------

    return render_template(
        "my_news.html",
        news_list=user_news
    )

# ==================================================
# SUBMIT NEWS
# ==================================================

@user.route(
    "/submit-news",
    methods=["GET", "POST"]
)
def submit_news():

    if (
        "user_id" not in session
        or session.get("user_role") != "user"
    ):
        return redirect(
            url_for("auth.user_login")
        )


    if request.method == "POST":

        # ----------------------------------------------
        # GET FORM DATA
        # ----------------------------------------------

        category = request.form.get(
            "category",
            ""
        ).strip()

        title = request.form.get(
            "title",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        incident_date = request.form.get(
            "incident_date",
            ""
        ).strip()

        incident_time = request.form.get(
            "incident_time",
            ""
        ).strip()

        bullet_points = request.form.get(
            "bullet_points",
            ""
        ).strip()

        additional_description = request.form.get(
            "additional_description",
            ""
        ).strip()

        source_url = request.form.get(
            "source_url",
            ""
        ).strip()

        supporting_information = request.form.get(
            "supporting_information",
            ""
        ).strip()

        action = request.form.get(
            "action",
            "draft"
        )


        # ==================================================
        # REQUIRED FIELD VALIDATION
        # ==================================================

        if not category or not title or not bullet_points:

            flash(
                "Category, title and bullet points are required.",
                "error"
            )

            return redirect(
                url_for("user.submit_news")
            )


        # ==================================================
        # DATE CONVERSION
        # ==================================================

        parsed_date = None

        if incident_date:

            try:

                parsed_date = datetime.strptime(
                    incident_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                flash(
                    "Invalid date format.",
                    "error"
                )

                return redirect(
                    url_for("user.submit_news")
                )


        # ==================================================
        # TIME CONVERSION
        # ==================================================

        parsed_time = None

        if incident_time:

            try:

                parsed_time = datetime.strptime(
                    incident_time,
                    "%H:%M"
                ).time()

            except ValueError:

                flash(
                    "Invalid time format.",
                    "error"
                )

                return redirect(
                    url_for("user.submit_news")
                )


        # ==================================================
        # UPLOAD FOLDER
        # ==================================================

        UPLOAD_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )


        image_path = None
        video_path = None


        # ==================================================
        # IMAGE UPLOAD
        # ==================================================

        image = request.files.get("image")

        if image and image.filename:

            # Validate extension

            if not allowed_file(
                image.filename,
                ALLOWED_IMAGE_EXTENSIONS
            ):

                flash(
                    "Invalid image file type.",
                    "error"
                )

                return redirect(
                    url_for("user.submit_news")
                )


            # Validate file size

            image_size = get_file_size(image)

            if image_size > MAX_IMAGE_SIZE:

                flash(
                    "Image file is too large. "
                    "Maximum allowed size is 10 MB.",
                    "error"
                )

                return redirect(
                    url_for("user.submit_news")
                )


            # Generate secure unique filename

            filename = generate_unique_filename(
                image.filename
            )

            if not filename:

                flash(
                    "Invalid image filename.",
                    "error"
                )

                return redirect(
                    url_for("user.submit_news")
                )


            image_path = f"uploads/{filename}"


            image.save(
                UPLOAD_FOLDER / filename
            )


        # ==================================================
        # VIDEO UPLOAD
        # ==================================================

        video = request.files.get("video")

        if video and video.filename:

            # Validate extension

            if not allowed_file(
                video.filename,
                ALLOWED_VIDEO_EXTENSIONS
            ):

                flash(
                    "Invalid video file type.",
                    "error"
                )

                return redirect(
                    url_for("user.submit_news")
                )


            # Validate file size

            video_size = get_file_size(video)

            if video_size > MAX_VIDEO_SIZE:

                flash(
                    "Video file is too large. "
                    "Maximum allowed size is 100 MB.",
                    "error"
                )

                return redirect(
                    url_for("user.submit_news")
                )


            # Generate secure unique filename

            filename = generate_unique_filename(
                video.filename
            )

            if not filename:

                flash(
                    "Invalid video filename.",
                    "error"
                )

                return redirect(
                    url_for("user.submit_news")
                )


            video_path = f"uploads/{filename}"


            video.save(
                UPLOAD_FOLDER / filename
            )


        # ==================================================
        # DETERMINE STATUS
        # ==================================================

        if action == "submit":

            status = "AI_PROCESSING"

        else:

            status = "DRAFT"


        # ==================================================
        # CREATE NEWS
        # ==================================================

        news = News(

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


        db.session.add(news)

        db.session.commit()


        # ==================================================
        # SAVE AS DRAFT
        # ==================================================

        if action != "submit":

            flash(
                "News saved as draft successfully.",
                "success"
            )

            return redirect(
                url_for("user.my_news")
            )


        # ==================================================
        # AI NEWS GENERATION
        # ==================================================

        try:

            print("\n======================================")
            print("AI NEWS GENERATION STARTED")
            print("News ID:", news.id)
            print("======================================\n")


            ai_result = generate_news_draft(news)


            news.ai_headline = ai_result["headline"]

            news.ai_subheading = ai_result["subheading"]

            news.ai_summary = ai_result["summary"]

            news.ai_article = ai_result["article"]


            news.key_facts = json.dumps(
                ai_result["key_facts"],
                ensure_ascii=False
            )


            news.tags = json.dumps(
                ai_result["tags"],
                ensure_ascii=False
            )


            news.status = "PENDING_REVIEW"


            db.session.commit()


            print("\n======================================")
            print("AI NEWS GENERATION SUCCESSFUL")
            print("News ID:", news.id)
            print("Status:", news.status)
            print("======================================\n")


            flash(
                "News submitted successfully and AI draft generated. "
                "It is now waiting for admin review.",
                "success"
            )


        except Exception as error:

            print("\n======================================")
            print("AI NEWS GENERATION FAILED")
            print("News ID:", news.id)
            print("Error:", error)
            print("======================================\n")


            news.status = "AI_PROCESSING_FAILED"

            db.session.commit()


            flash(
                "News was submitted, but AI processing failed. "
                "Please try again later.",
                "error"
            )


        return redirect(
            url_for("user.my_news")
        )


    return render_template(
        "submit_news.html"
    )


# ==================================================
# PROVIDE ADDITIONAL INFORMATION
# ==================================================

@user.route(
    "/provide-information/<int:news_id>",
    methods=["GET", "POST"]
)
def provide_information(news_id):

    # ----------------------------------------------
    # User Authentication + Role Check
    # ----------------------------------------------

    if (
        "user_id" not in session
        or session.get("user_role") != "user"
    ):
        return redirect(
            url_for("auth.user_login")
        )


    # ----------------------------------------------
    # Get News
    # ----------------------------------------------

    news = News.query.get_or_404(news_id)


    # ----------------------------------------------
    # Owner Check
    # ----------------------------------------------

    if news.user_id != session["user_id"]:

        flash(
            "You are not authorized to update this news.",
            "error"
        )

        return redirect(
            url_for("user.my_news")
        )


    # ----------------------------------------------
    # Status Check
    # ----------------------------------------------

    if news.status != "NEEDS_INFORMATION":

        flash(
            "Additional information is not currently requested "
            "for this news.",
            "error"
        )

        return redirect(
            url_for("user.my_news")
        )


    # ----------------------------------------------
    # Detect Required Sections
    # ----------------------------------------------

    requested_fields = get_requested_fields(
        news.admin_comment
    )


    # ==================================================
    # POST REQUEST
    # ==================================================

    if request.method == "POST":

        # ----------------------------------------------
        # Additional Information
        # ----------------------------------------------

        additional_information = request.form.get(
            "additional_information",
            ""
        ).strip()


        # ----------------------------------------------
        # URL
        # ----------------------------------------------

        new_source_url = request.form.get(
            "source_url",
            ""
        ).strip()


        # ----------------------------------------------
        # Validation
        # ----------------------------------------------

        if requested_fields["additional_information"]:

            if not additional_information:

                flash(
                    "Please provide the requested additional information.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


        if requested_fields["url"]:

            if not new_source_url:

                flash(
                    "Please provide the requested source URL.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


        # ----------------------------------------------
        # Upload Folder
        # ----------------------------------------------

        UPLOAD_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )


        # ==================================================
        # IMAGE UPLOAD
        # ==================================================

        if requested_fields["image"]:

            image = request.files.get("image")


            if not image or not image.filename:

                flash(
                    "Please provide the requested photo/image.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


            if not allowed_file(
                image.filename,
                ALLOWED_IMAGE_EXTENSIONS
            ):

                flash(
                    "Invalid image file type.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


            # Validate image size

            image_size = get_file_size(image)

            if image_size > MAX_IMAGE_SIZE:

                flash(
                    "Image file is too large. "
                    "Maximum allowed size is 10 MB.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


            # Generate secure unique filename

            filename = generate_unique_filename(
                image.filename
            )

            if not filename:

                flash(
                    "Invalid image filename.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


            image_path = f"uploads/{filename}"


            image.save(
                UPLOAD_FOLDER / filename
            )


            news.image_path = image_path


        # ==================================================
        # VIDEO UPLOAD
        # ==================================================

        if requested_fields["video"]:

            video = request.files.get("video")


            if not video or not video.filename:

                flash(
                    "Please provide the requested video.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


            if not allowed_file(
                video.filename,
                ALLOWED_VIDEO_EXTENSIONS
            ):

                flash(
                    "Invalid video file type.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


            # Validate video size

            video_size = get_file_size(video)

            if video_size > MAX_VIDEO_SIZE:

                flash(
                    "Video file is too large. "
                    "Maximum allowed size is 100 MB.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


            # Generate secure unique filename

            filename = generate_unique_filename(
                video.filename
            )

            if not filename:

                flash(
                    "Invalid video filename.",
                    "error"
                )

                return redirect(
                    url_for(
                        "user.provide_information",
                        news_id=news.id
                    )
                )


            video_path = f"uploads/{filename}"


            video.save(
                UPLOAD_FOLDER / filename
            )


            news.video_path = video_path


        # ==================================================
        # SAVE URL
        # ==================================================

        if requested_fields["url"]:

            news.source_url = new_source_url


        # ==================================================
        # SAVE ADDITIONAL INFORMATION
        # ==================================================

        if requested_fields["additional_information"]:

            existing_information = (
                news.supporting_information or ""
            ).strip()


            if existing_information:

                news.supporting_information = (
                    existing_information
                    + "\n\n"
                    + "Additional Information provided by user:\n"
                    + additional_information
                )

            else:

                news.supporting_information = (
                    "Additional Information provided by user:\n"
                    + additional_information
                )


        # ==================================================
        # START AI PROCESSING
        # ==================================================

        news.status = "AI_PROCESSING"

        news.admin_comment = None

        db.session.commit()


        # ==================================================
        # REGENERATE AI NEWS DRAFT
        # ==================================================

        try:

            print("\n======================================")
            print("AI NEWS REGENERATION STARTED")
            print("News ID:", news.id)
            print("======================================\n")

            ai_result = generate_news_draft(news)

            # ----------------------------------------------
            # Update AI Content
            # ----------------------------------------------

            news.ai_headline = ai_result["headline"]

            news.ai_subheading = ai_result["subheading"]

            news.ai_summary = ai_result["summary"]

            news.ai_article = ai_result["article"]

            news.key_facts = json.dumps(
                ai_result["key_facts"],
                ensure_ascii=False
            )

            news.tags = json.dumps(
                ai_result["tags"],
                ensure_ascii=False
            )

            # ----------------------------------------------
            # Return to Admin Review
            # ----------------------------------------------

            news.status = "PENDING_REVIEW"

            db.session.commit()

            print("\n======================================")
            print("AI NEWS REGENERATION SUCCESSFUL")
            print("News ID:", news.id)
            print("Status:", news.status)
            print("======================================\n")

            flash(
                "Additional information submitted successfully. "
                "AI draft has been regenerated and the news is "
                "waiting for admin review again.",
                "success"
            )

        except Exception as error:

            print("\n======================================")
            print("AI NEWS REGENERATION FAILED")
            print("News ID:", news.id)
            print("Error:", error)
            print("======================================\n")

            news.status = "AI_PROCESSING_FAILED"

            db.session.commit()

            flash(
                "Additional information was saved, but AI "
                "processing failed. Please try again later.",
                "error"
            )

        return redirect(
            url_for("user.my_news")
        )

    # ==================================================
    # GET REQUEST
    # ==================================================

    return render_template(
        "provide_information.html",
        news=news,
        requested_fields=requested_fields
    )