import time
import googletrans
import pandas as pd
import ast

from scipy import sparse

from Dictionary import subdistricts_chiang_mai_th as subd_cm_th
from Dictionary import subdistricts_chiang_mai_en as subd_cm_en
from Dictionary import bakery_list as bakery_list
from Dictionary import bakery_list_no_space as non_space_bakery_list
from Dictionary import review_th_positive as th_positive
from Dictionary import review_th_negative as th_negative
from Dictionary import review_en_positive as en_positive
from Dictionary import review_en_negative as en_negative

import demoji
import re
translator = googletrans.Translator()

def remove_thai_word(text):
    text = text.replace('ตำบล', ' ')
    text = text.replace('อำเภอ', ' ')
    text = text.replace('ซอย', ' ')
    text = text.replace('ถนน', ' ')
    text = text.replace('และ', ' ')
    text = text.replace('หรือ', ' ')
    text = text.replace(',', ' ')
    text = text.replace('ต.', ' ')
    text = text.replace('ถ.', ' ')
    text = text.replace('จ.', ' ')
    text = text.replace('อ.', ' ')
    return text


def get_and_extract_and_translate_address_data(input_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    for index, row in df.iterrows():
        district_found = []
        thai_address = row['address']
        thai_address = remove_thai_word(thai_address)
        for i in range(len(subd_cm_th)):
            if subd_cm_th[i] in thai_address:
                district_found.append(subd_cm_en[i])
        if len(district_found) < 1:
            df.at[index, 'address'] = ['Other']
        else:
            df.at[index, 'address'] = district_found
    df.to_csv(output_file, index=False)
    return df

def get_and_translate_menu_data(input_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    for index, row in df.iterrows():
        thai_menu = row['menu']
        if type(thai_menu) is not float:
            thai_menu = ast.literal_eval(thai_menu)
            updated_thai_menu = [word.replace('\n', '') for word in thai_menu]
            updated_thai_menu = [re.sub(r'[0-9!?,฿]', '', word) for word in updated_thai_menu]
            updated_thai_menu = [demoji.replace(word, '') for word in updated_thai_menu]
        else:
            updated_thai_menu = ['N/A']
        eng_menu = []
        for item in updated_thai_menu:
            while True:
                try:
                    translation = translator.translate(item, dest='en')
                    eng_menu.append(translation.text)
                    break
                except TypeError:
                    print("TypeError occurred. Retrying in 2 seconds...")
                    time.sleep(1)
        eng_menu = [word.lower() for word in eng_menu]
        df.at[index, 'menu'] = eng_menu
    df.to_csv(output_file, index=False)
    return df

def get_and_extract_menu_data(input_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    for index, row in df.iterrows():
        menu_found = []
        menu_list = row['menu']
        menu_list = ast.literal_eval(menu_list)
        for menu in menu_list:
            for i in range(len(bakery_list)):
                if bakery_list[i] in menu:
                    menu_found.append(non_space_bakery_list[i])
        menu_found = list(set(menu_found))
        if len(menu_found) < 1:
            df.at[index, 'menu'] = ['No bakery related menu']
        else:
            df.at[index, 'menu'] = menu_found
    df.to_csv(output_file, index=False)
    return df

def get_and_extract_review_data(input_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    for index, row in df.iterrows():
        thai_reviews = row['review']
        eng_reviews = []
        if type(thai_reviews) is not float:
            thai_reviews = ast.literal_eval(thai_reviews)
            for reviews in thai_reviews:
                reviews = remove_thai_word(reviews)
                review_split = re.split(r'\s+(?=[ก-ฮเ-์]+)', reviews)
                for review in review_split:
                    eng_review = []
                    for i in range(len(th_positive)):
                        if th_positive[i] in review:
                            if th_negative[i] in review:
                                eng_review.append(en_negative[i])
                            else:
                                eng_review.append(en_positive[i])
                    eng_review = list(set(eng_review))
                    eng_reviews.append(eng_review)
        else:
            eng_reviews = ['no review']
        eng_reviews = [review for review in eng_reviews if review]
        df.at[index, 'review'] = eng_reviews
    df.to_csv(output_file, index=False)
    return df

def combined_and_create_csv(input_file, address_file, menu_file, review_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    address_df = pd.read_csv(address_file, encoding='utf-8')
    menu_df = pd.read_csv(menu_file, encoding='utf-8')
    review_df = pd.read_csv(review_file, encoding='utf-8')
    df['address'] = address_df['address']
    df['menu'] = menu_df['menu']
    df['review'] = review_df['review']
    df.to_csv(output_file, index=False)
    return df

def create_a_feature_table(input_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    feature_address_df = pd.read_csv('../Material/features_address.csv', encoding='utf-8')
    feature_menu_df = pd.read_csv('../Material/features_menu.csv', encoding='utf-8')
    feature_review_df = pd.read_csv('../Material/features_review.csv', encoding='utf-8')
    df = df.drop(['menu', 'review', 'address'], axis=1)
    df = pd.merge(df, feature_address_df, left_index=True, right_index=True)
    df = pd.merge(df, feature_menu_df, left_index=True, right_index=True)
    df = pd.merge(df, feature_review_df, left_index=True, right_index=True)
    df.to_csv(output_file, index=False)
    return df

if __name__ == '__main__':
    # get_and_extract_and_translate_address_data('../Material/untranslated_bakery.csv', '../Material/translated_bakery_address.csv')
    # get_and_translate_menu_data('../Material/untranslated_bakery.csv', '../Material/translated_bakery_menu.csv')
    # get_and_extract_menu_data('../Material/translated_bakery_menu.csv', '../Material/translated_and_extract_bakery_menu.csv')
    # get_and_extract_review_data('../Material/untranslated_bakery.csv', '../Material/extracted_bakery_review.csv')
    # combined_and_create_csv('../Material/untranslated_bakery.csv', '../Material/translated_bakery_address.csv',
    #                         '../Material/translated_and_extract_bakery_menu.csv', '../Material/extracted_bakery_review.csv',
    #                         '../Material/cleaned_bakery.csv')
    print('')
