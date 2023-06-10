import llama_index.indices.struct_store
import openai
import pymongo
import pandas as pd
import mysql.connector
import logging
import sys
from dotenv import load_dotenv
import os

import nest_asyncio
from pymongo import MongoClient
from regex import *
import pandas as pd
from llama_index import GPTPandasIndex, download_loader, VectorStoreIndex
from llama_index import SimpleMongoReader
from pathlib import Path
from llama_index.node_parser import SimpleNodeParser
from llama_index import StorageContext, load_index_from_storage
from llama_index.storage.docstore import MongoDocumentStore
from llama_index.storage.index_store import MongoIndexStore
from llama_index.storage import StorageContext
nest_asyncio.apply()
load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
# OpenAI APIKEY
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
openai.api_key = os.environ.get("OPENAI_API_KEY")


def to_mongoDB():
    cleaned_df = pd.read_csv('../Material/cleaned_featured_bakery.csv')
    cleaned_dict = cleaned_df.to_dict(orient='records')
    client = pymongo.MongoClient(os.environ.get("MONGO_HOST"), int(os.environ.get("MONGO_PORT")))
    db = client[os.environ.get("BAKERY_DATABASE")]
    print(db)
    collection = db[os.environ.get("BAKERY_COLLECTION")]
    print(collection)
    collection.insert_many(cleaned_dict)
    client.close()

def csv_train_lmm():
    SimpleCSVReader = download_loader("SimpleCSVReader")
    # Load csv document
    loader = SimpleCSVReader()
    documents = loader.load_data(file=Path('../Material/cleaned_bakery.csv'))
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query("Here's another csv that I want you to read and understand. It has the information of bakery shops in Chiang Mai, We have around 403 shops/restaurants."
                                  "I'll explain each column for you, the first one is the bakery shop/restaurant name, second column rating. It's the overall score of their shop, and rating_amt column is the amount of peoples who gave the score. "
                                  "the address column contain the name of each district where the bakery shop located, for example if the address value is ['Mueang_Chiang_Mai', 'Suthep', 'Nimmanhaemin'], hence that the shop address is Mueang Chiang Mai Suthep Nimmanhaemin."
                                  "If the address = ['other'], it mean that the shop located in the location that I didn't label. next one is a menu column, each index in this column contain a list of menu and each item are the name of the product that they sold."
                                  "For example, if the menu equal to ['scone', 'brownie', 'muffin'], it mean that the shop have scone, brownie, and muffin as their menu."
                                  "If the menu equal to ['No bakery related menu'], it mean that they didn't include a menu on their website"
                                  "Next, open_hr and delivery_hr is not the same. 'open_hr' column is the open time period, but delivery_hr is a delivery available period"
                                  "price_scale is indicate to how expensive the bakery shop is, 1 mean cheap, 2 mean medium, 3 mean expensive, and none mean bakery shop doesn't tell us the price scale."
                                  "The seat_amt column tell you about how many seat are there in this particular shop/restaurant"
                                  "a review column which contain a list of reviewer, and inside the reviewer list contains"
                                  "a keyword that include in their comments. if the review is equal to [], it mean that the bakery shop/restaurant doesn't have any review."
                                  "Finally, the columns from car_park to for_group is indicate to a service & availability to their customer."
                                  "Here's some thing you need to know, when the value in some index"
                                  "is N/A, it's means that they didn't label it in their bakery shop's website. After that, please tell me about a bakery shop in Nimmanhaemin")

    print(response)
    # save
    index.storage_context.persist()

def pdf_train_lmm():
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(file=Path('../Material/Tourist_guide_bakery_shop.pdf'))
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query("These are the list of bakery shop that reviewed by foreign with their comment. I want you to be able to predict a next popular bakery product for both foreigner and Chiang Mai citizen.")
    print(response)
    index.storage_context.persist()
    return True

def test_lmm():
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    # load index
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    query = ""
    while query != ['q']:
        query = input("Enter query: ")
        response = query_engine.query(query)
        print(response)
        index.storage_context.persist()
    # save
if __name__ == '__main__':
    pdf_train_lmm()