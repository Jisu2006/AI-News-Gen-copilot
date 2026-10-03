from werkzeug.security import generate_password_hash

from repositories.user_repository import (
    create_user,
    find_user_by_email,
    find_user_by_id,
    count_users,
)


def main():

    print("=" * 60)
    print("USER REPOSITORY TEST")
    print("=" * 60)

    email = "mongo-test-user@example.com"

    existing = find_user_by_email(email)

    if existing:
        print("Test user already exists.")
        print(f"User ID: {existing['_id']}")
        print(f"Email: {existing['email']}")
        print("=" * 60)
        return

    password_hash = generate_password_hash(
        "TestPassword123"
    )

    user = create_user(
        name="Mongo Test User",
        email=email,
        password_hash=password_hash,
        role="user",
        is_verified=False,
    )

    print("User inserted successfully.")
    print(f"User ID: {user['_id']}")
    print(f"Name: {user['name']}")
    print(f"Email: {user['email']}")
    print(f"Role: {user['role']}")

    found_by_email = find_user_by_email(email)

    print()
    print("Find by email:")
    print(found_by_email)

    found_by_id = find_user_by_id(user["_id"])

    print()
    print("Find by ID:")
    print(found_by_id)

    print()
    print(f"Total users: {count_users()}")

    print()
    print("=" * 60)
    print("USER REPOSITORY TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()