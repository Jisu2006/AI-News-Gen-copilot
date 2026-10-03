from repositories.news_repository import (
    create_news,
    find_news_by_id,
    find_news_by_user,
    update_news,
    count_user_news,
    count_user_news_by_status,
)


def main():

    print("=" * 60)
    print("NEWS REPOSITORY TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Create test news
    # --------------------------------------------------------

    news = create_news(
        user_id=1,
        category="Test",
        title="MongoDB Test News",
        location="Test Location",
        incident_date="2026-10-03",
        incident_time="10:30:00",
        bullet_points="This is a MongoDB repository test.",
        additional_description="Testing news insertion.",
        source_url="https://example.com",
        supporting_information="Test supporting information.",
        status="DRAFT",
    )

    print("News inserted successfully.")
    print(f"News ID: {news.id}")
    print(f"Title: {news.title}")
    print(f"Status: {news.status}")

    # --------------------------------------------------------
    # Find by ID
    # --------------------------------------------------------

    found = find_news_by_id(
        news.id
    )

    print()
    print("Find by ID:")
    print(found)

    # --------------------------------------------------------
    # Update news
    # --------------------------------------------------------

    updated = update_news(
        news.id,
        {
            "status": "PENDING_REVIEW",
            "ai_headline": "MongoDB Test Headline",
            "key_facts": [
                "Test fact 1",
                "Test fact 2",
            ],
            "tags": [
                "test",
                "mongodb",
            ],
        }
    )

    print()
    print("Updated news:")
    print(updated)

    # --------------------------------------------------------
    # Find user news
    # --------------------------------------------------------

    user_news = find_news_by_user(
        1
    )

    print()
    print(
        f"User 1 news count: {len(user_news)}"
    )

    # --------------------------------------------------------
    # Counts
    # --------------------------------------------------------

    print()
    print(
        "Total user news:",
        count_user_news(1)
    )

    print(
        "Pending review:",
        count_user_news_by_status(
            1,
            "PENDING_REVIEW"
        )
    )

    print()
    print("=" * 60)
    print("NEWS REPOSITORY TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()