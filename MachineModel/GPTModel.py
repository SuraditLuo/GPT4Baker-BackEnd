import tempfile

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
from llama_index.node_parser import SimpleNodeParser
from llama_index.storage import StorageContext
from flask import Flask, request, jsonify, make_response
from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
app = Flask(__name__)
CORS(app)
nest_asyncio.apply()
load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
# OpenAI APIKEY
UPLOAD_FOLDER = '../Material'
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
openai.api_key = os.environ.get("OPENAI_API_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
storage_context = StorageContext.from_defaults(persist_dir="D:\Fork\GPT4Baker-BackEnd\MachineModel\storage")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()
def to_mongoDB(df):
    try:
        cleaned_dict = df.to_dict(orient='records')
        client = pymongo.MongoClient(os.environ.get("MONGO_HOST"), int(os.environ.get("MONGO_PORT")))
        db = client[os.environ.get("TEST_BAKERY_DATABASE")]
        collection = db[os.environ.get("TEST_BAKERY_COLLECTION")]
        collection.insert_many(cleaned_dict)
        client.close()
        return True
    except OSError:
        return False

def pdf_train_lmm(pdf, query):
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(file=Path(pdf))
    nodes = SimpleNodeParser().get_nodes_from_documents(documents)
    index.insert_nodes(nodes)
    query_engine = index.as_query_engine()
    response = query_engine.query(str(query))
    index.storage_context.persist()
    return response
@app.route('/readpdf', methods=['GET'])
def get_and_read_pdf():
    pdf = request.files['pdf']
    query = request.form['query']
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        pdf.save(temp_file.name)
        pdf_path = temp_file.name
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(file=Path(pdf_path))
    nodes = SimpleNodeParser().get_nodes_from_documents(documents)
    index.insert_nodes(nodes)
    query_engine = index.as_query_engine()
    response = query_engine.query(str(query))
    print(response)
    jsonResult = {'response': '200', 'date': datetime.now(), 'message': response}
    response = make_response(jsonResult)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    # Remove the temporary PDF file
    os.remove(pdf_path)
    return response
@app.route('/ask', methods=['GET'])
def reply():
    argList = request.args.to_dict(flat=False)
    prompt = argList['query'][0]
    #Get prompt and response
    response = query_engine.query(prompt)
    jsonResult = {'response': '200', 'date': datetime.now(), 'message': response}
    response = make_response(jsonResult)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

if __name__ == '__main__':
    # pdf_train_lmm('../Material/pdf-sample.pdf', "This is a short document abot acrobat PDF")
    app.run(debug=True)