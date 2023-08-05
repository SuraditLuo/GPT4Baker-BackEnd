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