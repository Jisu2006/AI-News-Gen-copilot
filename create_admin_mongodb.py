from getpass import getpass

from werkzeug.security import generate_password_hash

from database.mongo import (
    get_users_collection,
    get_next_id,
    utc_now,
)


def main():

    print("=" * 60)
    print("CREATE / UPDATE MONGODB ADMIN")
    print("=" * 60)

    # --------------------------------------------------------
    # Admin credentials
    # --------------------------------------------------------

    email = input(
        "Admin email [jisu@gmail.com]: "
    ).strip().lower()

    if not email:
        email = "jisu@gmail.com"

    password = getpass(
        "Admin password [press Enter for Admin@12345]: "
    )

    if not password:
        password = "Admin@12345"

    name = input(
        "Admin name [Admin]: "
    ).strip()

    if not name:
        name = "Admin"

    # --------------------------------------------------------
    # Users collection
    # --------------------------------------------------------

    users = get_users_collection()

    existing_user = users.find_one(
        {
            "email": email
        }
    )

    # --------------------------------------------------------
    # Update existing user
    # --------------------------------------------------------

    if existing_user:

        users.update_one(
            {
                "_id": existing_user["_id"]
            },
            {
                "$set": {
                    "name": name,
                    "password_hash":
                        generate_password_hash(
                            password
                        ),
                    "role": "admin",
                    "is_verified": True,
                    "email_verified": True,
                    "email_verified_at": utc_now(),
                    "updated_at": utc_now(),
                }
            }
        )

        admin_id = existing_user["_id"]

        print()
        print("Existing account updated to ADMIN.")

    # --------------------------------------------------------
    # Create new admin
    # --------------------------------------------------------

    else:

        admin_id = get_next_id(
            "users"
        )

        now = utc_now()

        admin_document = {
            "_id": admin_id,

            "name": name,

            "email": email,

            "password_hash":
                generate_password_hash(
                    password
                ),

            "role": "admin",

            "is_verified": True,

            "email_verified": True,

            "email_verified_at": now,

            "verification_token": None,

            "verification_token_expiry": None,

            "reset_token": None,

            "reset_token_expiry": None,

            "google_id": None,

            "mobile_number": None,

            "created_at": now,

            "updated_at": now,
        }

        users.insert_one(
            admin_document
        )

        print()
        print("New ADMIN account created.")

    # --------------------------------------------------------
    # Verify
    # --------------------------------------------------------

    admin = users.find_one(
        {
            "_id": admin_id
        }
    )

    print()
    print("=" * 60)
    print("ADMIN ACCOUNT")
    print("=" * 60)

    print(
        "ID:",
        admin["_id"]
    )

    print(
        "Name:",
        admin["name"]
    )

    print(
        "Email:",
        admin["email"]
    )

    print(
        "Role:",
        admin["role"]
    )

    print(
        "Verified:",
        admin["is_verified"]
    )

    print("=" * 60)
    print("ADMIN SETUP COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()