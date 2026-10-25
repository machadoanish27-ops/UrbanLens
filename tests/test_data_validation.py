import unittest

from scripts.validate_data import semantic_null, valid_coordinate, valid_percentage


class DataValidationTests(unittest.TestCase):
    def test_coordinate_bounds_are_checked(self) -> None:
        self.assertTrue(valid_coordinate("40.7", "-73.9"))
        self.assertFalse(valid_coordinate("91", "0"))
        self.assertFalse(valid_coordinate("0", "181"))

    def test_percentage_bounds_are_checked_without_rejecting_nulls(self) -> None:
        self.assertTrue(valid_percentage("0"))
        self.assertTrue(valid_percentage("100"))
        self.assertTrue(valid_percentage("75%"))
        self.assertTrue(valid_percentage(">75%"))
        self.assertTrue(valid_percentage("50% -< 75%"))
        self.assertFalse(valid_percentage("101"))
        self.assertFalse(valid_percentage(">105%"))
        self.assertTrue(valid_percentage("not available"))

    def test_semantic_null_detection(self) -> None:
        self.assertTrue(semantic_null(" N/A "))
        self.assertFalse(semantic_null("-4.5"))


if __name__ == "__main__":
    unittest.main()