import pymongo
import pandas as pd
import mysql.connector
import os

mongo_host = 'mongodb+srv://TokiDokor:TokiDoki%40081@gpt4bakerscrapeddatabas.fja2pcw.mongodb.net/?retryWrites=true&w=majority'
mongo_database = 'Bakery_database'
mongo_collection = 'bakeryInfo'
mongo_port = 27017
def to_mongoDB():
    cleaned_df = pd.read_csv('../cleaned_featured_bakery.csv')
    cleaned_dict = cleaned_df.to_dict(orient='records')
    client = pymongo.MongoClient(mongo_host, mongo_port)
    db = client[mongo_database]
    print(db)
    collection = db[mongo_collection]
    print(collection)
    collection.insert_many(cleaned_dict)
    client.close()


if __name__ == '__main__':
    to_mongoDB()