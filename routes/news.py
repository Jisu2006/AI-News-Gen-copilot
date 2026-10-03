import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    render_template,
    request,
    abort,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)

from repositories.news_repository import (
    get_published_news,
    get_breaking_news,
    get_featured_news,
    get_latest_news,
    get_related_news,
    get_published_locations,
    get_published_category_counts,
    get_published_news_by_id,
)

from repositories.engagement_repository import (
    increment_view_count,
    get_like_count,
    user_has_liked,
    toggle_like,
    create_comment,
    get_comment_count,
    get_comments,
)

from repositories.user_repository import (
    find_user_by_id,
)


news = Blueprint(
    "news",
    __name__
)


CATEGORIES = [
    "Local News",
    "Accident",
    "Crime",
    "Sports",
    "Entertainment",
    "Education",
    "Technology",
    "Business",
    "Weather",
    "Politics",
    "Events",
    "Other",
]


# ============================================================
# HOMEPAGE
# ============================================================

@news.route("/")
def homepage():

    search_query = request.args.get(
        "search",
        ""
    ).strip()

    selected_category = request.args.get(
        "category",
        ""
    ).strip()

    selected_location = request.args.get(
        "location",
        ""
    ).strip()

    selected_date = request.args.get(
        "date",
        ""
    ).strip()

    published_news = get_published_news(
        search_query=search_query,
        selected_category=selected_category,
        selected_location=selected_location,
        selected_date=selected_date,
    )

    breaking_news = get_breaking_news()

    featured_news = get_featured_news()

    locations = get_published_locations()

    return render_template(
        "news/home.html",
        published_news=published_news,
        breaking_news=breaking_news,
        featured_news=featured_news,
        search_query=search_query,
        selected_category=selected_category,
        selected_location=selected_location,
        selected_date=selected_date,
        categories=CATEGORIES,
        locations=locations,
    )


# ============================================================
# BREAKING NEWS
# ============================================================

@news.route("/breaking")
@news.route("/breaking-news")
def breaking_news_page():

    breaking_news = get_breaking_news()

    return render_template(
        "news/breaking_news.html",
        breaking_news=breaking_news,
    )


# ============================================================
# LATEST NEWS
# ============================================================

@news.route("/latest")
@news.route("/latest-news")
def latest_news_page():

    published_news = get_latest_news()

    return render_template(
        "news/latest_news.html",
        published_news=published_news,
    )


# ============================================================
# FEATURED NEWS
# ============================================================

@news.route("/featured")
@news.route("/featured-news")
def featured_news_page():

    featured_news = get_featured_news()

    return render_template(
        "news/featured_news.html",
        featured_news=featured_news,
    )


# ============================================================
# NEWS DETAIL
# ============================================================

@news.route("/news/<int:news_id>")
def news_detail(news_id):

    news_item = get_published_news_by_id(
        news_id
    )

    if not news_item:
        abort(404)

    # --------------------------------------------------------
    # View count
    # --------------------------------------------------------

    session_view_key = (
        f"viewed_news_{news_id}"
    )

    if not session.get(
        session_view_key
    ):

        result = increment_view_count(
            news_id
        )

        if result:

            session[
                session_view_key
            ] = True

            news_item = (
                get_published_news_by_id(
                    news_id
                )
            )

    # --------------------------------------------------------
    # User information
    # --------------------------------------------------------

    user = find_user_by_id(
        news_item.user_id
    )

    news_item[
        "user"
    ] = (
        user
        if user
        else {
            "name": "Unknown User"
        }
    )

    # --------------------------------------------------------
    # Likes
    # --------------------------------------------------------

    likes_count = get_like_count(
        news_id
    )

    current_user_id = session.get(
        "user_id"
    )

    user_liked = False

    if current_user_id:

        user_liked = user_has_liked(
            news_id,
            current_user_id
        )

    # --------------------------------------------------------
    # Comments
    # --------------------------------------------------------

    comments = get_comments(
        news_id
    )

    # --------------------------------------------------------
    # Related
    # --------------------------------------------------------

    related_news = get_related_news(
        category=news_item.category,
        exclude_news_id=news_id,
        limit=4,
    )

    return render_template(
        "news/detail.html",
        news=news_item,
        related_news=related_news,
        likes_count=likes_count,
        user_liked=user_liked,
        comments=comments,
    )


# ============================================================
# TOGGLE LIKE
# ============================================================

