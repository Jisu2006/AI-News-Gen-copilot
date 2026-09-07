from llm.llm_service import LLMService
from llm.prompts import build_news_prompt


def generate_news_draft(news):
    """
    Generate and validate an AI news draft.

    The incident date is passed to the LLM service so that
    date validation can behave according to the user's input.
    """

    # Build original news prompt
    prompt = build_news_prompt(news)

    # Check whether user actually provided an incident date
    allow_dates = news.incident_date is not None

    llm_service = LLMService()

    # ---------------------------------------------------------
    # First attempt
    # ---------------------------------------------------------

    try:

        result = llm_service.generate_news(
            prompt,
            allow_dates=allow_dates
        )

        return result

    except RuntimeError as error:

        error_message = str(error)

        # -----------------------------------------------------
        # If unsupported date was generated, retry once
        # -----------------------------------------------------

        if "unsupported date" in error_message.lower():

            print(
                "\nAI generated an unsupported date."
            )

            print(
                "Retrying Gemini with a stronger date restriction..."
            )

            retry_prompt = f"""
{prompt}

IMPORTANT CORRECTION:

The previous AI-generated draft contained a date that
was NOT provided by the user.

This is NOT allowed.

Generate the news draft again.

STRICT RULE:
The user did NOT provide an incident date.

Therefore, you MUST NOT include ANY date in:

- headline
- subheading
- summary
- article
- key_facts

Do NOT use today's date.
Do NOT infer a date.
Do NOT assume a date.
Do NOT create a date.

Use ONLY the information explicitly provided by the user.

Return ONLY valid JSON with these fields:

headline
subheading
summary
article
key_facts
tags
"""

            # Second attempt
            result = llm_service.generate_news(
                retry_prompt,
                allow_dates=False
            )

            return result

        # -----------------------------------------------------
        # Other errors
        # -----------------------------------------------------

        raise