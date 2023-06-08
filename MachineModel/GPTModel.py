import openai
import pymongo
import pandas as pd
import mysql.connector
import logging
import sys
from dotenv import load_dotenv
import os
from pathlib import Path
from llama_index import SimpleDirectoryReader, ServiceContext, LLMPredictor, StorageContext, download_loader
from llama_index import VectorStoreIndex, ListIndex, SimpleKeywordTableIndex
from llama_index.composability import ComposableGraph
from langchain.chat_models import ChatOpenAI
from llama_index.node_parser import SimpleNodeParser
from llama_index.response.notebook_utils import display_response
from llama_index.storage.docstore import MongoDocumentStore
from llama_index.storage.index_store.mongo_index_store import MongoIndexStore
from llama_index.indices.loading import load_index_from_storage
import tiktoken
import nest_asyncio
from pymongo import MongoClient
from regex import *

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
if __name__ == '__main__':
    ai_learning()