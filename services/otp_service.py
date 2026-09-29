import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db
from models.database_models import User, OTPVerification
from services.email_service import send_otp_email

OTP_EXPIRY_MINUTES = 10
OTP_RESEND_COOLDOWN_SECONDS = 60
MAX_OTP_ATTEMPTS = 5


def generate_and_send_otp(email: str, otp_type: str = "registration", user_name: str = "User") -> tuple[bool, str]:
    """
    Generate a secure 6-digit OTP, hash and store it in database, and send via email.
    """
    email = email.strip().lower()

    # Check resend cooldown
    can_resend, cooldown_msg, _ = can_resend_otp(email, otp_type)
    if not can_resend:
        return False, cooldown_msg

    # Invalidate previous unused OTPs for this email and type
    OTPVerification.query.filter_by(
        email=email,
        otp_type=otp_type,
        used=False
    ).update({"used": True})

    # Generate 6-digit secure numeric OTP
    otp_code = f"{secrets.randbelow(900000) + 100000}"
    otp_hash = generate_password_hash(otp_code)

    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
    resend_available_at = now + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS)

    otp_record = OTPVerification(
        email=email,
        otp_hash=otp_hash,
        otp_type=otp_type,
        expires_at=expires_at,
        attempts=0,
        resend_available_at=resend_available_at,
        used=False
    )

    db.session.add(otp_record)
    db.session.commit()

    # Send email
    email_sent = send_otp_email(email, otp_code, user_name)

    if email_sent:
        return True, f"A 6-digit verification code has been sent to {email}."
    else:
        # If email fails (e.g. offline/no SMTP credentials in dev), return message
        return True, f"Verification code generated for {email}. (Note: Check email/spam folder)"


def verify_otp(email: str, entered_otp: str, otp_type: str = "registration") -> tuple[bool, str]:
    """
    Verify the entered OTP against the stored hash in database.
    """
    email = email.strip().lower()
    entered_otp = (entered_otp or "").strip()

    if not entered_otp or len(entered_otp) != 6 or not entered_otp.isdigit():
        return False, "Please enter a valid 6-digit OTP code."

    # Fetch the latest unused OTP record
    record = OTPVerification.query.filter_by(
        email=email,
        otp_type=otp_type,
        used=False
    ).order_by(OTPVerification.created_at.desc()).first()

    if not record:
        return False, "No active verification code found. Please request a new code."

    now = datetime.utcnow()

    # Check expiration
    if now > record.expires_at:
        record.used = True
        db.session.commit()
        return False, "Verification code has expired. Please request a new code."

    # Check attempt limit
    if record.attempts >= MAX_OTP_ATTEMPTS:
        record.used = True
        db.session.commit()
        return False, "Maximum verification attempts exceeded. Please request a new code."

    # Check OTP hash
    if check_password_hash(record.otp_hash, entered_otp):
        record.used = True

        # Update user verification status in database
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_verified = True
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()

        db.session.commit()
        return True, "Email verified successfully!"
    else:
        record.attempts += 1
        db.session.commit()
        remaining = MAX_OTP_ATTEMPTS - record.attempts
        if remaining > 0:
            return False, f"Incorrect verification code. {remaining} attempt(s) remaining."
        else:
            record.used = True
            db.session.commit()
            return False, "Maximum verification attempts exceeded. Please request a new code."


def can_resend_otp(email: str, otp_type: str = "registration") -> tuple[bool, str, int]:
    """
    Check if the user can request a resend of the OTP based on cooldown.
    """
    email = email.strip().lower()
    record = OTPVerification.query.filter_by(
        email=email,
        otp_type=otp_type,
        used=False
    ).order_by(OTPVerification.created_at.desc()).first()

    if not record:
        return True, "", 0

    now = datetime.utcnow()
    if now < record.resend_available_at:
        remaining_seconds = int((record.resend_available_at - now).total_seconds())
        return False, f"Please wait {remaining_seconds} seconds before requesting a new code.", remaining_seconds

    return True, "", 0
