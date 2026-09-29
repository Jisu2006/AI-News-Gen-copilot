from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
    abort
)

from database.db import db
from models.database_models import News, AdminAction

admin = Blueprint("admin", __name__, url_prefix="/admin")


# ==================================================
# ADMIN ACCESS CONTROL
# ==================================================

def check_admin_access():
    """Verify administrator authentication and role."""
    if "user_id" not in session:
        return redirect(url_for("auth.admin_login", next=request.path))
    if session.get("user_role") != "admin":
        flash("Access denied. Administrator privileges required.", "error")
        abort(403)
    return None


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@admin.route("/dashboard")
def dashboard():
    auth_check = check_admin_access()
    if auth_check:
        return auth_check

    pending_news = News.query.filter(
        News.status == "PENDING_REVIEW"
    ).order_by(News.created_at.desc()).all()

    approved_news = News.query.filter(
        News.status == "APPROVED"
    ).order_by(News.updated_at.desc()).all()

    published_news = News.query.filter(
        News.status == "PUBLISHED"
    ).order_by(News.published_at.desc()).all()

    admin_actions = AdminAction.query.order_by(
        AdminAction.created_at.desc()
    ).limit(50).all()

    return render_template(
        "admin/dashboard.html",
        pending_news=pending_news,
        approved_news=approved_news,
        published_news=published_news,
        admin_actions=admin_actions
    )


# ==================================================
# REVIEW NEWS
# ==================================================

@admin.route("/news/<int:news_id>/review", methods=["GET", "POST"])
@admin.route("/review/<int:news_id>", methods=["GET", "POST"])
def review_news(news_id):
    auth_check = check_admin_access()
    if auth_check:
        return auth_check

    news_item = db.get_or_404(News, news_id)

    if request.method == "POST":
        action = request.form.get("action", "").strip().lower()
        comment = request.form.get("comment", "").strip()

        if action == "approve":
            news_item.is_breaking = (request.form.get("is_breaking") == "1")
            news_item.is_featured = (request.form.get("is_featured") == "1")
            news_item.status = "APPROVED"

            admin_action = AdminAction(
                admin_id=session["user_id"],
                news_id=news_item.id,
                action="APPROVED",
                comment=comment or "News draft approved by admin."
            )
            db.session.add(admin_action)
            db.session.commit()

            flash("News approved successfully. It is ready for publication.", "success")
            return redirect(url_for("admin.dashboard"))

        elif action == "request_information":
            if not comment:
                flash("Please enter instructions explaining what additional information is required.", "error")
                return redirect(url_for("admin.review_news", news_id=news_item.id))

            news_item.status = "NEEDS_INFORMATION"
            news_item.admin_comment = comment

            admin_action = AdminAction(
                admin_id=session["user_id"],
                news_id=news_item.id,
                action="REQUEST_INFORMATION",
                comment=comment
            )
            db.session.add(admin_action)
            db.session.commit()

            flash("Additional information requested from user.", "success")
            return redirect(url_for("admin.dashboard"))

        elif action == "reject":
            if not comment:
                flash("Please provide a reason for rejecting this news submission.", "error")
                return redirect(url_for("admin.review_news", news_id=news_item.id))

            news_item.status = "REJECTED"
            news_item.admin_comment = comment

            admin_action = AdminAction(
                admin_id=session["user_id"],
                news_id=news_item.id,
                action="REJECTED",
                comment=comment
            )
            db.session.add(admin_action)
            db.session.commit()

            flash("News submission rejected.", "success")
            return redirect(url_for("admin.dashboard"))

        else:
            flash("Invalid administrator action.", "error")
            return redirect(url_for("admin.review_news", news_id=news_item.id))

    return render_template("admin/review_news.html", news=news_item)


# ==================================================
# EDIT NEWS
# ==================================================

@admin.route("/news/<int:news_id>/edit", methods=["GET", "POST"])
@admin.route("/edit/<int:news_id>", methods=["GET", "POST"])
def edit_news(news_id):
    auth_check = check_admin_access()
    if auth_check:
        return auth_check

    news_item = db.get_or_404(News, news_id)

    if request.method == "POST":
        final_headline = request.form.get("final_headline", "").strip()
        final_subheading = request.form.get("final_subheading", "").strip()
        final_summary = request.form.get("final_summary", "").strip()
        final_article = request.form.get("final_article", "").strip()
        key_facts = request.form.get("key_facts", "").strip()
        tags = request.form.get("tags", "").strip()

        if not final_headline:
            flash("Headline cannot be empty.", "error")
            return redirect(url_for("admin.edit_news", news_id=news_item.id))

        if not final_summary:
            flash("Summary cannot be empty.", "error")
            return redirect(url_for("admin.edit_news", news_id=news_item.id))

        if not final_article:
            flash("Article content cannot be empty.", "error")
            return redirect(url_for("admin.edit_news", news_id=news_item.id))

        news_item.final_headline = final_headline
        news_item.final_subheading = final_subheading
        news_item.final_summary = final_summary
        news_item.final_article = final_article
        news_item.key_facts = key_facts
        news_item.tags = tags
        news_item.is_breaking = (request.form.get("is_breaking") == "1")
        news_item.is_featured = (request.form.get("is_featured") == "1")

        admin_action = AdminAction(
            admin_id=session["user_id"],
            news_id=news_item.id,
            action="EDITED",
            comment="News content edited by administrator."
        )
        db.session.add(admin_action)
        db.session.commit()

        flash("News draft updated successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/edit_news.html", news=news_item)


# ==================================================
# PUBLISH NEWS
# ==================================================

@admin.route("/publish/<int:news_id>", methods=["POST"])
def publish_news(news_id):
    auth_check = check_admin_access()
    if auth_check:
        return auth_check

    news_item = db.get_or_404(News, news_id)

    if news_item.status != "APPROVED":
        flash("Only approved news can be published.", "error")
        return redirect(url_for("admin.dashboard"))

    news_item.status = "PUBLISHED"
    news_item.published_at = datetime.utcnow()

    admin_action = AdminAction(
        admin_id=session["user_id"],
        news_id=news_item.id,
        action="PUBLISHED",
        comment="News published by administrator."
    )
    db.session.add(admin_action)
    db.session.commit()

    flash(f"News '{news_item.final_headline or news_item.ai_headline or news_item.title}' is now published on the newspaper!", "success")
    return redirect(url_for("admin.dashboard"))