"""Compatibility entry point for the resumable UrbanLens ETL."""

from etl.mongodb_import import main


if __name__ == "__main__":
    raise SystemExit(main())