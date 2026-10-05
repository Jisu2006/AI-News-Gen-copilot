import re
from datetime import datetime, time

from pymongo import ReturnDocument

from database.mongo import (
    get_news_collection,
    get_next_id,
    utc_now,
)


# ============================================================
# PRESENTATION HELPERS
# ============================================================

class DateDisplay(str):
    """
    String representation of YYYY-MM-DD that also supports
    the existing Jinja template's .strftime() usage.
    """

    def strftime(self, fmt: str):
        try:
            value = datetime.strptime(
                str(self),
                "%Y-%m-%d"
            )

            return value.strftime(fmt)

        except (TypeError, ValueError):
            return str(self)


class TimeDisplay(str):
    """
    String representation of HH:MM[:SS] that also supports
    .strftime() when required by templates.
    """

    def strftime(self, fmt: str):
        try:
            formats = (
                "%H:%M:%S",
                "%H:%M",
            )

            parsed = None

            for time_format in formats:
                try:
                    parsed = datetime.strptime(
                        str(self),
                        time_format
                    )
                    break
                except ValueError:
                    continue

            if parsed is None:
                return str(self)

            return parsed.strftime(fmt)

        except (TypeError, ValueError):
            return str(self)


class MongoDocument(dict):
    """
    Dictionary wrapper allowing both:

        document["title"]

    and:

        document.title
    """

    def __getattr__(self, name):

        if name == "id":
            return self.get("_id")

        try:
            return self[name]

        except KeyError as error:
            raise AttributeError(name) from error


class NewsDocument(MongoDocument):
    """
    MongoDB news document with compatibility helpers
    for existing Flask/Jinja templates.
    """

    def __getattr__(self, name):

        if name == "id":
            return self.get("_id")

        value = self.get(name)

        if (
            name == "incident_date"
            and isinstance(value, str)
            and value
        ):
            return DateDisplay(value)

        if (
            name == "incident_time"
            and isinstance(value, str)
            and value
        ):
            return TimeDisplay(value)

        return value


def _wrap_news(document):
    if document is None:
        return None

    return NewsDocument(document)


# ============================================================
# INTERNAL FIELD NORMALIZATION
# ============================================================

def _normalize_key_facts(value):

    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str):

        return [
            line.strip()
            for line in value.splitlines()
            if line.strip()
        ]

    return [str(value)]


def _normalize_tags(value):

    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str):

        return [
            item.strip()
            for item in value.replace(
                "\n",
                ","
            ).split(",")
            if item.strip()
        ]

    return [str(value)]


# ============================================================
# CREATE NEWS
# ============================================================

def create_news(
    user_id,
    category,
    title,
    location=None,
    incident_date=None,
    incident_time=None,
    bullet_points=None,
    additional_description=None,
    image_path=None,
    video_path=None,
    source_url=None,
    supporting_information=None,
    status="DRAFT",
):
    """
    Create a new news document.
    """

    news_id = get_next_id("news")

    now = utc_now()

    document = {
        "_id": news_id,

        "user_id": int(user_id),

        "category": category,
        "title": title,

        "location": location,

        "incident_date": (
            str(incident_date)
            if incident_date
            else None
        ),

        "incident_time": (
            str(incident_time)
            if incident_time
            else None
        ),

        "bullet_points": bullet_points,
        "additional_description": additional_description,

        "image_path": image_path,
        "video_path": video_path,

        "source_url": source_url,
        "supporting_information": supporting_information,

        # AI
        "ai_headline": None,
        "ai_subheading": None,
        "ai_summary": None,
        "ai_article": None,
        "key_facts": [],
        "tags": [],

        # Final editorial version
        "final_headline": None,
        "final_subheading": None,
        "final_summary": None,
        "final_article": None,

        # Workflow
        "status": status,
        "admin_comment": None,

        "is_breaking": False,
        "is_featured": False,

        # Timestamps
        "created_at": now,
        "updated_at": now,
        "published_at": None,

        # Engagement
        "views_count": 0,
    }

    get_news_collection().insert_one(
        document
    )

    return _wrap_news(document)


# ============================================================
# FIND NEWS BY ID
# ============================================================

def find_news_by_id(news_id):

    if news_id is None:
        return None

    try:
        news_id = int(news_id)

    except (TypeError, ValueError):
        return None

    document = (
        get_news_collection()
        .find_one(
            {
                "_id": news_id
            }
        )
    )

    return _wrap_news(document)


# ============================================================
# FIND NEWS BY USER
# ============================================================

def find_news_by_user(
    user_id,
    limit=100,
):

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        return []

    cursor = (
        get_news_collection()
        .find(
            {
                "user_id": user_id
            }
        )
        .sort(
            "created_at",
            -1
        )
        .limit(limit)
    )

    return [
        _wrap_news(document)
        for document in cursor
    ]


# ============================================================
# UPDATE NEWS
# ============================================================

def update_news(
    news_id,
    update_data: dict,
):

    if news_id is None:
        return None

    if not update_data:
        return find_news_by_id(news_id)

    try:
        news_id = int(news_id)

    except (TypeError, ValueError):
        return None

    update_data = dict(update_data)

    if "key_facts" in update_data:
        update_data["key_facts"] = (
            _normalize_key_facts(
                update_data["key_facts"]
            )
        )

    if "tags" in update_data:
        update_data["tags"] = (
            _normalize_tags(
                update_data["tags"]
            )
        )

    update_data["updated_at"] = utc_now()

    result = (
        get_news_collection()
        .find_one_and_update(
            {
                "_id": news_id
            },
            {
                "$set": update_data
            },
            return_document=ReturnDocument.AFTER,
        )
    )

    return _wrap_news(result)


