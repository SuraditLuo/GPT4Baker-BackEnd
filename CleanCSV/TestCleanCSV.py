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

# Extract keywords that include in our Chiang Mai address list (see in CleanCSV/Dictionary.py).
class test_script_get_and_extract_address_data(unittest.TestCase):
    def test_extract_address_data_one(self):
        result = get_and_extract_address_data('mock_data/unextract_address_sample.csv',
                                                            'mock_data/translated_address_sample.csv').iloc[0].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'address': [['Mueang_Chiang_Mai', 'Nong_Pa_Khrang', 'San_Kamphaeng']]
        })
        self.assertIsInstance(result, pandas.core.frame.DataFrame)
        self.assertTrue(result.equals(expected))
    # Address detail that doesn't include district or road
    def test_extract_address_data_two(self):
        result = get_and_extract_address_data('mock_data/unextract_address_sample.csv',
                                                            'mock_data/translated_address_sample.csv').iloc[1].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'address': [['Other']]
        })
        self.assertIsInstance(result, pandas.core.frame.DataFrame)
        self.assertTrue(result.equals(expected))

class test_script_get_and_translate_menu_data(unittest.TestCase):
    def test_translate_menu_data_one(self):
        result = get_and_translate_menu_data('mock_data/untranslate_menu_sample.csv',
                                             'mock_data/translated_menu_sample.csv').iloc[0].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'menu': [['coconut cake', 'coconut cream pie', 'mango', 'cheesecake brownies']]
        })
        self.assertIsInstance(result, pandas.core.frame.DataFrame)
        self.assertTrue(result.equals(expected))
    # Translate bakery shop that has no menu detail
    def test_translate_menu_data_two(self):
        result = get_and_translate_menu_data('mock_data/untranslate_menu_sample.csv',
                                             'mock_data/translated_menu_sample.csv').iloc[1].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'menu': [['n/a']]
        })
        self.assertIsInstance(result, pandas.core.frame.DataFrame)
        self.assertTrue(result.equals(expected))

# Extract keywords that include in our bakery dictionary (see in CleanCSV/Dictionary.py).
class test_script_get_and_extract_menu_data(unittest.TestCase):
    def test_extract_menu_data_one(self):
        result = get_and_extract_menu_data('mock_data/second_translated_menu_sample.csv',
                                             'mock_data/translated_extracted_menu_sample.csv').iloc[0].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'menu': [['brownie', 'cake', 'cheesecake', 'pie']]
        })
        self.assertTrue(result.equals(expected))
    # Bakery shop doesn't have menu detail
    def test_extract_menu_data_two(self):
        result = get_and_extract_menu_data('mock_data/second_translated_menu_sample.csv',
                                             'mock_data/translated_extracted_menu_sample.csv').iloc[1].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'menu': [['No bakery related menu']]
        })
        self.assertTrue(result.equals(expected))
    # Bakery shop doesn't have bakery related menu or keyword that include in our menu dictionary (see in CleanCSV/Dictionary.py).
    def test_extract_menu_data_three(self):
        result = get_and_extract_menu_data('mock_data/second_translated_menu_sample.csv',
                                           'mock_data/translated_extracted_menu_sample.csv').iloc[2].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'menu': [['No bakery related menu']]
        })
        self.assertTrue(result.equals(expected))

# Extract keywords that include in our Chiang Mai review (see in CleanCSV/Dictionary.py).
class test_script_get_and_extract_review_data(unittest.TestCase):
    def test_extract_review_data_one(self):
        result = get_and_extract_review_data('mock_data/unextract_review_sample.csv',
                                             'mock_data/extracted_review_sample.csv').iloc[0].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'review': [[['beautiful'], ['delicious'], ['good_atmosphere'], ['lovely'], ['worth']]]
        })
        self.assertIsInstance(result, pandas.core.frame.DataFrame)
        self.assertTrue(result.equals(expected))
    # no review
    def test_extract_review_data_two(self):
        result = get_and_extract_review_data('mock_data/unextract_review_sample.csv',
                                             'mock_data/extracted_review_sample.csv').iloc[1].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'review': [['no review']]
        })
        self.assertIsInstance(result, pandas.core.frame.DataFrame)
        self.assertTrue(result.equals(expected))
    # has review but no review keyword in our dictionary (see in CleanCSV/Dictionary.py).
    def test_extract_review_data_two(self):
        result = get_and_extract_review_data('mock_data/unextract_review_sample.csv',
                                             'mock_data/extracted_review_sample.csv').iloc[2].to_frame().T
        result = result.reset_index(drop=True)
        expected = pd.DataFrame({
            'review': [[]]
        })
        self.assertIsInstance(result, pandas.core.frame.DataFrame)
        self.assertTrue(result.equals(expected))

class test_script_combined_and_create_csv(unittest.TestCase):
    def test_combined_and_create_csv(self):
        result = combined_and_create_csv('mock_data/unclean_sample.csv','mock_data/translated_address_sample.csv',
                                         'mock_data/translated_extracted_menu_sample.csv', 'mock_data/extracted_review_sample.csv',
                                         'mock_data/clean_sample.csv')
        result = result.reset_index(drop=True)
        result['address'] = result['address'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        result['menu'] = result['menu'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        result['review'] = result['review'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        expected = pd.DataFrame({
            'address': [['Mueang_Chiang_Mai', 'Nong_Pa_Khrang', 'San_Kamphaeng'], ['Other'], np.NaN],
            'menu': [['brownie', 'cake', 'cheesecake', 'pie'], ['No bakery related menu'], ['No bakery related menu']],
            'review': [[['beautiful'], ['delicious'], ['good_atmosphere'], ['lovely'], ['worth']], ['no review'], []]
        })
        self.assertIsInstance(result, pandas.core.frame.DataFrame)
        self.assertTrue(result.equals(expected))

class test_script_get_csv_and_become_text_data(unittest.TestCase):
    def setUp(self):
        self.input_file = 'mock_data/cleaned_table_first_sample.csv'
        self.text_file = 'mock_data/first_formatted_text_file.txt'
    def test_csv_to_text_data_one(self):
        self.assertTrue(os.path.exists(self.input_file))
        get_and_become_text_data(self.input_file, self.text_file)
        self.assertTrue(os.path.exists(self.text_file))
        with open(self.text_file, 'r') as file:
            content = file.read()
            self.assertIsInstance(content, str)
    def tearDown(self):
        # Remove the text file after the test
        if os.path.exists(self.text_file):
            os.remove(self.text_file)


if __name__ == '__main__':
    unittest.main()