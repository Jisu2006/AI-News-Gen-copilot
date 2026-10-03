from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
    abort,
)

from database.mongo import utc_now

from repositories.news_repository import (
    find_news_by_id,
    update_news,
    NewsDocument,
)

from repositories.admin_repository import (
    create_admin_action,
    get_admin_dashboard_data,
)


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ============================================================
# ADMIN ACCESS CONTROL
# ============================================================

def check_admin_access():
    """
    Verify administrator authentication and role.
    """

    if "user_id" not in session:

        return redirect(
            url_for(
                "auth.admin_login",
                next=request.path
            )
        )

    if session.get(
        "user_role"
    ) != "admin":

        flash(
            "Access denied. Administrator privileges required.",
            "error"
        )

        abort(403)

    return None


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@admin.route("/dashboard")
def dashboard():

    auth_check = check_admin_access()

    if auth_check:
        return auth_check

    dashboard_data = (
        get_admin_dashboard_data()
    )

    return render_template(
        "admin/dashboard.html",
        pending_news=dashboard_data[
            "pending_news"
        ],
        approved_news=dashboard_data[
            "approved_news"
        ],
        published_news=dashboard_data[
            "published_news"
        ],
        admin_actions=dashboard_data[
            "admin_actions"
        ],
    )


# ============================================================
# REVIEW NEWS
# ============================================================

