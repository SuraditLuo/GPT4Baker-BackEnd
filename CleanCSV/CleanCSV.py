import time
import googletrans
import pandas as pd
import ast
from Dictionary import subdistricts_chiang_mai_th as subd_cm_th
from Dictionary import subdistricts_chiang_mai_en as subd_cm_en
from Dictionary import bakery_list as bakery_list
from Dictionary import review_th_positive as th_positive
from Dictionary import review_th_negative as th_negative
from Dictionary import review_en_positive as en_positive
from Dictionary import review_en_negative as en_negative

import demoji
import re
translator = googletrans.Translator()

def remove_word(text):
    text = text.replace('ตำบล', ' ')
    text = text.replace('อำเภอ', ' ')
    text = text.replace('ซอย', ' ')
    text = text.replace('ถนน', ' ')
    text = text.replace('และ', ' ')
    text = text.replace('หรือ', ' ')
    text = text.replace(',', ' ')
    return text


def get_and_clean_address_data():
    df = pd.read_csv('../untranslated_bakery.csv', encoding='utf-8')
    for index, row in df.iterrows():
        district_found = []
        thai_address = row['address']
        thai_address = remove_word(thai_address)
        for i in range(len(subd_cm_th)):
            if subd_cm_th[i] in thai_address:
                district_found.append(subd_cm_en[i])
        print(thai_address)
        print('-> ', district_found)
        if len(district_found) < 1:
            df.at[index, 'address'] = ['Other']
        else:
            df.at[index, 'address'] = district_found
    df.to_csv('../translated_bakery_address.csv', index=False)

def get_and_translate_menu_data():
    df = pd.read_csv('../untranslated_bakery.csv', encoding='utf-8')
    for index, row in df.iterrows():
        thai_menu = row['menu']
        if type(thai_menu) is not float:
            #Convert sting type to list type
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
        print(eng_menu)
        df.at[index, 'menu'] = eng_menu
    df.to_csv('../translated_bakery_menu.csv', index=False)

def get_and_extract_menu_data():
    df = pd.read_csv('../translated_bakery_menu.csv', encoding='utf-8')
    print(bakery_list)
    for index, row in df.iterrows():
        menu_found = []
        menu_list = row['menu']
        menu_list = ast.literal_eval(menu_list)
        for menu in menu_list:
            for i in range(len(bakery_list)):
                if bakery_list[i] in menu:
                    menu_found.append(bakery_list[i])
        print(menu_list)
        # remove duplicated item
        menu_found = list(set(menu_found))
        print(len(menu_found))
        print('-> ', menu_found)
        if len(menu_found) < 1:
            df.at[index, 'menu'] = ['No bakery related menu']
        else:
            df.at[index, 'menu'] = menu_found
    df.to_csv('../translated_and_extract_bakery_menu.csv', index=False)

def get_and_extract_review_data():
    df = pd.read_csv('../untranslated_bakery.csv', encoding='utf-8')
    for index, row in df.iterrows():
        thai_reviews = row['review']
        eng_reviews = []
        if type(thai_reviews) is not float:
            thai_reviews = ast.literal_eval(thai_reviews)
            for reviews in thai_reviews:
                reviews = remove_word(reviews)
                review_split = re.split(r'\s+(?=[ก-ฮเ-์]+)', reviews)
                for review in review_split:
                    eng_review = []
                    for i in range (len(th_positive)):
                        if th_positive[i] in review:
                            if th_negative[i] in review:
                                eng_review.append(en_negative[i])
                            else:
                                eng_review.append(en_positive[i])
                    eng_review = list(set(eng_review))
                    eng_reviews.append(eng_review)
        else:
            eng_reviews = ['no review']
        # remove blank list
        eng_reviews = [review for review in eng_reviews if review]
        df.at[index, 'review'] = eng_reviews
    df.to_csv('../extracted_bakery_review.csv', index=False)
def combined_and_create_csv():
    df = pd.read_csv('../untranslated_bakery.csv', encoding='utf-8')
    address_df = pd.read_csv('../translated_bakery_address.csv', encoding='utf-8')
    menu_df = pd.read_csv('../translated_and_extract_bakery_menu.csv', encoding='utf-8')
    review_df = pd.read_csv('../extracted_bakery_review.csv', encoding='utf-8')
    df['address'] = address_df['address']
    df['menu'] = menu_df['menu']
    df['review'] = review_df['review']
    df.to_csv('cleaned_bakery.csv', index=False)
if __name__ == '__main__':
    # get_and_clean_address_data()
    # get_and_clean_menu_data()
    # get_and_translate_menu_data()
    # get_and_extract_menu_data()
    # get_and_extract_review_data()
    combined_and_create_csv()