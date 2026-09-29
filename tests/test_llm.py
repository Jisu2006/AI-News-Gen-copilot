import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from models.database_models import News
from llm.news_generator import generate_news_draft


with app.app_context():

    news = News.query.first()

    if not news:
        print("No news found in database.")
        exit()

    print("\nOriginal News:")
    print("Title:", news.title)
    print("Category:", news.category)
    print("Location:", news.location)
    print("Bullet Points:", news.bullet_points)

    print("\nGenerating AI News Draft...\n")

    result = generate_news_draft(news)

    print("========== AI NEWS DRAFT ==========\n")

    print("HEADLINE:")
    print(result["headline"])

    print("\nSUBHEADING:")
    print(result["subheading"])

    print("\nSUMMARY:")
    print(result["summary"])

    print("\nARTICLE:")
    print(result["article"])

    print("\nKEY FACTS:")
    for fact in result["key_facts"]:
        print("-", fact)

    print("\nTAGS:")
    for tag in result["tags"]:
        print("-", tag)

    print("\n===================================")