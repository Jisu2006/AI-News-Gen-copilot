import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


class Config:

    # ========================================================
    # APPLICATION
    # ========================================================

    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY is missing from the .env file."
        )

    # ========================================================
    # MONGODB
    # ========================================================

    MONGO_URI = os.getenv("MONGO_URI")

    MONGO_DB_NAME = os.getenv(
        "MONGO_DB_NAME",
        "ai_newsgen"
    )

    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI is missing from the .env file."
        )

    # ========================================================
    # UPLOADS
    # ========================================================

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        str(
            BASE_DIR
            / "static"
            / "uploads"
        )
    )

    MAX_CONTENT_LENGTH = (
        110 * 1024 * 1024
    )

    # ========================================================
    # MAIL
    # ========================================================

    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(
        os.getenv(
            "MAIL_PORT",
            "587"
        )
    )

    MAIL_USE_TLS = os.getenv(
        "MAIL_USE_TLS",
        "True"
    ).lower() in (
        "true",
        "1",
        "t"
    )

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
        ""
    )

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD",
        ""
    )

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        MAIL_USERNAME or
        "ainewsgen.copilot@gmail.com"
    )

    # ========================================================
    # GEMINI
    # ========================================================

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        ""
    )

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash"
    )