# ============================================================
# USER COUNTS
# ============================================================

def count_user_news(user_id):

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        return 0

    return (
        get_news_collection()
        .count_documents(
            {
                "user_id": user_id
            }
        )
    )


def count_user_news_by_status(
    user_id,
    status,
):

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        return 0

    return (
        get_news_collection()
        .count_documents(
            {
                "user_id": user_id,
                "status": status,
            }
        )
    )


# ============================================================
# DELETE NEWS
# ============================================================

def delete_news(news_id):

    try:
        news_id = int(news_id)

    except (TypeError, ValueError):
        return False

    result = (
        get_news_collection()
        .delete_one(
            {
                "_id": news_id
            }
        )
    )

    return result.deleted_count == 1


# ============================================================
# EXACT CASE-INSENSITIVE FIELD MATCH
# ============================================================

def _exact_regex(value: str):
    return {
        "$regex": (
            "^"
            + re.escape(
                value.strip()
            )
            + "$"
        ),
        "$options": "i",
    }


# ============================================================
# GET PUBLISHED NEWS
# ============================================================

def get_published_news(
    search_query="",
    selected_category="",
    selected_location="",
    selected_date="",
    limit=200,
):

    filters = {
        "status": "PUBLISHED"
    }

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search_query:

        pattern = re.escape(
            search_query.strip()
        )

        search_regex = {
            "$regex": pattern,
            "$options": "i",
        }

        filters["$or"] = [
            {
                "title":
                    search_regex
            },
            {
                "ai_headline":
                    search_regex
            },
            {
                "ai_subheading":
                    search_regex
            },
            {
                "ai_summary":
                    search_regex
            },
            {
                "ai_article":
                    search_regex
            },
            {
                "final_headline":
                    search_regex
            },
            {
                "final_subheading":
                    search_regex
            },
            {
                "final_summary":
                    search_regex
            },
            {
                "final_article":
                    search_regex
            },
            {
                "bullet_points":
                    search_regex
            },
            {
                "additional_description":
                    search_regex
            },
            {
                "supporting_information":
                    search_regex
            },
            {
                "key_facts":
                    search_regex
            },
            {
                "tags":
                    search_regex
            },
            {
                "category":
                    search_regex
            },
            {
                "location":
                    search_regex
            },
        ]

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    if selected_category:
        filters["category"] = _exact_regex(
            selected_category
        )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    if selected_location:
        filters["location"] = _exact_regex(
            selected_location
        )

    # --------------------------------------------------------
    # Incident Date
    # --------------------------------------------------------

    if selected_date:
        filters["incident_date"] = (
            selected_date
        )

    cursor = (
        get_news_collection()
        .find(filters)
        .sort(
            "published_at",
            -1
        )
        .limit(limit)
    )

    return [
        _wrap_news(document)
        for document in cursor
    ]


# ============================================================
# BREAKING NEWS
# ============================================================

def get_breaking_news(
    limit=200,
):

    cursor = (
        get_news_collection()
        .find(
            {
                "status": "PUBLISHED",
                "is_breaking": True,
            }
        )
        .sort(
            "published_at",
            -1
        )
        .limit(limit)
    )

    return [
        _wrap_news(document)
        for document in cursor
    ]


# ============================================================
# FEATURED NEWS
# ============================================================

def get_featured_news(
    limit=200,
):

    cursor = (
        get_news_collection()
        .find(
            {
                "status": "PUBLISHED",
                "is_featured": True,
            }
        )
        .sort(
            "published_at",
            -1
        )
        .limit(limit)
    )

    return [
        _wrap_news(document)
        for document in cursor
    ]


# ============================================================
# LATEST NEWS
# ============================================================

def get_latest_news(
    limit=200,
):

    cursor = (
        get_news_collection()
        .find(
            {
                "status": "PUBLISHED"
            }
        )
        .sort(
            "published_at",
            -1
        )
        .limit(limit)
    )

    return [
        _wrap_news(document)
        for document in cursor
    ]


# ============================================================
# RELATED NEWS
# ============================================================

def get_related_news(
    category,
    exclude_news_id,
    limit=4,
):

    filters = {
        "status": "PUBLISHED",
        "category": _exact_regex(
            category
        ),
    }

    if exclude_news_id is not None:

        try:
            exclude_news_id = int(
                exclude_news_id
            )

            filters["_id"] = {
                "$ne": exclude_news_id
            }

        except (TypeError, ValueError):
            pass

    cursor = (
        get_news_collection()
        .find(filters)
        .sort(
            "published_at",
            -1
        )
        .limit(limit)
    )

    return [
        _wrap_news(document)
        for document in cursor
    ]


# ============================================================
# PUBLISHED LOCATIONS
# ============================================================

def get_published_locations():

    locations = (
        get_news_collection()
        .distinct(
            "location",
            {
                "status": "PUBLISHED"
            }
        )
    )

    cleaned = sorted(
        {
            str(location).strip()
            for location in locations
            if location
            and str(location).strip()
        },
        key=lambda value:
            value.lower()
    )

    return cleaned


# ============================================================
# CATEGORY COUNTS
# ============================================================

def get_published_category_counts(
    categories,
):

    collection = get_news_collection()

    counts = {}

    for category in categories:

        counts[category] = (
            collection.count_documents(
                {
                    "status": "PUBLISHED",
                    "category": _exact_regex(
                        category
                    ),
                }
            )
        )

    return counts


# ============================================================
# GET FULL NEWS DETAIL
# ============================================================

def get_published_news_by_id(
    news_id,
):

    news_item = find_news_by_id(
        news_id
    )

    if not news_item:
        return None

    if news_item.status != "PUBLISHED":
        return None

    return news_item