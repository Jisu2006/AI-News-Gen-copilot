from pymongo import ReturnDocument

from database.mongo import (
    get_users_collection,
    get_next_id,
    utc_now,
)


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    name: str,
    email: str,
    password_hash: str,
    role: str = "user",
    is_verified: bool = False,
):
    """
    Create a new user in MongoDB.
    """

    users = get_users_collection()

    now = utc_now()
    user_id = get_next_id("users")

    user_document = {
        "_id": user_id,
        "name": name.strip(),
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "role": role,

        "is_verified": is_verified,
        "email_verified": is_verified,
        "email_verified_at": now if is_verified else None,

        "verification_token": None,
        "verification_token_expiry": None,

        "reset_token": None,
        "reset_token_expiry": None,

        "google_id": None,
        "mobile_number": None,

        "created_at": now,
        "updated_at": now,
    }

    users.insert_one(user_document)

    return user_document


# ============================================================
# FIND USER BY EMAIL
# ============================================================

def find_user_by_email(email: str):
    """
    Find user by email.
    """

    if not email:
        return None

    return get_users_collection().find_one(
        {
            "email": email.strip().lower()
        }
    )


# ============================================================
# FIND USER BY ID
# ============================================================

def find_user_by_id(user_id):
    """
    Find user by integer ID.
    """

    if user_id is None:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    return get_users_collection().find_one(
        {
            "_id": user_id
        }
    )


# ============================================================
# UPDATE USER
# ============================================================

def update_user(user_id, update_data: dict):
    """
    Update user fields.
    """

    if user_id is None or not update_data:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    update_data = dict(update_data)
    update_data["updated_at"] = utc_now()

    return get_users_collection().find_one_and_update(
        {
            "_id": user_id
        },
        {
            "$set": update_data
        },
        return_document=ReturnDocument.AFTER,
    )


# ============================================================
# VERIFY USER EMAIL
# ============================================================

def verify_user_email(email: str):
    """
    Mark user's email as verified.
    """

    user = find_user_by_email(email)

    if not user:
        return None

    now = utc_now()

    return get_users_collection().find_one_and_update(
        {
            "_id": user["_id"]
        },
        {
            "$set": {
                "is_verified": True,
                "email_verified": True,
                "email_verified_at": now,
                "updated_at": now,
            }
        },
        return_document=ReturnDocument.AFTER,
    )


# ============================================================
# UPDATE REGISTRATION DETAILS
# ============================================================

def update_registration_details(
    email: str,
    name: str,
    password_hash: str,
):
    """
    Update an existing unverified user.
    """

    user = find_user_by_email(email)

    if not user:
        return None

    now = utc_now()

    return get_users_collection().find_one_and_update(
        {
            "_id": user["_id"],
            "is_verified": False,
        },
        {
            "$set": {
                "name": name.strip(),
                "password_hash": password_hash,
                "updated_at": now,
            }
        },
        return_document=ReturnDocument.AFTER,
    )


# ============================================================
# COUNT USERS
# ============================================================

def count_users():
    """
    Return total number of users.
    """

    return get_users_collection().count_documents({})