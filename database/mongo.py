import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import (
    ConfigurationError,
    PyMongoError,
    ServerSelectionTimeoutError,
)
from pymongo import ReturnDocument


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

INDIA_TZ = ZoneInfo("Asia/Kolkata")

# ============================================================
# MONGODB CONFIGURATION
# ============================================================

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv(
    "MONGO_DB_NAME",
    "ai_newsgen"
)


if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is missing from the .env file."
    )


# ============================================================
# MONGODB CLIENT
# ============================================================

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
    tz_aware=True,
    tzinfo=INDIA_TZ,
)


# ============================================================
# DATABASE
# ============================================================

mongo_db = client[MONGO_DB_NAME]


# ============================================================
# COLLECTION NAMES
# ============================================================

USERS_COLLECTION = "users"
NEWS_COLLECTION = "news"
ADMIN_ACTIONS_COLLECTION = "admin_actions"
OTP_COLLECTION = "otp_verifications"
COMMENTS_COLLECTION = "news_comments"
LIKES_COLLECTION = "news_likes"
COUNTERS_COLLECTION = "counters"


# ============================================================
# COLLECTION ACCESSORS
# ============================================================

def get_mongo_db():
    return mongo_db


def get_users_collection():
    return mongo_db[USERS_COLLECTION]


def get_news_collection():
    return mongo_db[NEWS_COLLECTION]


def get_admin_actions_collection():
    return mongo_db[ADMIN_ACTIONS_COLLECTION]


def get_otp_collection():
    return mongo_db[OTP_COLLECTION]


def get_comments_collection():
    return mongo_db[COMMENTS_COLLECTION]


def get_likes_collection():
    return mongo_db[LIKES_COLLECTION]


def get_counters_collection():
    return mongo_db[COUNTERS_COLLECTION]


# ============================================================
# UTC TIME HELPER
# ============================================================

def utc_now():
    """
    Return timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)


# ============================================================
# AUTO-INCREMENT ID
# ============================================================

def get_next_id(sequence_name: str) -> int:
    """
    Generate the next integer ID atomically.

    Example:
        get_next_id("users") -> 1
        get_next_id("users") -> 2
        get_next_id("news")  -> 1
    """

    result = get_counters_collection().find_one_and_update(
        {"_id": sequence_name},
        {
            "$inc": {
                "value": 1
            }
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    return int(result["value"])


# ============================================================
# CONNECTION TEST
# ============================================================

def test_mongo_connection():
    """
    Test MongoDB Atlas connection.
    """

    try:
        result = client.admin.command("ping")

        if result.get("ok") == 1:
            print("=" * 50)
            print("MongoDB Atlas Connection: SUCCESS")
            print(f"Database: {MONGO_DB_NAME}")
            print("=" * 50)
            return True

        print("MongoDB Atlas Connection: FAILED")
        print(f"Ping result: {result}")
        return False

    except ServerSelectionTimeoutError as error:
        print("=" * 50)
        print("MongoDB Connection FAILED")
        print("Reason: Server selection timeout")
        print(error)
        print("=" * 50)
        return False

    except ConfigurationError as error:
        print("=" * 50)
        print("MongoDB Configuration ERROR")
        print(error)
        print("=" * 50)
        return False

    except PyMongoError as error:
        print("=" * 50)
        print("MongoDB ERROR")
        print(error)
        print("=" * 50)
        return False

    except Exception as error:
        print("=" * 50)
        print("Unexpected MongoDB ERROR")
        print(error)
        print("=" * 50)
        return False


# ============================================================
# COLLECTIONS + INDEXES
# ============================================================

def create_collections_and_indexes():
    """
    Create required collections and indexes.
    """

    print()
    print("=" * 60)
    print("Creating MongoDB collections and indexes...")
    print("=" * 60)

    users = get_users_collection()
    news = get_news_collection()
    admin_actions = get_admin_actions_collection()
    otp = get_otp_collection()
    comments = get_comments_collection()
    likes = get_likes_collection()

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    users.create_index(
        "email",
        unique=True,
        name="unique_user_email"
    )

    users.create_index(
        "role",
        name="user_role_index"
    )

    # --------------------------------------------------------
    # NEWS
    # --------------------------------------------------------

    news.create_index(
        [
            ("status", 1),
            ("created_at", -1)
        ],
        name="news_status_created"
    )

    news.create_index(
        [
            ("status", 1),
            ("published_at", -1)
        ],
        name="news_status_published"
    )

    news.create_index(
        [
            ("category", 1),
            ("status", 1)
        ],
        name="news_category_status"
    )

    news.create_index(
        [
            ("location", 1),
            ("status", 1)
        ],
        name="news_location_status"
    )

    news.create_index(
        "user_id",
        name="news_user_id_index"
    )

    news.create_index(
        "is_breaking",
        name="news_breaking_index"
    )

    news.create_index(
        "is_featured",
        name="news_featured_index"
    )

    # --------------------------------------------------------
    # ADMIN ACTIONS
    # --------------------------------------------------------

    admin_actions.create_index(
        [
            ("news_id", 1),
            ("created_at", -1)
        ],
        name="admin_actions_news_created"
    )

    admin_actions.create_index(
        [
            ("admin_id", 1),
            ("created_at", -1)
        ],
        name="admin_actions_admin_created"
    )

    # --------------------------------------------------------
    # OTP
    # --------------------------------------------------------

    otp.create_index(
        [
            ("email", 1),
            ("otp_type", 1),
            ("created_at", -1)
        ],
        name="otp_email_type_created"
    )

    otp.create_index(
        "expires_at",
        name="otp_expiry_index"
    )

    # --------------------------------------------------------
    # COMMENTS
    # --------------------------------------------------------

    comments.create_index(
        [
            ("news_id", 1),
            ("created_at", -1)
        ],
        name="comments_news_created"
    )

    comments.create_index(
        "user_id",
        name="comments_user_index"
    )

    # --------------------------------------------------------
    # LIKES
    # --------------------------------------------------------

    likes.create_index(
        [
            ("news_id", 1),
            ("user_id", 1)
        ],
        unique=True,
        name="unique_news_user_like"
    )

    likes.create_index(
        "news_id",
        name="likes_news_index"
    )

    print("Users collection configured.")
    print("News collection configured.")
    print("Admin actions collection configured.")
    print("OTP collection configured.")
    print("Comments collection configured.")
    print("Likes collection configured.")
    print("Counters collection ready.")

    print()
    print("MongoDB collections and indexes created successfully.")
    print("=" * 60)