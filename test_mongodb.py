from database.mongo import (
    test_mongo_connection,
    create_collections_and_indexes,
    get_mongo_db,
)


def main():
    print()
    print("=" * 60)
    print("MONGODB SETUP TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Test connection
    # --------------------------------------------------------

    if not test_mongo_connection():
        print("MongoDB connection failed.")
        return

    # --------------------------------------------------------
    # Create collections + indexes
    # --------------------------------------------------------

    create_collections_and_indexes()

    # --------------------------------------------------------
    # Show database information
    # --------------------------------------------------------

    db = get_mongo_db()

    collections = db.list_collection_names()

    print()
    print("=" * 60)
    print("AVAILABLE COLLECTIONS")
    print("=" * 60)

    for collection_name in sorted(collections):
        print(f" - {collection_name}")

    print()
    print("=" * 60)
    print("MONGODB SETUP COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()