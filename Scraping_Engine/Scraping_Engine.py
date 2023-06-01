import googletrans
from bs4 import BeautifulSoup as bs
from googletrans import Translator
import cloudscraper
import requests
from pymongo import MongoClient
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import pandas as pd
import traceback

# scraper = cloudscraper.create_scraper(delay=10, browser="chrome")
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}


def scrapingURL():
    page_number = 1
    base_url = 'https://www.wongnai.com/rankings'
    PATH = 'C:\Program Files (x86)\chromedriver.exe'
    df = pd.DataFrame(columns=['name', 'url'])

    # Set up Chrome WebDriver
    # options = Options()
    # options.add_argument("--headless")  # Run Chrome WebDriver in headless mode (without opening a browser window)
    # driver = webdriver.Chrome(PATH, options=options)
    driver = webdriver.Chrome(PATH)

    for page_number in range(10):
        url = f'{base_url}?category=24&region=373&page.size=50&page.number={page_number}'
        driver.get(url)
        try:
            # Scrape name
            name_li_booleans = WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "bd20"))
            )
            name_list = [element.text for element in name_li_booleans]

            # Scrape URL
            url_li_booleans = driver.find_elements(By.CLASS_NAME, "k0pvs2-0.sc-1bs98dy-0.hgwkbN.ectdXQ")
            url_list = [element.get_attribute("href") for element in url_li_booleans]

            for i in range(len(url_list)):
                name = name_list[i]
                url = url_list[i]
                new_row = pd.DataFrame({'name': [name], 'url': [url]})
                df = pd.concat([df, new_row], ignore_index=True)

            # Check if there is a next page
            next_page_link = driver.find_element(By.CLASS_NAME, "sc-bdfBQB.guRoDh")
            if not next_page_link:
                break  # Exit the loop if there is no next page

            # Increment the page number for the next iteration
            page_number += 1

        except TimeoutException:
            print(f"TimeoutException occurred. Retrying page {page_number}...")
            break

        except Exception as e:
            print(f"An error occurred on page {page_number}: {str(e)}")
            break  # Exit the loop if there is an error accessing a page

    print("We got", len(df), "bakeries shops.")

    # Drop the duplicated rows
    df_nonDupe = df.drop_duplicates(subset=['name'])

    # Save the dataframe as a CSV file
    df_nonDupe.to_csv('url_dataset.csv', index=False)

    # Close the browser and WebDriver
    driver.quit()
