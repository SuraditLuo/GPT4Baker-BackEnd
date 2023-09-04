import math
import unittest
from MongoConfig import time_range_to_list, rating_calc, popular_calc, get_preference


class TestTimeRangeToList(unittest.TestCase):
    # for time_range_to_list#
    def test_valid_time_range(self):
        # Test a valid time range
        time_range = "08:00 - 10:30"
        expected_result = ["08:00", "09:00", "10:00"]
        self.assertEqual(time_range_to_list(time_range), expected_result)

    def test_same_start_end_time(self):
        # Test a time range with the same start and end times
        time_range = "12:00 - 12:00"
        expected_result = ["12:00"]
        self.assertEqual(time_range_to_list(time_range), expected_result)

    def test_positive_rating_amt(self):
        # Test with a positive rating amount
        rating = 4.5
        rating_amt = 100
        name = "Bakery A"
        expected_result = {
            'name': name,
            'rating_score': 4.5 * math.log(100, 100)
        }
        self.assertEqual(rating_calc(rating, rating_amt, name), expected_result)

    # for rating_calc#
    def test_zero_rating_amt(self):
        # Test with a rating amount of 0
        rating = 3.0
        rating_amt = 0
        name = "Bakery B"
        expected_result = {
            'name': name,
            'rating_score': 0
        }
        self.assertEqual(rating_calc(rating, rating_amt, name), expected_result)

    def test_negative_rating_amt(self):
        # Test with a negative rating amount (should result in 0 rating score)
        rating = 4.5
        rating_amt = -10
        name = "Bakery A"
        expected_result = {
            'name': name,
            'rating_score': 0
        }

    # for popular_calc#
    def test_positive_values(self):
        # Test with positive check-in and bookmark values
        check_in = 100
        bookmark = 50
        name = "Bakery A"
        expected_result = {
            'name': name,
            'popularity_score': math.log(100, 10) + math.log(50, 50)
        }
        self.assertEqual(popular_calc(check_in, bookmark, name), expected_result)

    def test_zero_values(self):
        # Test with check-in and bookmark values of 0 (should result in log(1) for both)
        check_in = 0
        bookmark = 0
        name = "Bakery B"
        expected_result = {
            'name': name,
            'popularity_score': math.log(1, 10) + math.log(1, 50)
        }
        self.assertEqual(popular_calc(check_in, bookmark, name), expected_result)

    # for get_perference#
    def test_no_preference(self):
        # Test when both arguments are dictionaries
        is_for_kids = {'key': 'value'}
        is_for_group = {'key': 'value'}
        self.assertEqual(get_preference(is_for_kids, is_for_group), 'no_preference')

    def test_for_both(self):
        # Test when both arguments are booleans
        is_for_kids = True
        is_for_group = True
        self.assertEqual(get_preference(is_for_kids, is_for_group), 'for_both')

    def test_for_kids(self):
        # Test when is_for_kids is a boolean and is_for_group is a dictionary
        is_for_kids = True
        is_for_group = {'key': 'value'}
        self.assertEqual(get_preference(is_for_kids, is_for_group), 'for_kids')

    def test_for_group(self):
        # Test when is_for_kids is a dictionary and is_for_group is a boolean
        is_for_kids = {'key': 'value'}
        is_for_group = True
        self.assertEqual(get_preference(is_for_kids, is_for_group), 'for_group')

    def test_invalid_input(self):
        # Test when input does not match any expected case
        is_for_kids = {}
        is_for_group = {}
        self.assertEqual(get_preference(is_for_kids, is_for_group), 'no_preference')


if __name__ == '__main__':
    unittest.main()

