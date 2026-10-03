import secrets
from datetime import timedelta

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from database.mongo import (
    get_otp_collection,
    get_users_collection,
    get_next_id,
    utc_now,
)

from services.email_service import send_otp_email


OTP_EXPIRY_MINUTES = 10
OTP_RESEND_COOLDOWN_SECONDS = 60
MAX_OTP_ATTEMPTS = 5


# ============================================================
# GENERATE + SEND OTP
# ============================================================

def generate_and_send_otp(
    email: str,
    otp_type: str = "registration",
    user_name: str = "User",
) -> tuple[bool, str]:

    email = email.strip().lower()

    otp_collection = get_otp_collection()

    # --------------------------------------------------------
    # Check resend cooldown
    # --------------------------------------------------------

    can_resend, cooldown_msg, _ = can_resend_otp(
        email,
        otp_type
    )

    if not can_resend:
        return False, cooldown_msg

    # --------------------------------------------------------
    # Invalidate previous OTPs
    # --------------------------------------------------------

    otp_collection.update_many(
        {
            "email": email,
            "otp_type": otp_type,
            "used": False,
        },
        {
            "$set": {
                "used": True
            }
        },
    )

    # --------------------------------------------------------
    # Generate OTP
    # --------------------------------------------------------

    otp_code = str(
        secrets.randbelow(900000) + 100000
    )

    otp_hash = generate_password_hash(
        otp_code
    )

    now = utc_now()

    expires_at = (
        now +
        timedelta(minutes=OTP_EXPIRY_MINUTES)
    )

    resend_available_at = (
        now +
        timedelta(
            seconds=OTP_RESEND_COOLDOWN_SECONDS
        )
    )

    # --------------------------------------------------------
    # Store OTP in MongoDB
    # --------------------------------------------------------

    otp_document = {
        "_id": get_next_id("otp_verifications"),

        "email": email,

        "otp_hash": otp_hash,

        "otp_type": otp_type,

        "expires_at": expires_at,

        "attempts": 0,

        "resend_available_at": resend_available_at,

        "used": False,

        "metadata": {},

        "created_at": now,
    }

    otp_collection.insert_one(
        otp_document
    )

    # --------------------------------------------------------
    # Send OTP email
    # --------------------------------------------------------

    email_sent = send_otp_email(
        email,
        otp_code,
        user_name
    )

    if email_sent:
        return (
            True,
            f"A 6-digit verification code has been sent to {email}."
        )

    # Email failed
    return (
        False,
        "OTP was generated, but the email could not be sent. "
        "Please check your email configuration and try again."
    )


# ============================================================
# VERIFY OTP
# ============================================================

def verify_otp(
    email: str,
    entered_otp: str,
    otp_type: str = "registration",
) -> tuple[bool, str]:

    email = email.strip().lower()
    entered_otp = (entered_otp or "").strip()

    if (
        not entered_otp
        or len(entered_otp) != 6
        or not entered_otp.isdigit()
    ):
        return (
            False,
            "Please enter a valid 6-digit OTP code."
        )

    otp_collection = get_otp_collection()

    # --------------------------------------------------------
    # Find latest unused OTP
    # --------------------------------------------------------

    record = otp_collection.find_one(
        {
            "email": email,
            "otp_type": otp_type,
            "used": False,
        },
        sort=[
            ("created_at", -1)
        ],
    )

    if not record:
        return (
            False,
            "No active verification code found. "
            "Please request a new code."
        )

    now = utc_now()

    # --------------------------------------------------------
    # Check expiration
    # --------------------------------------------------------

    if now > record["expires_at"]:

        otp_collection.update_one(
            {
                "_id": record["_id"]
            },
            {
                "$set": {
                    "used": True
                }
            },
        )

        return (
            False,
            "Verification code has expired. "
            "Please request a new code."
        )

    # --------------------------------------------------------
    # Check attempts
    # --------------------------------------------------------

    if record["attempts"] >= MAX_OTP_ATTEMPTS:

        otp_collection.update_one(
            {
                "_id": record["_id"]
            },
            {
                "$set": {
                    "used": True
                }
            },
        )

        return (
            False,
            "Maximum verification attempts exceeded. "
            "Please request a new code."
        )

    # --------------------------------------------------------
    # Check OTP hash
    # --------------------------------------------------------

    if check_password_hash(
        record["otp_hash"],
        entered_otp
    ):

        # Mark OTP used
        otp_collection.update_one(
            {
                "_id": record["_id"]
            },
            {
                "$set": {
                    "used": True
                }
            },
        )

        # ----------------------------------------------------
        # Verify user in MongoDB
        # ----------------------------------------------------

        users = get_users_collection()

        result = users.update_one(
            {
                "email": email
            },
            {
                "$set": {
                    "is_verified": True,
                    "email_verified": True,
                    "email_verified_at": now,
                    "updated_at": now,
                }
            },
        )

        if result.matched_count == 0:
            return (
                False,
                "User account was not found."
            )

        return (
            True,
            "Email verified successfully!"
        )

    # --------------------------------------------------------
    # Incorrect OTP
    # --------------------------------------------------------

    new_attempts = record["attempts"] + 1

    update_data = {
        "$set": {
            "attempts": new_attempts
        }
    }

    if new_attempts >= MAX_OTP_ATTEMPTS:
        update_data["$set"]["used"] = True

    otp_collection.update_one(
        {
            "_id": record["_id"]
        },
        update_data,
    )

    remaining = (
        MAX_OTP_ATTEMPTS -
        new_attempts
    )

    if remaining > 0:
        return (
            False,
            f"Incorrect verification code. "
            f"{remaining} attempt(s) remaining."
        )

    return (
        False,
        "Maximum verification attempts exceeded. "
        "Please request a new code."
    )


# ============================================================
# CHECK RESEND COOLDOWN
# ============================================================

def can_resend_otp(
    email: str,
    otp_type: str = "registration",
) -> tuple[bool, str, int]:

    email = email.strip().lower()

    record = get_otp_collection().find_one(
        {
            "email": email,
            "otp_type": otp_type,
            "used": False,
        },
        sort=[
            ("created_at", -1)
        ],
    )

    if not record:
        return True, "", 0

    now = utc_now()

    resend_available_at = record.get(
        "resend_available_at"
    )

    if (
        resend_available_at
        and now < resend_available_at
    ):

        remaining_seconds = int(
            (
                resend_available_at -
                now
            ).total_seconds()
        )

        return (
            False,
            f"Please wait {remaining_seconds} "
            f"seconds before requesting a new code.",
            remaining_seconds,
        )

    return True, "", 0