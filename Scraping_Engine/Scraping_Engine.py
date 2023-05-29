import googletrans
from bs4 import BeautifulSoup as bs
from googletrans import Translator
import cloudscraper
import requests
import pandas as pd
from pymongo import MongoClient
import time

scraper = cloudscraper.create_scraper(delay=10, browser="chrome")
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}
def scrapingURL():
    page_number = 1
    base_url = 'https://www.wongnai.com/rankings'

    df = pd.DataFrame(columns=['name', 'url'])
    while True:
        url = f'{base_url}?category=24&region=373&page.size=500&page.number={page_number}'
        # Send the request to the URL
        response = scraper.get(url, headers=headers)
        if response.status_code == 200:
            # Parse the HTML using BeautifulSoup
            soup = bs(response.content, 'html.parser')

            # Scrape name
            name_results = soup.find_all(class_="bd20")
            name_list = [element.get_text() for element in name_results]
            # Scrape URL
            url_results = soup.find_all(class_="k0pvs2-0 sc-1bs98dy-0 hgwkbN ectdXQ")
            url_list = [element.get("href") for element in url_results]
            # # Scrape Rank
            # rank_results = soup.find_all(class_='text-gray-500 font-highlight rg16 rg14-mWeb')
            # rank_list = [element.get_text() for element in rank_results]
            # Append the scraped data to the main list
            for i in range(len(url_list)):
                name = name_list[i]
                url = url_list[i]
                # rank = rank_list[i]
                new_row = pd.DataFrame({'name': [name], 'url': [url]})
                df = pd.concat([df, new_row], ignore_index=True)
            # Check if there is a next page
            next_page_link = soup.find('button', {'class': 'sc-bdfBQB guRoDh'})
            if not next_page_link:
                break  # Exit the loop if there is no next page

            # Increment the page number for the next iteration
            page_number += 1
        else:
            print(f'Error accessing page {page_number}')
            break  # Exit the loop if there is an error accessing a page
    print("We got ", df['name'].str.len(), " bakeries shop.")
    #Convert to dataframe, then save it as a csv file
    print(df.to_markdown())
    #Drop the duplicated rows
    df_nonDupe = df.drop_duplicates(subset=['name'])
    # df_nonDupe = df_nonDupe[df_nonDupe['rank'].str.contains('ร้านเบเกอรี/เค้ก')]
    print(df_nonDupe.to_markdown())
    # df_nonDupe = df_nonDupe.drop('rank', axis=1)
    df_nonDupe.to_csv('url_dataset.csv', index=False)

def scrapingInfo():
    base_url = 'https://www.wongnai.com'
    bakeries = pd.read_csv('url_dataset.csv', encoding="ISO-8859-1")
    df = pd.DataFrame(columns=['name', 'rating', 'rating_amt', 'address', 'menu', 'review'])
    for i in range(len(bakeries)):
        try:
            url = f'{base_url}{bakeries.iloc[i, 1]}'
            response = scraper.get(url, headers=headers)
            if response.status_code == 200:
                soup = bs(response.content, 'html.parser')
                name = soup.find(class_="bd36 bd18-mWeb text-gray-700").get_text()
                rating_element = soup.find(class_='qkywve-1 dAZpcF bd48 text-gray-700')
                if rating_element is not None:
                    rating = float(rating_element.get_text())
                else:
                    rating = "N/A"
                rating_amt_text = soup.select_one('span.rg16.rg14-mWeb.font-highlight.text-gray-500 span:first-child').get_text()
                rating_amt = int(''.join(filter(str.isdigit, rating_amt_text)))
                address = soup.find('div', {'class': 'rg14'}).get_text()
                menu_element_list = soup.find_all(class_="StyledText-sc-s63irq eHtWye bd16 bd14-mWeb mb-2 mb-0-mWeb bd16 bd14-mWeb mb-2 mb-0-mWeb")
                if menu_element_list:
                    menus = [element.get_text() for element in menu_element_list]
                else:
                    menus = "N/A"
                review_element_list = soup.find_all('p', class_='sc-1gcav05-0 caARHI relative break-word text-gray-550 rg14')
                if review_element_list:
                    for review_element in review_element_list:
                        for a_element in review_element.find_all('a'):
                            a_element.extract()
                    reviews = [element.get_text(strip=True, separator=' ') for element in review_element_list]
                else:
                    reviews = "N/A"
                print('index ', i, ' name: ', name, ' rating: ', rating)
                new_row = pd.DataFrame({'name': [name], 'rating': [rating], 'rating_amt': [rating_amt]
                                        ,'address': [address], 'menu': [menus], 'review': [reviews]})
                df = pd.concat([df, new_row], ignore_index=True)
        except AttributeError:
            print(f"AttributeError occurred at index {i}. Skipping the row.")
    df.to_csv('untranslated_bakerie.csv', index=False)
    print(df)


if __name__ == '__main__':
    scrapingInfo()


