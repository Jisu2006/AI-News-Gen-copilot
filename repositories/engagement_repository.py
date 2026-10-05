from datetime import datetime, timezone
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from database.mongo import (
    get_comments_collection,
    get_likes_collection,
    get_next_id,
    get_news_collection,
    get_users_collection,
    utc_now,
)


# ============================================================
# VIEWS
# ============================================================

def increment_view_count(news_id):
    """
    Increment news view count atomically.
    """

    try:
        news_id = int(news_id)

    except (TypeError, ValueError):
        return None

    return get_news_collection().find_one_and_update(
        {
            "_id": news_id,
            "status": "PUBLISHED",
        },
        {
            "$inc": {
                "views_count": 1
            }
        },
        return_document=ReturnDocument.AFTER,
    )


# ============================================================
# LIKE COUNT
# ============================================================

def get_like_count(news_id):

    try:
        news_id = int(news_id)

    except (TypeError, ValueError):
        return 0

    return get_likes_collection().count_documents(
        {
            "news_id": news_id
        }
    )


# ============================================================
# CHECK USER LIKE
# ============================================================

def user_has_liked(
    news_id,
    user_id,
):

    try:
        news_id = int(news_id)
        user_id = int(user_id)

    except (TypeError, ValueError):
        return False

    document = get_likes_collection().find_one(
        {
            "news_id": news_id,
            "user_id": user_id,
        }
    )

    return document is not None


# ============================================================
# TOGGLE LIKE
# ============================================================

def toggle_like(
    news_id,
    user_id,
):

    news_id = int(news_id)
    user_id = int(user_id)

    likes = get_likes_collection()

    existing_like = likes.find_one(
        {
            "news_id": news_id,
            "user_id": user_id,
        }
    )

    if existing_like:

        likes.delete_one(
            {
                "_id":
                    existing_like["_id"]
            }
        )

        liked = False

    else:

        document = {
            "_id":
                get_next_id(
                    "news_likes"
                ),

            "news_id":
                news_id,

            "user_id":
                user_id,

            "created_at":
                utc_now(),
        }

        try:

            likes.insert_one(
                document
            )

            liked = True

        except DuplicateKeyError:

            liked = True

    total_likes = likes.count_documents(
        {
            "news_id": news_id
        }
    )

    return {
        "liked": liked,
        "likes_count": total_likes,
    }


# ============================================================
# CREATE COMMENT
# ============================================================

def create_comment(
    news_id,
    user_id,
    comment_text,
):
    """
    Create a news comment in MongoDB.
    """

    try:
        news_id = int(news_id)
        user_id = int(user_id)

    except (TypeError, ValueError):
        raise ValueError(
            "Invalid news_id or user_id."
        )

    comment_text = (
        comment_text or ""
    ).strip()

    if not comment_text:
        raise ValueError(
            "Comment cannot be empty."
        )

    comment_text = comment_text[:2000]

    now = utc_now()

    comment_id = get_next_id(
        "news_comments"
    )

    document = {
        "_id": comment_id,

        "news_id": news_id,

        "user_id": user_id,

        "comment_text": comment_text,

        "created_at": now,

        "updated_at": now,
    }

    get_comments_collection().insert_one(
        document
    )

    return document


# ============================================================
# COMMENT COUNT
# ============================================================

def get_comment_count(news_id):

    try:
        news_id = int(news_id)

    except (TypeError, ValueError):
        return 0

    return get_comments_collection().count_documents(
        {
            "news_id": news_id
        }
    )


# ============================================================
# GET COMMENTS WITH USER
# ============================================================

def get_comments(
    news_id,
    limit=200,
):

    try:
        news_id = int(news_id)

    except (TypeError, ValueError):
        return []

    comments = list(
        get_comments_collection()
        .find(
            {
                "news_id":
                    news_id
            }
        )
        .sort(
            "created_at",
            -1
        )
        .limit(limit)
    )

    users = get_users_collection()

    for comment in comments:

        user = users.find_one(
            {
                "_id":
                    comment.get(
                        "user_id"
                    )
            }
        )

        comment["author"] = (
            user
            if user
            else {
                "name": "User"
            }
        )

    return comments