from repositories.admin_repository import (
    get_news_by_status,
    get_recent_admin_actions,
    get_admin_dashboard_data,
)


def main():

    print("=" * 60)
    print("ADMIN REPOSITORY TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Pending
    # --------------------------------------------------------

    pending = get_news_by_status(
        "PENDING_REVIEW"
    )

    print(
        f"Pending news: {len(pending)}"
    )

    # --------------------------------------------------------
    # Approved
    # --------------------------------------------------------

    approved = get_news_by_status(
        "APPROVED"
    )

    print(
        f"Approved news: {len(approved)}"
    )

    # --------------------------------------------------------
    # Published
    # --------------------------------------------------------

    published = get_news_by_status(
        "PUBLISHED"
    )

    print(
        f"Published news: {len(published)}"
    )

    # --------------------------------------------------------
    # Admin actions
    # --------------------------------------------------------

    actions = get_recent_admin_actions(
        50
    )

    print(
        f"Admin actions: {len(actions)}"
    )

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    dashboard = get_admin_dashboard_data()

    print()
    print(
        "Dashboard keys:",
        list(dashboard.keys())
    )

    print()
    print("=" * 60)
    print("ADMIN REPOSITORY TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()