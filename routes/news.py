from flask import Blueprint, render_template, request
from models.database_models import News
from sqlalchemy import or_, func

news = Blueprint("news", __name__)


# ==================================================
# HOMEPAGE
# ==================================================

@news.route("/")
def homepage():

    search_query = request.args.get("search", "").strip()
    selected_category = request.args.get("category", "").strip()
    selected_location = request.args.get("location", "").strip()
    selected_date = request.args.get("date", "").strip()

    # ==================================================
    # BASE QUERY
    # Only published news will be shown
    # ==================================================

    query = News.query.filter(
        News.status == "PUBLISHED"
    )


    # ==================================================
    # SEARCH FILTER
    # ==================================================

    if search_query:

        search_pattern = f"%{search_query}%"

        query = query.filter(
            or_(

                # Original title
                News.title.ilike(search_pattern),

                # AI generated content
                News.ai_headline.ilike(search_pattern),
                News.ai_subheading.ilike(search_pattern),
                News.ai_summary.ilike(search_pattern),
                News.ai_article.ilike(search_pattern),

                # Admin final content
                News.final_headline.ilike(search_pattern),
                News.final_subheading.ilike(search_pattern),
                News.final_summary.ilike(search_pattern),
                News.final_article.ilike(search_pattern),

                # User submitted information
                News.bullet_points.ilike(search_pattern),
                News.additional_description.ilike(search_pattern),
                News.supporting_information.ilike(search_pattern),

                # Other searchable information
                News.key_facts.ilike(search_pattern),
                News.tags.ilike(search_pattern),
                News.category.ilike(search_pattern),
                News.location.ilike(search_pattern)
            )
        )


    # ==================================================
    # CATEGORY FILTER
    # ==================================================

    if selected_category:

        query = query.filter(
            func.lower(func.trim(News.category))
            == selected_category.lower().strip()
        )


    # ==================================================
    # LOCATION FILTER
    # ==================================================

    if selected_location:

        query = query.filter(
            func.lower(func.trim(News.location))
            == selected_location.lower().strip()
        )


    # ==================================================
    # DATE FILTER
    # ==================================================

    if selected_date:

        query = query.filter(
            News.incident_date == selected_date
        )


    # ==================================================
    # FILTERED / ALL PUBLISHED NEWS
    # ==================================================

    published_news = query.order_by(
        News.published_at.desc()
    ).all()


    # ==================================================
    # BREAKING NEWS
    # ==================================================

    breaking_news = News.query.filter(
        News.status == "PUBLISHED",
        News.is_breaking == True
    ).order_by(
        News.published_at.desc()
    ).all()


    # ==================================================
    # FEATURED NEWS
    # ==================================================

    featured_news = News.query.filter(
        News.status == "PUBLISHED",
        News.is_featured == True
    ).order_by(
        News.published_at.desc()
    ).all()


    # ==================================================
    # AVAILABLE CATEGORIES
    # ==================================================

    categories = [
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
    # AVAILABLE LOCATIONS
    # ==================================================

    locations = News.query.with_entities(
        News.location
    ).filter(
        News.status == "PUBLISHED",
        News.location.isnot(None),
        News.location != ""
    ).distinct().order_by(
        News.location
    ).all()

    locations = [
        location[0]
        for location in locations
    ]


    # ==================================================
    # SEND DATA TO HOMEPAGE
    # ==================================================

    return render_template(
        "news/home.html",

        published_news=published_news,

        breaking_news=breaking_news,

        featured_news=featured_news,

        search_query=search_query,

        selected_category=selected_category,

        selected_location=selected_location,

        selected_date=selected_date,

        categories=categories,

        locations=locations
    )


# ==================================================
# BREAKING NEWS PAGE
# ==================================================

@news.route("/breaking-news")
def breaking_news_page():

    breaking_news = News.query.filter(
        News.status == "PUBLISHED",
        News.is_breaking == True
    ).order_by(
        News.published_at.desc()
    ).all()

    return render_template(
        "news/breaking_news.html",
        breaking_news=breaking_news
    )


# ==================================================
# FEATURED NEWS PAGE
# ==================================================

@news.route("/featured-news")
def featured_news_page():

    featured_news = News.query.filter(
        News.status == "PUBLISHED",
        News.is_featured == True
    ).order_by(
        News.published_at.desc()
    ).all()

    return render_template(
        "news/featured_news.html",
        featured_news=featured_news
    )


# ==================================================
# NEWS DETAIL PAGE
# ==================================================

@news.route("/news/<int:news_id>")
def news_detail(news_id):

    news_item = News.query.filter(
        News.id == news_id,
        News.status == "PUBLISHED"
    ).first_or_404()

    return render_template(
        "news/detail.html",
        news=news_item
    )

# ==================================================
# CATEGORIES PAGE
# ==================================================

@news.route("/categories")
def categories_page():

    categories = [
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

    return render_template(
        "news/categories.html",
        categories=categories
    )


# ==================================================
# ABOUT PAGE
# ==================================================

@news.route("/about")
def about_page():

    return render_template(
        "news/about.html"
    )