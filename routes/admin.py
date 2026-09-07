from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash
)

from database.db import db
from models.database_models import News, AdminAction

from datetime import datetime


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ==================================================
# ADMIN AUTHENTICATION CHECK
# ==================================================

def is_admin():

    return (
        "user_id" in session
        and session.get("user_role") == "admin"
    )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@admin.route("/dashboard")
def dashboard():

    if not is_admin():
        return redirect(
            url_for("auth.admin_login")
        )


    # ----------------------------------------------
    # Pending Review News
    # ----------------------------------------------

    pending_news = News.query.filter(
        News.status == "PENDING_REVIEW"
    ).order_by(
        News.created_at.desc()
    ).all()


    # ----------------------------------------------
    # Approved News
    # ----------------------------------------------

    approved_news = News.query.filter(
        News.status == "APPROVED"
    ).order_by(
        News.updated_at.desc()
    ).all()


    # ----------------------------------------------
    # Published News
    # ----------------------------------------------

    published_news = News.query.filter(
        News.status == "PUBLISHED"
    ).order_by(
        News.published_at.desc()
    ).all()


    # ==================================================
    # AUDIT TRAIL
    # ==================================================

    admin_actions = AdminAction.query.order_by(
        AdminAction.created_at.desc()
    ).all()


    # ==================================================
    # SEND DATA TO DASHBOARD
    # ==================================================

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

@admin.route(
    "/review/<int:news_id>",
    methods=["GET", "POST"]
)
def review_news(news_id):

    if not is_admin():
        return redirect(
            url_for("auth.admin_login")
        )


    news = News.query.get_or_404(news_id)


    # ----------------------------------------------
    # Only Pending News Can Be Reviewed
    # ----------------------------------------------

    if news.status != "PENDING_REVIEW":

        flash(
            "This news is not currently waiting for review.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ==================================================
    # POST REQUEST
    # ==================================================

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        ).strip().lower()


        comment = request.form.get(
            "comment",
            ""
        ).strip()


        # ==================================================
        # APPROVE NEWS
        # ==================================================

        if action == "approve":

            # Save Breaking News option

            news.is_breaking = (
                request.form.get("is_breaking") == "1"
            )


            # Save Featured News option

            news.is_featured = (
                request.form.get("is_featured") == "1"
            )


            # Change status

            news.status = "APPROVED"


            # Create Admin Action

            admin_action = AdminAction(

                admin_id=session["user_id"],

                news_id=news.id,

                action="APPROVED",

                comment=comment

            )


            db.session.add(admin_action)

            db.session.commit()


            flash(
                "News approved successfully. "
                "It is now ready for publishing.",
                "success"
            )


        # ==================================================
        # REQUEST ADDITIONAL INFORMATION
        # ==================================================

        elif action == "request_information":

            if not comment:

                flash(
                    "Please provide a comment explaining "
                    "what information is required.",
                    "error"
                )

                return redirect(
                    url_for(
                        "admin.review_news",
                        news_id=news.id
                    )
                )


            news.status = "NEEDS_INFORMATION"

            news.admin_comment = comment


            # Create Admin Action

            admin_action = AdminAction(

                admin_id=session["user_id"],

                news_id=news.id,

                action="REQUEST_INFORMATION",

                comment=comment

            )


            db.session.add(admin_action)

            db.session.commit()


            flash(
                "Additional information requested from the user.",
                "success"
            )


        # ==================================================
        # REJECT NEWS
        # ==================================================

        elif action == "reject":

            if not comment:

                flash(
                    "Please provide a reason for rejection.",
                    "error"
                )

                return redirect(
                    url_for(
                        "admin.review_news",
                        news_id=news.id
                    )
                )


            news.status = "REJECTED"

            news.admin_comment = comment


            # Create Admin Action

            admin_action = AdminAction(

                admin_id=session["user_id"],

                news_id=news.id,

                action="REJECTED",

                comment=comment

            )


            db.session.add(admin_action)

            db.session.commit()


            flash(
                "News rejected successfully.",
                "success"
            )


        # ==================================================
        # INVALID ACTION
        # ==================================================

        else:

            flash(
                "Invalid admin action.",
                "error"
            )

            return redirect(
                url_for(
                    "admin.review_news",
                    news_id=news.id
                )
            )


        # After action → Admin Dashboard

        return redirect(
            url_for("admin.dashboard")
        )


    # ==================================================
    # SHOW REVIEW PAGE
    # ==================================================

    return render_template(
        "admin/review_news.html",
        news=news
    )


