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
    cleaned_df = pd.read_csv('../cleaned_featured_bakery.csv')
    cleaned_dict = cleaned_df.to_dict(orient='records')
    client = pymongo.MongoClient(os.environ.get("MONGO_HOST"), int(os.environ.get("MONGO_PORT")))
    db = client[os.environ.get("BAKERY_DATABASE")]
    print(db)
    collection = db[os.environ.get("BAKERY_COLLECTION")]
    print(collection)
    collection.insert_many(cleaned_dict)
    client.close()

def ai_learning():
    from pathlib import Path
    from llama_index import download_loader

    SimpleCSVReader = download_loader("SimpleCSVReader")

    loader = SimpleCSVReader()
    documents = loader.load_data(file=Path('../cleaned_featured_bakery.csv'))
    print(documents)

def train_lmm():
    SimpleCSVReader = download_loader("SimpleCSVReader")
    # Load csv document
    loader = SimpleCSVReader()
    documents = loader.load_data(file=Path('../cleaned_bakery.csv'))
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query("Here's another csv that I want you to read and understand. It's the same information as a "
                                  "previous one, which is an information of bakery shops in Chiang Mai we have around 403 sample."
                                  "I'll explain some column, the address column contain the name of each district where the bakery shop located"
                                  "the columns from car_park to for_group is indicate to a service & suitable to their customer."
                                  "And lastly, a review column which contain a list of reviewer, and inside the reviewer list contains"
                                  "a keyword that include in their comments. Here's some thing you need to know, when the value in some index"
                                  "is N/A, it's means that they didn't label it in their bakery shop's website.")

    print(response)
    # save
    index.storage_context.persist()

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
    train_lmm()