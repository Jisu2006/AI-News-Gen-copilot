from repositories.news_repository import (
    get_published_news,
    get_breaking_news,
    get_featured_news,
    get_latest_news,
    get_published_locations,
    get_published_category_counts,
)


CATEGORIES = [
    "Local News",
    "Accident",
    "Crime",
    "Sports",
    "Entertainment",
    "Education",
    "Technology",
    "Business",
    "Weather",
    "Politics",
    "Events",
    "Other",
]


def main():

    print("=" * 60)
    print("PUBLIC NEWS REPOSITORY TEST")
    print("=" * 60)

    latest = get_latest_news()

    breaking = get_breaking_news()

    featured = get_featured_news()

    locations = get_published_locations()

    category_counts = (
        get_published_category_counts(
            CATEGORIES
        )
    )

    print(
        f"Latest published news: {len(latest)}"
    )

    print(
        f"Breaking news: {len(breaking)}"
    )

    print(
        f"Featured news: {len(featured)}"
    )

    print(
        f"Published locations: {locations}"
    )

    print()
    print("Category counts:")

    for category, count in category_counts.items():

        print(
            f"  {category}: {count}"
        )

    print()
    print("=" * 60)
    print("PUBLIC NEWS REPOSITORY TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()