import math
import os
from dotenv import load_dotenv
import pymongo
load_dotenv()
client = pymongo.MongoClient(os.environ.get("MONGO_HOST"), int(os.environ.get("MONGO_PORT")))
db = client[os.environ.get("BAKERY_DATABASE")]
collection = db[os.environ.get("BAKERY_COLLECTION")]
def to_mongoDB(df):
    try:
        cleaned_dict = df.to_dict(orient='records')
        collection.insert_many(cleaned_dict)
        client.close()
        return True
    except OSError:
        return False

def time_range_to_list(time_range):
    start_time_str, end_time_str = time_range.split(" - ")

    # Parse the start and end times to extract the hour and minute components
    start_hour, start_minute = map(int, start_time_str.split(":"))
    end_hour, end_minute = map(int, end_time_str.split(":"))

    time_list = []
    current_hour, current_minute = start_hour, start_minute

    while current_hour < end_hour or (current_hour == end_hour and current_minute <= end_minute):
        time_list.append(f"{current_hour:02d}:{current_minute:02d}")
        current_minute += 60
        if current_minute >= 60:
            current_hour += 1
            current_minute -= 60
    return time_list

def rating_calc(rating, rating_amt, name):
    if rating_amt > 0:
        bakery_rating = {
            'name': name,
            'rating_score': rating * math.log(rating_amt, 100)
        }
    else:
        bakery_rating = {
            'name': name,
            'rating_score': 0
        }
    return bakery_rating
def popular_calc(check_in, bookmark, name):
    popularity_score = math.log(max(check_in, 1), 10) + math.log(max(bookmark, 1), 50)
    bakery_popular = {
        'name': name,
        'popularity_score': popularity_score
    }
    return bakery_popular
def get_preference(is_for_kids, is_for_group):
    if isinstance(is_for_kids, dict) and isinstance(is_for_group, dict):
        return 'no_preference'
    elif isinstance(is_for_kids, bool) and isinstance(is_for_group, bool):
        return 'for_both'
    elif isinstance(is_for_kids, bool) and isinstance(is_for_group, dict):
        return 'for_kids'
    elif isinstance(is_for_kids, dict) and isinstance(is_for_group, bool):
        return 'for_group'
    else:
        return 'no_preference'






