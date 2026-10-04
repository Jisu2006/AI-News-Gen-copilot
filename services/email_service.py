import os
import smtplib
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import Config


# ============================================================
# EMAILJS CONFIGURATION
# ============================================================

EMAILJS_API_URL = (
    "https://api.emailjs.com/api/v1.0/email/send"
)

EMAILJS_SERVICE_ID = os.getenv(
    "EMAILJS_SERVICE_ID",
    ""
).strip()

EMAILJS_TEMPLATE_ID = os.getenv(
    "EMAILJS_TEMPLATE_ID",
    ""
).strip()

EMAILJS_PUBLIC_KEY = os.getenv(
    "EMAILJS_PUBLIC_KEY",
    ""
).strip()

EMAILJS_PRIVATE_KEY = os.getenv(
    "EMAILJS_PRIVATE_KEY",
    ""
).strip()


def emailjs_configured() -> bool:
    """
    EmailJS is considered configured only when all
    required credentials are available.
    """

    return bool(
        EMAILJS_SERVICE_ID
        and
        EMAILJS_TEMPLATE_ID
        and
        EMAILJS_PUBLIC_KEY
        and
        EMAILJS_PRIVATE_KEY
    )


# ============================================================
# EMAILJS OTP EMAIL
# ============================================================

def send_otp_email_emailjs(
    to_email: str,
    otp_code: str,
    user_name: str = "User",
) -> bool:

    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,

        # Required for EmailJS strict server-side mode
        "accessToken": EMAILJS_PRIVATE_KEY,

        "template_params": {
            "to_email": to_email,
            "user_name": user_name,
            "otp_code": otp_code,
        },
    }

    try:

        response = requests.post(
            EMAILJS_API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=15,
        )

        if response.status_code == 200:

            print(
                "[EMAILJS] OTP email sent successfully."
            )

            return True

        print(
            "[EMAILJS ERROR] "
            f"HTTP {response.status_code}: "
            f"{response.text}"
        )

        return False

    except requests.RequestException as error:

        print(
            "[EMAILJS ERROR] "
            f"{type(error).__name__}: {error}"
        )

        return False

    except Exception as error:

        print(
            "[EMAILJS ERROR] "
            f"{type(error).__name__}: {error}"
        )

        return False


# ============================================================
# OLD SMTP FALLBACK
# ============================================================

def send_otp_email_smtp(
    to_email: str,
    otp_code: str,
    user_name: str = "User",
) -> bool:

    server_host = Config.MAIL_SERVER
    server_port = Config.MAIL_PORT
    username = Config.MAIL_USERNAME
    password = (
        Config.MAIL_PASSWORD or ""
    ).replace(" ", "").strip()

    sender_email = Config.MAIL_DEFAULT_SENDER

    if not username or not password:

        print(
            "[EMAIL WARNING] "
            "SMTP username or password is not configured."
        )

        return False

    subject = (
        "AI-NewsGen Copilot - Verify Your Email OTP"
    )

    text_content = f"""Hello {user_name},

Thank you for registering on AI-NewsGen Copilot.

Your One-Time Password (OTP) for email verification is:

{otp_code}

This OTP is valid for 10 minutes.

Please do not share this code with anyone.

If you did not request this verification, please ignore this email.

Regards,
AI-NewsGen Copilot Team
"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; background:#f5f7fb; padding:30px;">
    <div style="max-width:540px;margin:auto;background:white;padding:30px;border-radius:12px;">
        <h2 style="text-align:center;color:#4f46e5;">
            AI-NewsGen Copilot
        </h2>

        <p>Hello <strong>{user_name}</strong>,</p>

        <p>
            Thank you for registering on AI-NewsGen Copilot.
        </p>

        <p>Your verification OTP is:</p>

        <div style="
            font-size:32px;
            font-weight:bold;
            text-align:center;
            letter-spacing:8px;
            padding:20px;
            margin:20px 0;
            background:#f1f5f9;
            border-radius:10px;
            color:#4f46e5;
        ">
            {otp_code}
        </div>

        <p>
            This OTP is valid for 10 minutes.
        </p>

        <p>
            Please do not share this code with anyone.
        </p>

        <p>
            Regards,<br>
            AI-NewsGen Copilot Team
        </p>
    </div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")

    msg["Subject"] = subject
    msg["From"] = (
        f"AI-NewsGen Copilot <{sender_email}>"
    )
    msg["To"] = to_email

    msg.attach(
        MIMEText(
            text_content,
            "plain"
        )
    )

    msg.attach(
        MIMEText(
            html_content,
            "html"
        )
    )

    server = None

    try:

        if Config.MAIL_USE_TLS:

            server = smtplib.SMTP(
                server_host,
                server_port,
                timeout=12,
            )

            server.starttls()

        else:

            server = smtplib.SMTP(
                server_host,
                server_port,
                timeout=12,
            )

        server.login(
            username,
            password
        )

        server.sendmail(
            sender_email,
            [to_email],
            msg.as_string(),
        )

        print(
            "[SMTP] OTP email sent successfully."
        )

        return True

    except Exception as error:

        print(
            "[SMTP ERROR] "
            f"{type(error).__name__}: {error}"
        )

        return False

    finally:

        if server is not None:

            try:
                server.quit()
            except Exception:
                pass


# ============================================================
# MAIN OTP EMAIL FUNCTION
# ============================================================

def send_otp_email(
    to_email: str,
    otp_code: str,
    user_name: str = "User",
) -> bool:

    to_email = (
        to_email or ""
    ).strip()

    user_name = (
        user_name or "User"
    ).strip()

    otp_code = (
        otp_code or ""
    ).strip()

    if not to_email or not otp_code:

        print(
            "[EMAIL ERROR] "
            "Recipient email or OTP is missing."
        )

        return False

    # --------------------------------------------------------
    # EMAILJS FIRST
    # --------------------------------------------------------

    if emailjs_configured():

        print(
            "[EMAIL] Using EmailJS HTTPS API..."
        )

        emailjs_success = (
            send_otp_email_emailjs(
                to_email,
                otp_code,
                user_name,
            )
        )

        if emailjs_success:
            return True

        print(
            "[EMAIL] EmailJS failed. "
            "Trying SMTP fallback..."
        )

    else:

        print(
            "[EMAIL] EmailJS is not fully configured."
        )

    # --------------------------------------------------------
    # SMTP FALLBACK
    # --------------------------------------------------------

    return send_otp_email_smtp(
        to_email,
        otp_code,
        user_name,
    )