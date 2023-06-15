import ast
import os
import unittest

import numpy as np
import pandas.core.frame

from CSVCleaner import remove_thai_word
import pandas as pd
from CSVCleaner import get_and_extract_address_data
from CSVCleaner import get_and_translate_menu_data
from CSVCleaner import get_and_extract_menu_data
from CSVCleaner import get_and_extract_review_data
from CSVCleaner import combined_and_create_csv
from CSVtotxt import get_and_become_text_data
class test_script_remove_thai_word(unittest.TestCase):
    def test_remove_thai_word_one(self):
        # Test data
        input_text = "335 มูลเมือง ซอย9 ต.ศรีภูมิ อ.เมือง จ.เชียงใหม่ 50200 เชียงใหม่ (ซอยหลังก๊วยเตี๋ยวรสเยี่ยม แจ่งศรีภูมิ (เข้า มูลเมือง ซอย9 30 เมตร และ เลี้ยวขวา))"
        # Invoke the method to be tested
        result = remove_thai_word(input_text)
        # Verify the results
        expected = "335 มูลเมือง  9  ศรีภูมิ  เมือง  เชียงใหม่ 50200 เชียงใหม่ ( หลังก๊วยเตี๋ยวรสเยี่ยม แจ่งศรีภูมิ (เข้า มูลเมือง  9 30 เมตร   เลี้ยวขวา))"
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected)

    def test_remove_thai_word_two(self):
        # Test data
        input_text = "อ. จ. ถนน และ ตำบล, หรือ ซอย"
        result = remove_thai_word(input_text)
        self.assertIsInstance(result, str)
        expected = "              "
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()