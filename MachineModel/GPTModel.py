import tempfile

import openai
import pymongo
from datetime import datetime
import logging
import sys
from dotenv import load_dotenv
import os
import nest_asyncio
from llama_index import GPTPandasIndex, download_loader, VectorStoreIndex
from pathlib import Path
from llama_index import StorageContext, load_index_from_storage
from llama_index.node_parser import SimpleNodeParser
from llama_index.storage import StorageContext
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from bson import json_util
from collections import defaultdict
import json
import ast

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

def pdf_train_llm(pdf, query):
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
    json_response = jsonify(response)
    json_data = json_response.get_json()
    score = json_data.get('source_nodes')[0].get('score')
    print(score)
    json_data.pop('source_nodes')
    json_data.pop('extra_info')
    response = {'response': '200', 'date': datetime.now(), 'message': json_data, 'score': score}
    # Remove the temporary PDF file
    os.remove(pdf_path)
    return response
@app.route('/ask', methods=['GET'])
def reply():
    argList = request.args.to_dict(flat=False)
    prompt = argList['query'][0]
    #Get prompt and response
    response = query_engine.query(prompt)
    json_response = jsonify(response)
    json_data = json_response.get_json()
    score = json_data.get('source_nodes')[0].get('score')
    print(score)
    json_data.pop('source_nodes')
    json_data.pop('extra_info')
    response = {'response': '200', 'date': datetime.now(), 'message': json_data, 'score': score}
    return response

@app.route('/findmongo', methods=['GET'])
def get_mongo_data():
    argList = request.args.to_dict(flat=False)
    address = argList['address'][0]
    try:
        documents = collection.find({
        'address': {
            '$regex': f"(.*{address}.*)"
            }
        })
        find_amt = collection.count_documents({
            'address': {
                '$regex': f"(.*{address}.*)"
            }
        })
        # Create a defaultdict to store the counts of each menu item
        menu_counts = defaultdict(int)
        result = json.loads(json_util.dumps(documents))
        for bakery_shop in result:
            menu_items_str = bakery_shop.get('menu', [])
            menu_items = ast.literal_eval(menu_items_str)
            for menu_item in menu_items:
                menu_counts[menu_item] += 1
        menu_counts.pop("No bakery related menu", None)
        menu_counts_sorted = dict(sorted(menu_counts.items(), key=lambda x: x[1], reverse=True))
        print(menu_counts_sorted)
        return menu_counts_sorted, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # pdf_train_lmm('../Material/pdf-sample.pdf', "This is a short document abot acrobat PDF")
    app.run(debug=True)