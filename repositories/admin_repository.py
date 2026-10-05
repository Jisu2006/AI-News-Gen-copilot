from database.mongo import (
    get_admin_actions_collection,
    get_users_collection,
    get_news_collection,
    get_next_id,
    utc_now,
)

from repositories.news_repository import (
    find_news_by_id,
    NewsDocument,
)


# ============================================================
# CREATE ADMIN ACTION
# ============================================================

def create_admin_action(
    admin_id,
    news_id,
    action: str,
    comment: str | None = None,
):
    """
    Store an administrative action in MongoDB.
    """

    admin_action_id = get_next_id(
        "admin_actions"
    )

    document = {
        "_id": admin_action_id,

        "admin_id": int(admin_id),

        "news_id": int(news_id),

        "action": action,

        "comment": comment,

        "created_at": utc_now(),
    }

    get_admin_actions_collection().insert_one(
        document
    )

    return document


# ============================================================
# GET NEWS BY STATUS
# ============================================================

def get_news_by_status(
    status: str,
    sort_field: str = "created_at",
    descending: bool = True,
    limit: int = 100,
):
    """
    Get news records by status.
    """

    sort_direction = -1 if descending else 1

    cursor = (
        get_news_collection()
        .find(
            {
                "status": status
            }
        )
        .sort(
            sort_field,
            sort_direction
        )
        .limit(limit)
    )

    return [
        NewsDocument(document)
        for document in cursor
    ]


# ============================================================
# GET RECENT ADMIN ACTIONS
# ============================================================

def get_recent_admin_actions(
    limit: int = 50,
):
    """
    Get recent admin actions and attach
    the corresponding admin user.
    """

    actions = list(
        get_admin_actions_collection()
        .find({})
        .sort(
            "created_at",
            -1
        )
        .limit(limit)
    )

    users = get_users_collection()

    result = []

    for action in actions:

        admin_user = users.find_one(
            {
                "_id": action.get(
                    "admin_id"
                )
            }
        )

        action["admin"] = (
            admin_user
            if admin_user
            else {
                "name": "Unknown Admin"
            }
        )

        result.append(
            action
        )

    return result


# ============================================================
# GET ADMIN DASHBOARD DATA
# ============================================================

def get_admin_dashboard_data():
    """
    Return all data required by admin dashboard.
    """

    pending_news = get_news_by_status(
        "PENDING_REVIEW",
        sort_field="created_at",
        descending=True,
    )

    approved_news = get_news_by_status(
        "APPROVED",
        sort_field="updated_at",
        descending=True,
    )

    published_news = get_news_by_status(
        "PUBLISHED",
        sort_field="published_at",
        descending=True,
    )

    admin_actions = get_recent_admin_actions(
        limit=50
    )

    return {
        "pending_news": pending_news,
        "approved_news": approved_news,
        "published_news": published_news,
        "admin_actions": admin_actions,
    }