from flask import Blueprint, render_template, request, abort, redirect, url_for, session, flash, jsonify
from models.database_models import News, NewsComment, NewsLike, User
from database.db import db
from sqlalchemy import or_, func

news = Blueprint("news", __name__)

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
    "Other"
]


# ==================================================
# HOMEPAGE
# ==================================================

@news.route("/")
def homepage():
    search_query = request.args.get("search", "").strip()
    selected_category = request.args.get("category", "").strip()
    selected_location = request.args.get("location", "").strip()
    selected_date = request.args.get("date", "").strip()

    # Base query: only published news
    query = News.query.filter(News.status == "PUBLISHED")

    # Search filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                News.title.ilike(search_pattern),
                News.ai_headline.ilike(search_pattern),
                News.ai_subheading.ilike(search_pattern),
                News.ai_summary.ilike(search_pattern),
                News.ai_article.ilike(search_pattern),
                News.final_headline.ilike(search_pattern),
                News.final_subheading.ilike(search_pattern),
                News.final_summary.ilike(search_pattern),
                News.final_article.ilike(search_pattern),
                News.bullet_points.ilike(search_pattern),
                News.additional_description.ilike(search_pattern),
                News.supporting_information.ilike(search_pattern),
                News.key_facts.ilike(search_pattern),
                News.tags.ilike(search_pattern),
                News.category.ilike(search_pattern),
                News.location.ilike(search_pattern)
            )
        )

    # Category filter
    if selected_category:
        query = query.filter(
            func.lower(func.trim(News.category)) == selected_category.lower().strip()
        )

    # Location filter
    if selected_location:
        query = query.filter(
            func.lower(func.trim(News.location)) == selected_location.lower().strip()
        )

    # Date filter
    if selected_date:
        query = query.filter(News.incident_date == selected_date)

    published_news = query.order_by(News.published_at.desc()).all()

    breaking_news = News.query.filter(
        News.status == "PUBLISHED",
        News.is_breaking == True
    ).order_by(News.published_at.desc()).all()

    featured_news = News.query.filter(
        News.status == "PUBLISHED",
        News.is_featured == True
    ).order_by(News.published_at.desc()).all()

    locations_query = News.query.with_entities(
        News.location
    ).filter(
        News.status == "PUBLISHED",
        News.location.isnot(None),
        News.location != ""
    ).distinct().order_by(News.location).all()

    locations = [loc[0] for loc in locations_query if loc[0]]

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
        locations=locations
    )


# ==================================================
# BREAKING NEWS PAGE
# ==================================================

@news.route("/breaking")
@news.route("/breaking-news")
def breaking_news_page():
    breaking_news = News.query.filter(
        News.status == "PUBLISHED",
        News.is_breaking == True
    ).order_by(News.published_at.desc()).all()

    return render_template(
        "news/breaking_news.html",
        breaking_news=breaking_news
    )


# ==================================================
# LATEST NEWS PAGE
# ==================================================

@news.route("/latest")
@news.route("/latest-news")
def latest_news_page():
    published_news = News.query.filter(
        News.status == "PUBLISHED"
    ).order_by(News.published_at.desc()).all()

    return render_template(
        "news/latest_news.html",
        published_news=published_news
    )


# ==================================================
# FEATURED NEWS PAGE
# ==================================================

@news.route("/featured")
@news.route("/featured-news")
def featured_news_page():
    featured_news = News.query.filter(
        News.status == "PUBLISHED",
        News.is_featured == True
    ).order_by(News.published_at.desc()).all()

    return render_template(
        "news/featured_news.html",
        featured_news=featured_news
    )


# ==================================================
# NEWS DETAIL PAGE & ENGAGEMENT
# ==================================================