# ==================================================
# EDIT NEWS
# ==================================================

@admin.route(
    "/edit/<int:news_id>",
    methods=["GET", "POST"]
)
def edit_news(news_id):

    # ----------------------------------------------
    # Admin Authentication
    # ----------------------------------------------

    if not is_admin():
        return redirect(
            url_for("auth.admin_login")
        )


    # ----------------------------------------------
    # Get News
    # ----------------------------------------------

    news = News.query.get_or_404(news_id)


    # ----------------------------------------------
    # Only PENDING_REVIEW and APPROVED News
    # Can Be Edited
    # ----------------------------------------------

    if news.status not in [
        "PENDING_REVIEW",
        "APPROVED"
    ]:

        flash(
            "Only pending or approved news can be edited.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ==================================================
    # POST REQUEST
    # ==================================================

    if request.method == "POST":

        # ----------------------------------------------
        # Get Edited Values
        # ----------------------------------------------

        final_headline = request.form.get(
            "final_headline",
            ""
        ).strip()


        final_subheading = request.form.get(
            "final_subheading",
            ""
        ).strip()


        final_summary = request.form.get(
            "final_summary",
            ""
        ).strip()


        final_article = request.form.get(
            "final_article",
            ""
        ).strip()


        key_facts = request.form.get(
            "key_facts",
            ""
        ).strip()


        tags = request.form.get(
            "tags",
            ""
        ).strip()


        # ----------------------------------------------
        # Basic Validation
        # ----------------------------------------------

        if not final_headline:

            flash(
                "Headline cannot be empty.",
                "error"
            )

            return redirect(
                url_for(
                    "admin.edit_news",
                    news_id=news.id
                )
            )


        if not final_summary:

            flash(
                "Summary cannot be empty.",
                "error"
            )

            return redirect(
                url_for(
                    "admin.edit_news",
                    news_id=news.id
                )
            )


        if not final_article:

            flash(
                "Article cannot be empty.",
                "error"
            )

            return redirect(
                url_for(
                    "admin.edit_news",
                    news_id=news.id
                )
            )


        # ----------------------------------------------
        # Save Admin-Edited Content
        # ----------------------------------------------

        news.final_headline = final_headline

        news.final_subheading = final_subheading

        news.final_summary = final_summary

        news.final_article = final_article


        # ----------------------------------------------
        # Save Key Facts and Tags
        # ----------------------------------------------

        news.key_facts = key_facts

        news.tags = tags


        # ----------------------------------------------
        # Save Breaking / Featured
        # ----------------------------------------------

        news.is_breaking = (
            request.form.get("is_breaking") == "1"
        )


        news.is_featured = (
            request.form.get("is_featured") == "1"
        )


        # ----------------------------------------------
        # Create Audit Trail
        # ----------------------------------------------

        admin_action = AdminAction(

            admin_id=session["user_id"],

            news_id=news.id,

            action="EDITED",

            comment="News content edited by admin."

        )


        db.session.add(admin_action)


        # ----------------------------------------------
        # Save Changes
        # ----------------------------------------------

        db.session.commit()


        flash(
            "News edited successfully.",
            "success"
        )


        return redirect(
            url_for("admin.dashboard")
        )


    # ==================================================
    # SHOW EDIT PAGE
    # ==================================================

    return render_template(
        "admin/edit_news.html",
        news=news
    )


# ==================================================
# PUBLISH NEWS
# ==================================================

@admin.route(
    "/publish/<int:news_id>",
    methods=["POST"]
)
def publish_news(news_id):

    if not is_admin():
        return redirect(
            url_for("auth.admin_login")
        )


    news = News.query.get_or_404(news_id)


    # ----------------------------------------------
    # Only APPROVED News Can Be Published
    # ----------------------------------------------

    if news.status != "APPROVED":

        flash(
            "Only approved news can be published.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )


    # ----------------------------------------------
    # Change Status
    # ----------------------------------------------

    news.status = "PUBLISHED"


    # ----------------------------------------------
    # Save Publication Time
    # ----------------------------------------------

    news.published_at = datetime.utcnow()


    # ----------------------------------------------
    # Create Admin Action
    # ----------------------------------------------

    admin_action = AdminAction(

        admin_id=session["user_id"],

        news_id=news.id,

        action="PUBLISHED",

        comment="News published by admin."

    )


    db.session.add(admin_action)


    db.session.commit()


    flash(
        "News published successfully.",
        "success"
    )


    return redirect(
        url_for("admin.dashboard")
    )