from repositories.engagement_repository import (
    increment_view_count,
    get_like_count,
    user_has_liked,
    toggle_like,
    create_comment,
    get_comment_count,
    get_comments,
)

from repositories.news_repository import (
    find_news_by_id,
)

from database.mongo import (
    get_news_collection,
)


def main():

    print("=" * 60)
    print("MONGODB ENGAGEMENT TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Automatically select a published news article
    # --------------------------------------------------------

    published_news = get_news_collection().find_one(
        {
            "status": "PUBLISHED"
        },
        sort=[
            ("_id", -1)
        ]
    )

    if not published_news:

        print("No published news found in MongoDB.")

        return

    news_id = published_news["_id"]

    user_id = 1

    news = find_news_by_id(
        news_id
    )

    if not news:

        print(
            f"News ID {news_id} not found."
        )

        return

    print(
        f"Testing News ID: {news_id}"
    )

    print(
        f"News Status: {news.status}"
    )

    # --------------------------------------------------------
    # View
    # --------------------------------------------------------

    result = increment_view_count(
        news_id
    )

    print(
        "View count:",
        result.get("views_count")
        if result
        else "FAILED"
    )

    # --------------------------------------------------------
    # Like
    # --------------------------------------------------------

    before_likes = get_like_count(
        news_id
    )

    print(
        "Likes before:",
        before_likes
    )

    was_liked = user_has_liked(
        news_id,
        user_id
    )

    print(
        "User already liked:",
        was_liked
    )

    like_result = toggle_like(
        news_id,
        user_id
    )

    print(
        "Like result:",
        like_result
    )

    # --------------------------------------------------------
    # Comment
    # --------------------------------------------------------

    comment = create_comment(
        news_id=news_id,
        user_id=user_id,
        comment_text="MongoDB engagement test comment.",
    )

    print(
        "Comment ID:",
        comment["_id"]
    )

    print(
        "Comment count:",
        get_comment_count(
            news_id
        )
    )

    # --------------------------------------------------------
    # Fetch comments
    # --------------------------------------------------------

    comments = get_comments(
        news_id
    )

    print(
        "Fetched comments:",
        len(comments)
    )

    print()
    print("=" * 60)
    print("MONGODB ENGAGEMENT TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()