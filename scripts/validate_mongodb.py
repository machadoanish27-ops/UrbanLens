import sys

from app.db.settings import MongoSettings
from scripts.validate_data import DATASETS, NATURAL_KEYS, PROJECT_ROOT


def main() -> int:
    try:
        settings = MongoSettings.from_environment()
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    try:
        from pymongo import MongoClient
    except ImportError:
        print("Install project dependencies before running the MongoDB audit.", file=sys.stderr)
        return 2

    client = MongoClient(settings.uri)
    try:
        database = client[settings.database]
        for collection_name, relative_path in DATASETS.items():
            path = PROJECT_ROOT / "data" / relative_path
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                import csv

                expected = sum(1 for _ in csv.DictReader(stream))
            collection = database[collection_name]
            actual = collection.count_documents({})
            fields = NATURAL_KEYS.get(collection_name)
            if not fields:
                print(f"{collection_name}: csv_expected={expected}, mongo_actual={actual}, duplicate_natural_keys=not_configured")
                continue
            group_key = {field: f"${field}" for field in fields}
            duplicates = list(
                collection.aggregate(
                    [
                        {"$group": {"_id": group_key, "count": {"$sum": 1}}},
                        {"$match": {"count": {"$gt": 1}}},
                        {"$count": "duplicate_keys"},
                    ]
                )
            )
            duplicate_count = duplicates[0]["duplicate_keys"] if duplicates else 0
            print(
                f"{collection_name}: csv_expected={expected}, mongo_actual={actual}, "
                f"duplicate_natural_keys={duplicate_count}"
            )
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())