@news.route("/news/<int:news_id>")
def news_detail(news_id):
    news_item = News.query.filter(
        News.id == news_id,
        News.status == "PUBLISHED"
    ).first_or_404()

    # Deduplicated view count increment using session
    session_view_key = f"viewed_news_{news_id}"
    if not session.get(session_view_key):
        news_item.views_count = (news_item.views_count or 0) + 1
        try:
            db.session.commit()
            session[session_view_key] = True
        except Exception:
            db.session.rollback()

    # Likes data
    likes_count = NewsLike.query.filter_by(news_id=news_item.id).count()
    user_id = session.get("user_id")
    user_liked = False
    if user_id:
        user_liked = NewsLike.query.filter_by(news_id=news_item.id, user_id=user_id).first() is not None

    # Comments data
    comments = NewsComment.query.filter_by(news_id=news_item.id).order_by(NewsComment.created_at.desc()).all()

    # Related news
    related_news = News.query.filter(
        News.status == "PUBLISHED",
        News.category == news_item.category,
        News.id != news_item.id
    ).order_by(News.published_at.desc()).limit(4).all()

    return render_template(
        "news/detail.html",
        news=news_item,
        related_news=related_news,
        likes_count=likes_count,
        user_liked=user_liked,
        comments=comments
    )


@news.route("/news/<int:news_id>/like", methods=["POST"])
def toggle_like(news_id):
    news_item = News.query.filter_by(id=news_id, status="PUBLISHED").first_or_404()
    user_id = session.get("user_id")

    if not user_id:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "success": False,
                "error": "login_required",
                "message": "Please log in to like this article.",
                "redirect": url_for("auth.user_login")
            }), 401
        flash("Please log in to like this article.", "warning")
        return redirect(url_for("auth.user_login"))

    existing_like = NewsLike.query.filter_by(news_id=news_item.id, user_id=user_id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        new_like = NewsLike(news_id=news_item.id, user_id=user_id)
        db.session.add(new_like)
        db.session.commit()
        liked = True

    total_likes = NewsLike.query.filter_by(news_id=news_item.id).count()

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "liked": liked,
            "likes_count": total_likes
        })

    return redirect(url_for("news.news_detail", news_id=news_id))


@news.route("/news/<int:news_id>/comment", methods=["POST"])
def post_comment(news_id):
    news_item = News.query.filter_by(id=news_id, status="PUBLISHED").first_or_404()
    user_id = session.get("user_id")

    if not user_id:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "success": False,
                "error": "login_required",
                "message": "Please log in to post a comment.",
                "redirect": url_for("auth.user_login")
            }), 401
        flash("Please log in to post a comment.", "warning")
        return redirect(url_for("auth.user_login"))

    comment_text = request.form.get("comment_text", "").strip()
    if not comment_text and request.is_json:
        req_data = request.get_json(silent=True) or {}
        comment_text = req_data.get("comment_text", "").strip()

    if not comment_text:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "success": False,
                "error": "empty_comment",
                "message": "Comment cannot be empty."
            }), 400
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("news.news_detail", news_id=news_id))

    # Length limit and persistence
    comment_text = comment_text[:2000]

    new_comment = NewsComment(
        news_id=news_item.id,
        user_id=user_id,
        comment_text=comment_text
    )
    db.session.add(new_comment)
    db.session.commit()

    user_name = session.get("user_name") or "User"
    comments_count = NewsComment.query.filter_by(news_id=news_item.id).count()

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "comment": {
                "id": new_comment.id,
                "user_name": user_name,
                "comment_text": new_comment.comment_text,
                "created_at": new_comment.created_at.strftime("%d %b %Y, %I:%M %p")
            },
            "comments_count": comments_count
        })

    flash("Your comment has been posted successfully!", "success")
    return redirect(url_for("news.news_detail", news_id=news_id))


# ==================================================
# CATEGORIES PAGE
# ==================================================

@news.route("/categories")
def categories_page():
    # Count published news per category
    category_counts = {}
    for cat in CATEGORIES:
        count = News.query.filter(
            News.status == "PUBLISHED",
            func.lower(func.trim(News.category)) == cat.lower().strip()
        ).count()
        category_counts[cat] = count

    return render_template(
        "news/categories.html",
        categories=CATEGORIES,
        category_counts=category_counts
    )


# ==================================================
# ABOUT PAGE
# ==================================================

@news.route("/about")
def about_page():
    return render_template("news/about.html")