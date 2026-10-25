import tempfile
import unittest
from pathlib import Path

from etl.mongodb_import import (
    INSERT_ONLY_COLLECTIONS,
    NATURAL_KEYS,
    natural_key,
    scalar,
    validate_csv,
)


class MongoEtLTests(unittest.TestCase):
    def test_required_natural_keys_are_provider_specific(self) -> None:
        self.assertEqual(NATURAL_KEYS["city_aliases"], ("city_id", "normalized_alias"))
        self.assertEqual(NATURAL_KEYS["city_provider_identities"], ("provider", "provider_location_id"))
        self.assertEqual(
            NATURAL_KEYS["weather_observations"],
            ("city_id", "provider", "observed_at", "source_row"),
        )

    def test_weather_observations_are_insert_only(self) -> None:
        self.assertIn("weather_observations", INSERT_ONLY_COLLECTIONS)

    def test_numeric_conversion_keeps_negative_values(self) -> None:
        self.assertEqual(scalar("-7.5", "temperature_c"), -7.5)
        self.assertEqual(scalar("not available", "value"), None)

    def test_csv_preflight_rejects_duplicate_natural_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.csv"
            path.write_text(
                "city_id,normalized_alias\ncity_a,alias\ncity_a,alias\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate natural key"):
                validate_csv("city_aliases", path)

    def test_csv_preflight_counts_unkeyed_rows_without_fabricating_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.csv"
            path.write_text(
                "city_id,normalized_alias\ncity_a,alias\ncity_b,\n",
                encoding="utf-8",
            )
            stats = validate_csv("city_aliases", path)
            self.assertEqual(stats.total_rows, 2)
            self.assertEqual(stats.importable_rows, 1)
            self.assertEqual(stats.skipped_missing_key, 1)

    def test_natural_key_requires_all_fields(self) -> None:
        self.assertIsNone(natural_key("city_provider_identities", {"provider": "weather"}))


if __name__ == "__main__":
    unittest.main()