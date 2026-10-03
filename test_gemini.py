import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# VALIDATE API KEY
# ============================================================

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from .env"
    )


# ============================================================
# CREATE CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# TEST REQUEST
# ============================================================

try:

    response = client.models.generate_content(
        model=MODEL,
        contents=(
            "Reply with exactly: "
            "GEMINI_CONNECTION_SUCCESS"
        ),
    )

    print("=" * 60)
    print("GEMINI API TEST")
    print("=" * 60)

    print(
        "Model:",
        MODEL
    )

    print(
        "Response:",
        response.text
    )

    print("=" * 60)
    print("Gemini API connection: SUCCESS")
    print("=" * 60)

except Exception as error:

    print("=" * 60)
    print("Gemini API connection: FAILED")
    print("=" * 60)

    print(error)

    print("=" * 60)