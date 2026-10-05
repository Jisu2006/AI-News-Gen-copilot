import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from database.mongo import get_news_collection
from repositories.news_repository import NewsDocument
from llm.news_generator import generate_news_draft


with app.app_context():

    # --------------------------------------------------------
    # Get first news document from MongoDB
    # --------------------------------------------------------

    news_document = get_news_collection().find_one(
        {},
        sort=[("_id", 1)]
    )

    if not news_document:
        print("No news found in MongoDB.")
        sys.exit()

    # Convert MongoDB document into application NewsDocument
    news = NewsDocument(news_document)

    # --------------------------------------------------------
    # Display original news
    # --------------------------------------------------------

    print("\nOriginal News:")
    print("Title:", news.title)
    print("Category:", news.category)
    print("Location:", news.location)
    print("Bullet Points:", news.bullet_points)

    # --------------------------------------------------------
    # Generate AI News Draft
    # --------------------------------------------------------

    print("\nGenerating AI News Draft...\n")

    try:
        result = generate_news_draft(news)

    except Exception as error:
        print("AI NEWS GENERATION FAILED")
        print("Error:", error)
        sys.exit(1)

    # --------------------------------------------------------
    # Display generated result
    # --------------------------------------------------------

    print("========== AI NEWS DRAFT ==========\n")

    print("HEADLINE:")
    print(result.get("headline", ""))

    print("\nSUBHEADING:")
    print(result.get("subheading", ""))

    print("\nSUMMARY:")
    print(result.get("summary", ""))

    print("\nARTICLE:")
    print(result.get("article", ""))

    print("\nKEY FACTS:")

    for fact in result.get("key_facts", []):
        print("-", fact)

    print("\nTAGS:")

    for tag in result.get("tags", []):
        print("-", tag)

    print("\n===================================")