def selenium_web_scraping():
    # options = Options()
    # options.add_argument("--headless")  # Run Chrome WebDriver in headless mode (without opening a browser window)
    PATH = 'C:\Program Files (x86)\chromedriver.exe'
    # driver = webdriver.Chrome(PATH, options=options)
    driver = webdriver.Chrome(PATH)
    bakeries = pd.read_csv('url_dataset.csv', encoding="utf-8")
    df = pd.DataFrame(columns=['name', 'rating', 'rating_amt', 'address', 'menu',
                               'open_hr', 'delivery_hr', 'price_scale', 'seat_amt', 'review', 'check_in', 'bookmarked'])
    boolean_df = pd.DataFrame(columns=['car_park', 'Wi-Fi', 'pet_allows', 'card_accept', 'delivery',
                                       'for_kids', 'for_group'])
    for i in range(len(bakeries)):
        try:
            url = bakeries.iloc[i, 1]
            driver.get(url)
            # driver.get('https://www.wongnai.com/restaurants/617953VA-%E0%B9%84%E0%B8%A3%E0%B9%88%E0%B8%82%E0%B8%B4%E0%B8%87%E0%B8%82%E0%B8%99%E0%B8%A1%E0%B8%84%E0%B8%A3%E0%B8%81%E0%B8%AA%E0%B8%B4%E0%B8%87%E0%B8%84%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B9%8C%E0%B9%83%E0%B8%9A%E0%B9%80%E0%B8%95%E0%B8%A2%E0%B8%AB%E0%B8%AD%E0%B8%A1')
            # For resolve CaptCha
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'mb-16-mWeb'))
            )
            sparse_list = ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
            li_list = ['ที่จอดรถ', 'Wi-Fi', 'สัตว์เลี้ยงเข้าได้', 'รับบัตรเครดิต', 'เดลิเวอรี',
                       'เหมาะสำหรับเด็กๆ', 'เหมาะสำหรับมาเป็นกลุ่ม']
            name = driver.find_element(By.CLASS_NAME, 'bd36.bd18-mWeb.text-gray-700').text
            try:
                price_scale = len(driver.find_element(By.XPATH, '//*[@id="body"]/div[2]/div[2]/div[2]/div/div[1]/div[3]/div/span[1]').text)
            except NoSuchElementException:
                price_scale = 'N/A'
            try:
                rating_element = driver.find_element(By.XPATH,
                                                     '//*[@id="body"]/div[2]/div[2]/div[1]/div[1]/div/div[1]/div/div[1]/div/div/div/div/div')
                rating = float(rating_element.text)
            except NoSuchElementException:
                rating = 'N/A'
            rating_amt_text = driver.find_element(By.CSS_SELECTOR, 'span.rg16.rg14-mWeb.font-highlight.text-gray-500 span:nth-child(1)').text
            rating_amt = int(''.join(filter(str.isdigit, rating_amt_text)))
            address = driver.find_element(By.CLASS_NAME, 'sc-18y57ed-0.jEIapA').text
            see_all_element = driver.find_element(By.LINK_TEXT, 'ดูทั้งหมด')
            # Click the button
            see_all_element.click()
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'Flex-sc-3uaums.wcvcr1-2.kcXriF.jAhZuV'))
            )
            menus = driver.find_elements(By.CSS_SELECTOR, 'div.fk7hzc-3.jzMXwh.mr-0')
            if menus:
                menu = [element.text for element in menus]
            else:
                menu = 'N/A'
            driver.back()
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.sc-1kh6w3g-8.gdNTro tr td:nth-child(2)'))
            )
            try:
                open_hr = driver.find_elements(By.CSS_SELECTOR, 'table.sc-1kh6w3g-8.gdNTro tr td:nth-child(2)')[0].text
            except NoSuchElementException:
                open_hr = 'N/A'
            try:
                delivery_hr = driver.find_elements(By.CSS_SELECTOR, 'div.sc-1kh6w3g-0.lljiDP')
                if len(delivery_hr) != 0:
                    delivery_hr = delivery_hr[0].text.split(': ')[1]
                else:
                    delivery_hr = 'N/A'
            except (IndexError, NoSuchElementException):
                delivery_hr = 'N/A'
            try:
                seat_amt_elements = driver.find_elements(By.CLASS_NAME, 'sc-1kh6w3g-1.hpJBMe')
                if len(seat_amt_elements) > 1:
                    seat_amt = seat_amt_elements[1].text
                    if seat_amt != 'ไม่มีที่นั่ง/จัดส่งเท่านั้น':
                        seat_amt = [word for word in seat_amt.split() if word.isdigit()]
                        if len(seat_amt) > 1:
                            seat_amt = seat_amt[1]
                        else:
                            seat_amt = seat_amt[0]
                else:
                    seat_amt = 'N/A'
            except NoSuchElementException:
                seat_amt = 'N/A'
            try:
                li_elements = driver.find_elements(By.CSS_SELECTOR, 'div._1weidWQshSdU3oH6Fm7DNW:nth-child(2) ul li')
                for element in li_elements:
                    li_boolean = False
                    first_span_class = element.find_element(By.TAG_NAME, 'span:nth-child(1)').get_attribute('class')
                    title = element.find_element(By.TAG_NAME, 'span:nth-child(2)').text
                    if first_span_class == 'zjgh1d-0 buIyWl sc-1kh6w3g-10 ixKJFC':
                        li_boolean = True
                    for index, item in enumerate(li_list):
                        if title == item:
                            sparse_list[index] = li_boolean
                boolean_new_row = pd.DataFrame({'car_park': [sparse_list[0]], 'Wi-Fi': [sparse_list[1]], 'pet_allows': [sparse_list[2]],
                                        'card_accept': [sparse_list[3]], 'delivery': [sparse_list[4]], 'for_kids': [sparse_list[5]],
                                        'for_group': [sparse_list[6]]})
            except NoSuchElementException:
                continue
            try:
                driver.find_element(By.CLASS_NAME, 'BaseGap-sc-1wadqs8.jtAAwm.iowx8b-4.cDpduH.iowx8b-4.cDpduH')
                check_in = driver.find_element(By.XPATH, '//*[@id="body"]/div[2]/div[2]/div[1]/div[5]/div[1]/div[1]/div/h2').text
                check_in = int(''.join(filter(str.isdigit, check_in.split())))
                bookmarked = driver.find_element(By.XPATH, '//*[@id="body"]/div[2]/div[2]/div[1]/div[5]/div[2]/div[1]/div/h2').text
                bookmarked = int(''.join(filter(str.isdigit, bookmarked.split())))
            except NoSuchElementException:
                check_in = 0
                bookmarked = 0
            # Check if there is a more review
            reviews = driver.find_elements(By.CLASS_NAME, 'sc-1gcav05-0.caARHI.relative.break-word.text-gray-550.rg14')
            if reviews:
                # See most recent review
                recent_button = driver.find_element(By.CLASS_NAME, 'BaseGap-sc-1wadqs8.liYrUj.text-blue-600.clickable.text-blue-600.clickable')
                recent_button.click()
                time.sleep(2)
                recent_button = driver.find_elements(By.CLASS_NAME, 'kv09ql-1.eubCdB')[1]
                recent_button.click()
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, 'sc-1gcav05-0.caARHI.relative.break-word.text-gray-550.rg14')))
                # Limit the click amount so an automated won't detect during scraping
                for i in range(5):
                    try:
                        button = WebDriverWait(driver, 10) \
                            .until(EC.presence_of_element_located((By.CLASS_NAME, "StyledButton-sc-1lpnvbj.hOAwrM")))
                        # Click the button using JavaScript
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)
                    except NoSuchElementException:
                        break
                    except TimeoutException:
                        break
                # After no more button, find all the review
                try:
                    readmore_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located((By.LINK_TEXT, 'อ่านต่อ')))
                    if readmore_element:
                        for element in readmore_element:
                            try:
                                time.sleep(2)   # Delay to allow the element to be in the clickable area
                                element.click()
                            except ElementClickInterceptedException:
                                # Scroll the page to bring the element into view
                                driver.execute_script("arguments[0].scrollIntoView();", element)
                                time.sleep(2)  # Delay to allow the element to be in the clickable area
                                element.click()
                except TimeoutException:
                    pass # go to next line
                reviews = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME,
                                                         'sc-1gcav05-0.caARHI.relative.break-word.text-gray-550.rg14')))
                review_list = [element.text for element in reviews]
                for i, review in enumerate(review_list):
                    if review == 'เนื้อหาของรีวิวถูกซ่อนเนื่องจากระบบคัดกรอง':
                        review_list.remove(review)
                    if 'ดูเพิ่มเติม' in review:
                        review_list[i] = review_list[i].replace('ดูเพิ่มเติม', '')
                    # Sometimes it doesn't detect the element for..whatever reason. It quiet a rare situation,
                    # so we just let it happen.
                    if '...อ่านต่อ' in review:
                        review_list[i] = review_list[i].replace('...อ่านต่อ', '')
            else:
                review_list = 'N/A'
            df_new_row = pd.DataFrame({'name': [name], 'rating': [rating], 'rating_amt': [rating_amt], 'address': [address],
                                       'menu': [menu], 'open_hr': [open_hr], 'delivery_hr': [delivery_hr],
                                       'price_scale': [price_scale], 'seat_amt': [seat_amt], 'review': [review_list],
                                       'check_in': [check_in], 'bookmarked': [bookmarked]})
            df = pd.concat([df, df_new_row], ignore_index=True)
            boolean_df = pd.concat([boolean_df, boolean_new_row], ignore_index=True)
            print('-----Done-------')
        except Exception as e:
            print(f"Error occurred at index {i}. Retry this row. Error message: {str(e)}")
            traceback.print_exc()
            continue
    driver.quit()
    # Quit the driver and save the DataFrame to CSV
    merged_df = pd.merge(df, boolean_df, left_index=True, right_index=True)
    merged_df.to_csv('untranslated_bakery.csv', index=False, encoding='utf-8')
    print(merged_df)