@news.route(
    "/news/<int:news_id>/like",
    methods=["POST"]
)
def toggle_like_route(news_id):

    news_item = get_published_news_by_id(
        news_id
    )

    if not news_item:
        abort(404)

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        if (
            request.is_json
            or
            request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest"
        ):

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        "login_required",

                    "message":
                        "Please log in to like this article.",

                    "redirect":
                        url_for(
                            "auth.user_login"
                        ),
                }
            ), 401

        flash(
            "Please log in to like this article.",
            "warning"
        )

        return redirect(
            url_for(
                "auth.user_login"
            )
        )

    try:

        result = toggle_like(
            news_id,
            user_id
        )

    except Exception as error:

        print(
            f"[LIKE ERROR] {error}"
        )

        if (
            request.is_json
            or
            request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest"
        ):

            return jsonify(
                {
                    "success":
                        False,

                    "message":
                        "Unable to update like."
                }
            ), 500

        flash(
            "Unable to update like.",
            "error"
        )

        return redirect(
            url_for(
                "news.news_detail",
                news_id=news_id
            )
        )

    if (
        request.is_json
        or
        request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest"
    ):

        return jsonify(
            {
                "success":
                    True,

                "liked":
                    result["liked"],

                "likes_count":
                    result["likes_count"],
            }
        )

    return redirect(
        url_for(
            "news.news_detail",
            news_id=news_id
        )
    )


# ============================================================
# POST COMMENT
# ============================================================

@news.route(
    "/news/<int:news_id>/comment",
    methods=["POST"]
)
def post_comment(news_id):

    news_item = get_published_news_by_id(
        news_id
    )

    if not news_item:
        abort(404)

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        if (
            request.is_json
            or
            request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest"
        ):

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        "login_required",

                    "message":
                        "Please log in to post a comment.",

                    "redirect":
                        url_for(
                            "auth.user_login"
                        ),
                }
            ), 401

        flash(
            "Please log in to post a comment.",
            "warning"
        )

        return redirect(
            url_for(
                "auth.user_login"
            )
        )

    # --------------------------------------------------------
    # Get comment
    # --------------------------------------------------------

    comment_text = request.form.get(
        "comment_text",
        ""
    ).strip()

    if (
        not comment_text
        and
        request.is_json
    ):

        request_data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        comment_text = (
            request_data.get(
                "comment_text",
                ""
            )
            .strip()
        )

    if not comment_text:

        if (
            request.is_json
            or
            request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest"
        ):

            return jsonify(
                {
                    "success":
                        False,

                    "error":
                        "empty_comment",

                    "message":
                        "Comment cannot be empty."
                }
            ), 400

        flash(
            "Comment cannot be empty.",
            "warning"
        )

        return redirect(
            url_for(
                "news.news_detail",
                news_id=news_id
            )
        )

    comment_text = comment_text[:2000]

    try:

        new_comment = create_comment(
            news_id=news_id,
            user_id=user_id,
            comment_text=comment_text,
        )

        comments_count = get_comment_count(
            news_id
        )

    except Exception as error:

        print(
            f"[COMMENT ERROR] {error}"
        )

        if (
            request.is_json
            or
            request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest"
        ):

            return jsonify(
                {
                    "success":
                        False,

                    "message":
                        "Unable to post comment."
                }
            ), 500

        flash(
            "Unable to post comment.",
            "error"
        )

        return redirect(
            url_for(
                "news.news_detail",
                news_id=news_id
            )
        )

    user_name = (
        session.get(
            "user_name"
        )
        or
        "User"
    )

    if (
        request.is_json
        or
        request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest"
    ):

        created_at = (
            new_comment["created_at"]
        )

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=timezone.utc
            )

        created_at = created_at.astimezone(
            ZoneInfo("Asia/Kolkata")
        )

        return jsonify(
            {
                "success":
                    True,

                "comment":
                    {
                        "id":
                            new_comment["_id"],

                        "user_name":
                            user_name,

                        "comment_text":
                            new_comment[
                                "comment_text"
                            ],

                        "created_at":
                            created_at.strftime(
                                "%d %b %Y, %I:%M %p"
                            ),
                    },

                "comments_count":
                    comments_count,
            }
        )

    flash(
        "Your comment has been posted successfully!",
        "success"
    )

    return redirect(
        url_for(
            "news.news_detail",
            news_id=news_id
        )
    )


# ============================================================
# CATEGORIES
# ============================================================

@news.route("/categories")
def categories_page():

    category_counts = (
        get_published_category_counts(
            CATEGORIES
        )
    )

    return render_template(
        "news/categories.html",
        categories=CATEGORIES,
        category_counts=category_counts,
    )


# ============================================================
# ABOUT
# ============================================================

@news.route("/about")
def about_page():

    return render_template(
        "news/about.html"
    )