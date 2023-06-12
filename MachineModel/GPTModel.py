import llama_index.indices.struct_store
import openai
import pymongo
import pandas as pd
from datetime import datetime
import logging
import sys
from dotenv import load_dotenv
import os
import nest_asyncio
import pandas as pd
from llama_index import GPTPandasIndex, download_loader, VectorStoreIndex
from pathlib import Path
from llama_index import StorageContext, load_index_from_storage
from llama_index.storage import StorageContext
from flask import Flask, request, jsonify, make_response
from flask import Flask, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
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


def pdf_train_lmm():
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(file=Path('../Material/403bakery detail in chiang mai.pdf'))
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query("Please replace your existing knowledge base with this modified document.These are all bakery shops/restaurants in Chiang Mai. This is called 'Chiang Mai Bakery Document', this document includes detail about rating, address or location detail, review, etc. on each bakery shop/restaurant.")
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
@app.route('/askbot', methods=['GET'])
def Reply():
    argList = request.args.to_dict(flat=False)
    prompt = argList['query'][0]
    #Get prompt and response
    response = query_engine.query(prompt)
    jsonResult = { 'response': '200','date': datetime.now(), 'message': response}
    response = make_response(jsonResult)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    index.storage_context.persist()
    return response

if __name__ == '__main__':
    # test_lmm()
    storage_context = StorageContext.from_defaults(persist_dir="D:\Fork\GPT4Baker-BackEnd\MachineModel\storage")
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    app.run(debug=True)