@admin.route(
    "/news/<int:news_id>/review",
    methods=["GET", "POST"]
)
@admin.route(
    "/review/<int:news_id>",
    methods=["GET", "POST"]
)
def review_news(news_id):

    auth_check = check_admin_access()

    if auth_check:
        return auth_check

    news_item = find_news_by_id(
        news_id
    )

    if not news_item:

        flash(
            "News submission not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    if request.method == "POST":

        action = (
            request.form.get(
                "action",
                ""
            )
            .strip()
            .lower()
        )

        comment = (
            request.form.get(
                "comment",
                ""
            )
            .strip()
        )

        # ----------------------------------------------------
        # APPROVE
        # ----------------------------------------------------

        if action == "approve":

            update_data = {
                "is_breaking":
                    request.form.get(
                        "is_breaking"
                    ) == "1",

                "is_featured":
                    request.form.get(
                        "is_featured"
                    ) == "1",

                "status":
                    "APPROVED",

                "admin_comment":
                    None,
            }

            updated_news = update_news(
                news_item.id,
                update_data
            )

            if not updated_news:

                flash(
                    "Unable to approve this news.",
                    "error"
                )

                return redirect(
                    url_for(
                        "admin.review_news",
                        news_id=news_item.id
                    )
                )

            create_admin_action(
                admin_id=session[
                    "user_id"
                ],
                news_id=news_item.id,
                action="APPROVED",
                comment=(
                    comment
                    or
                    "News draft approved by admin."
                ),
            )

            flash(
                "News approved successfully. "
                "It is ready for publication.",
                "success"
            )

            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        # ----------------------------------------------------
        # REQUEST INFORMATION
        # ----------------------------------------------------

        elif action == "request_information":

            if not comment:

                flash(
                    "Please enter instructions explaining "
                    "what additional information is required.",
                    "error"
                )

                return redirect(
                    url_for(
                        "admin.review_news",
                        news_id=news_item.id
                    )
                )

            updated_news = update_news(
                news_item.id,
                {
                    "status":
                        "NEEDS_INFORMATION",

                    "admin_comment":
                        comment,
                }
            )

            if not updated_news:

                flash(
                    "Unable to request additional information.",
                    "error"
                )

                return redirect(
                    url_for(
                        "admin.review_news",
                        news_id=news_item.id
                    )
                )

            create_admin_action(
                admin_id=session[
                    "user_id"
                ],
                news_id=news_item.id,
                action="REQUEST_INFORMATION",
                comment=comment,
            )

            flash(
                "Additional information requested from user.",
                "success"
            )

            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        elif action == "reject":

            if not comment:

                flash(
                    "Please provide a reason for rejecting "
                    "this news submission.",
                    "error"
                )

                return redirect(
                    url_for(
                        "admin.review_news",
                        news_id=news_item.id
                    )
                )

            updated_news = update_news(
                news_item.id,
                {
                    "status":
                        "REJECTED",

                    "admin_comment":
                        comment,
                }
            )

            if not updated_news:

                flash(
                    "Unable to reject this news.",
                    "error"
                )

                return redirect(
                    url_for(
                        "admin.review_news",
                        news_id=news_item.id
                    )
                )

            create_admin_action(
                admin_id=session[
                    "user_id"
                ],
                news_id=news_item.id,
                action="REJECTED",
                comment=comment,
            )

            flash(
                "News submission rejected.",
                "success"
            )

            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        # ----------------------------------------------------
        # INVALID ACTION
        # ----------------------------------------------------

        else:

            flash(
                "Invalid administrator action.",
                "error"
            )

            return redirect(
                url_for(
                    "admin.review_news",
                    news_id=news_item.id
                )
            )

    return render_template(
        "admin/review_news.html",
        news=news_item
    )


# ============================================================
# EDIT NEWS
# ============================================================

@admin.route(
    "/news/<int:news_id>/edit",
    methods=["GET", "POST"]
)
@admin.route(
    "/edit/<int:news_id>",
    methods=["GET", "POST"]
)
def edit_news(news_id):

    auth_check = check_admin_access()

    if auth_check:
        return auth_check

    news_item = find_news_by_id(
        news_id
    )

    if not news_item:

        flash(
            "News submission not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    if request.method == "POST":

        final_headline = (
            request.form.get(
                "final_headline",
                ""
            ).strip()
        )

        final_subheading = (
            request.form.get(
                "final_subheading",
                ""
            ).strip()
        )

        final_summary = (
            request.form.get(
                "final_summary",
                ""
            ).strip()
        )

        final_article = (
            request.form.get(
                "final_article",
                ""
            ).strip()
        )

        key_facts_text = (
            request.form.get(
                "key_facts",
                ""
            ).strip()
        )

        tags_text = (
            request.form.get(
                "tags",
                ""
            ).strip()
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not final_headline:

            flash(
                "Headline cannot be empty.",
                "error"
            )

            return redirect(
                url_for(
                    "admin.edit_news",
                    news_id=news_item.id
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
                    news_id=news_item.id
                )
            )

        if not final_article:

            flash(
                "Article content cannot be empty.",
                "error"
            )

            return redirect(
                url_for(
                    "admin.edit_news",
                    news_id=news_item.id
                )
            )

        # ----------------------------------------------------
        # KEY FACTS
        # ----------------------------------------------------

        if key_facts_text:

            key_facts = [
                line.strip()
                for line
                in key_facts_text.splitlines()
                if line.strip()
            ]

            if (
                len(key_facts) == 1
                and
                "," in key_facts[0]
            ):
                key_facts = [
                    item.strip()
                    for item
                    in key_facts[0].split(",")
                    if item.strip()
                ]

        else:

            key_facts = []

        # ----------------------------------------------------
        # TAGS
        # ----------------------------------------------------

        if tags_text:

            tags = [
                item.strip()
                for item
                in tags_text.replace(
                    "\n",
                    ","
                ).split(",")
                if item.strip()
            ]

        else:

            tags = []

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        updated_news = update_news(
            news_item.id,
            {
                "final_headline":
                    final_headline,

                "final_subheading":
                    final_subheading,

                "final_summary":
                    final_summary,

                "final_article":
                    final_article,

                "key_facts":
                    key_facts,

                "tags":
                    tags,

                "is_breaking":
                    request.form.get(
                        "is_breaking"
                    ) == "1",

                "is_featured":
                    request.form.get(
                        "is_featured"
                    ) == "1",
            }
        )

        if not updated_news:

            flash(
                "Unable to update news.",
                "error"
            )

            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        # ----------------------------------------------------
        # AUDIT LOG
        # ----------------------------------------------------

        create_admin_action(
            admin_id=session[
                "user_id"
            ],
            news_id=news_item.id,
            action="EDITED",
            comment=(
                "News content edited by administrator."
            ),
        )

        flash(
            "News draft updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    # --------------------------------------------------------
    # Prepare MongoDB list fields for textarea display
    # --------------------------------------------------------

    form_news = NewsDocument(
        dict(news_item)
    )

    if isinstance(
        form_news.get("key_facts"),
        list
    ):

        form_news[
            "key_facts"
        ] = "\n".join(
            str(item)
            for item
            in form_news["key_facts"]
        )

    if isinstance(
        form_news.get("tags"),
        list
    ):

        form_news[
            "tags"
        ] = ", ".join(
            str(item)
            for item
            in form_news["tags"]
        )

    return render_template(
        "admin/edit_news.html",
        news=form_news
    )


# ============================================================
# PUBLISH NEWS
# ============================================================

@admin.route(
    "/publish/<int:news_id>",
    methods=["POST"]
)
def publish_news(news_id):

    auth_check = check_admin_access()

    if auth_check:
        return auth_check

    news_item = find_news_by_id(
        news_id
    )

    if not news_item:

        flash(
            "News submission not found.",
            "error"
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    # --------------------------------------------------------
    # Only approved news can be published
    # --------------------------------------------------------

    if news_item.status != "APPROVED":

        flash(
            "Only approved news can be published.",
            "error"
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    published_time = utc_now()

    updated_news = update_news(
        news_item.id,
        {
            "status":
                "PUBLISHED",

            "published_at":
                published_time,
        }
    )

    if not updated_news:

        flash(
            "Unable to publish news.",
            "error"
        )

        return redirect(
            url_for(
                "admin.dashboard"
            )
        )

    create_admin_action(
        admin_id=session[
            "user_id"
        ],
        news_id=news_item.id,
        action="PUBLISHED",
        comment=(
            "News published by administrator."
        ),
    )

    headline = (
        updated_news.final_headline
        or
        updated_news.ai_headline
        or
        updated_news.title
    )

    flash(
        f"News '{headline}' is now published on the newspaper!",
        "success"
    )

    return redirect(
        url_for(
            "admin.dashboard"
        )
    )