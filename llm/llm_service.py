import os
import json
import re
import time

from google import genai
from dotenv import load_dotenv


load_dotenv()


class LLMService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured in .env"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

    # ==========================================================
    # GENERATE CONTENT
    # ==========================================================

    def generate(self, prompt):
        """
        Generate content from Gemini.

        Temporary API errors such as 503 are retried
        automatically before failing.
        """

        max_retries = 3

        for attempt in range(1, max_retries + 1):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return response.text

            except Exception as error:

                error_message = str(error)

                # Temporary Gemini/API errors
                temporary_errors = [
                    "429",
                    "500",
                    "502",
                    "503",
                    "504",
                    "UNAVAILABLE",
                    "RESOURCE_EXHAUSTED",
                    "INTERNAL"
                ]

                is_temporary_error = any(
                    error_code in error_message
                    for error_code in temporary_errors
                )

                # Retry temporary errors
                if is_temporary_error:

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retry attempt "
                        f"{attempt}/{max_retries}..."
                    )

                    # If this was the final attempt,
                    # stop retrying.
                    if attempt == max_retries:

                        raise RuntimeError(
                            "Gemini service is temporarily "
                            "unavailable after multiple "
                            "retry attempts."
                        )

                    # Increasing wait time:
                    # Attempt 1 → 2 seconds
                    # Attempt 2 → 4 seconds
                    time.sleep(2 * attempt)

                else:

                    # Do not retry permanent errors
                    raise

    # ==========================================================
    # GENERATE NEWS
    # ==========================================================

    def generate_news(self, prompt, allow_dates=False):
        """
        Generate structured news content from Gemini.

        Returns:
            dict: Validated AI-generated news data.

        allow_dates:
            False → AI must not generate dates
            True  → Dates are allowed because the user
                    provided an incident date.
        """

        response_text = self.generate(prompt)

        # ------------------------------------------------------
        # Clean Gemini response
        # ------------------------------------------------------

        response_text = response_text.strip()

        # Remove ```json
        if response_text.startswith("```json"):

            response_text = response_text[7:]

        # Remove ```
        elif response_text.startswith("```"):

            response_text = response_text[3:]

        # Remove closing ```
        if response_text.endswith("```"):

            response_text = response_text[:-3]

        response_text = response_text.strip()

        # ------------------------------------------------------
        # Convert JSON response into Python dictionary
        # ------------------------------------------------------

        try:

            news_data = json.loads(
                response_text
            )

        except json.JSONDecodeError as error:

            raise RuntimeError(
                f"Gemini returned invalid JSON: {error}"
            )

        # ------------------------------------------------------
        # Required fields
        # ------------------------------------------------------

        required_fields = [
            "headline",
            "subheading",
            "summary",
            "article",
            "key_facts",
            "tags"
        ]

        for field in required_fields:

            if field not in news_data:

                raise RuntimeError(
                    f"Gemini response is missing "
                    f"field: {field}"
                )

        # ------------------------------------------------------
        # Validate AI output
        # ------------------------------------------------------

        return validate_news_output(
            news_data,
            allow_dates=allow_dates
        )


# ==============================================================
# NEWS OUTPUT VALIDATION
# ==============================================================

def validate_news_output(news_data, allow_dates=False):
    """
    Validate AI-generated news content.

    Currently validates dates.

    If allow_dates=False:
        Any generated date is rejected.

    If allow_dates=True:
        Dates are allowed because the user provided
        an incident date.
    """

    # ----------------------------------------------------------
    # Combine AI-generated text
    # ----------------------------------------------------------

    combined_text = " ".join([
        str(
            news_data.get(
                "headline",
                ""
            )
        ),

        str(
            news_data.get(
                "subheading",
                ""
            )
        ),

        str(
            news_data.get(
                "summary",
                ""
            )
        ),

        str(
            news_data.get(
                "article",
                ""
            )
        ),

        " ".join(
            str(fact)
            for fact in news_data.get(
                "key_facts",
                []
            )
        )
    ])

    # ----------------------------------------------------------
    # Date validation
    # ----------------------------------------------------------

    # Only check dates when the user did NOT
    # provide an incident date.
    if not allow_dates:

        date_patterns = [

            # Example:
            # September 4, 2026
            (
                r'\b(?:January|February|March|April|May|June|'
                r'July|August|September|October|November|'
                r'December)\s+\d{1,2},\s+\d{4}\b'
            ),

            # Example:
            # 04/09/2026
            # 04-09-2026
            (
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
            ),

            # Example:
            # 2026/09/04
            # 2026-09-04
            (
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
            ),

            # Example:
            # September 2026
            (
                r'\b(?:January|February|March|April|May|June|'
                r'July|August|September|October|November|'
                r'December)\s+\d{4}\b'
            ),
        ]

        for pattern in date_patterns:

            if re.search(
                pattern,
                combined_text,
                re.IGNORECASE
            ):

                raise RuntimeError(
                    "AI draft contains an unsupported date. "
                    "The user did not provide an incident date."
                )

    # ----------------------------------------------------------
    # Validation successful
    # ----------------------------------------------------------

    return news_data