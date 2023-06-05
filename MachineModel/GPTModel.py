import pymongo
import pandas as pd
import mindsdb
def to_mongoDB():
    cleaned_df = pd.read_csv('../cleaned_featured_bakery.csv', encoding='utf-8')
    cleaned_dict = cleaned_df.to_dict(orient='records')
    mongo_host = 'mongodb://localhost'
    mongo_port = 27017
    mongo_database = 'Bakery'
    mongo_collection = 'bakeryInfo'

    client = pymongo.MongoClient(mongo_host, mongo_port)
    db = client[mongo_database]
    print(db)
    collection = db[mongo_collection]
    print(collection)
    collection.insert_many(cleaned_dict)
    client.close()


# def trainBakeryAi():


if __name__ == '__main__':
    to_mongoDB()
