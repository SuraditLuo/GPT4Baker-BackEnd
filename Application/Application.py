import math
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
from Mongo.Mongo_config import time_range_to_list, collection, rating_calc, popular_calc, get_preference
from urllib.parse import parse_qs
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
nest_asyncio.apply()
load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
# OpenAI APIKEY
UPLOAD_FOLDER = '../Material'
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
openai.api_key = os.environ.get("OPENAI_API_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
storage_context = StorageContext.from_defaults(persist_dir="D:\Fork\GPT4Baker-BackEnd\Application\storage")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()

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
@app.route('/readpdffrompostman', methods=['GET', 'POST'])
def get_and_read_pdf_test():
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
@app.route('/readpdf', methods=['GET', 'POST'])
def get_and_read_pdf():
    pdf = request.form.get('pdf')
    query = request.form.get('query')
    pdfName = request.form.get('pdfName')
    # Decode the base64 content
    print(pdf)
    print(query)
    print(pdfName)
    pdf_content = base64.b64decode(pdf.split(',', 1)[1])
    with open(pdfName, 'wb') as pdf_file:
        pdf_file.write(pdf_content)
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(file=Path(pdfName))
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
    print(json_data)
    # Remove the temporary PDF file
    os.remove(pdfName)
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
        # Create a defaultdict to store the counts of each items
        menu_counts = defaultdict(int)
        price_counts = defaultdict(int)
        time_counts = defaultdict(int)
        for_kids_count = 0
        for_group_count = 0
        for_both_count = 0
        no_preference_count = 0
        top_rating = []
        top_popular = []
        result = json.loads(json_util.dumps(documents))
        for bakery_shop in result:
            #get menu for each shop
            menu_items_str = bakery_shop.get('menu', [])
            menu_items = ast.literal_eval(menu_items_str)
            formatted_menu_items = [item.replace('_', ' ').title() for item in menu_items]
            for menu_item in formatted_menu_items:
                menu_counts[menu_item] += 1
            #get price for each shops
            price_scale = bakery_shop.get('price_scale')
            if price_scale in {'1', '2', '3', 'none'}:
                price_counts[price_scale] += 1
            #get and process the open hour
            open_period = bakery_shop.get('open_hr', None)
            if open_period is not None:
                for time in time_range_to_list(open_period):
                    time_counts[time] += 1
            preference = get_preference(bakery_shop.get('for_kids'), bakery_shop.get('for_group'))
            if preference == 'for_kids':
                for_kids_count += 1
            elif preference == 'for_group':
                for_group_count += 1
            elif preference == 'for_both':
                for_both_count += 1
            else:
                no_preference_count += 1
            top_rating.append(rating_calc(bakery_shop.get('rating'), bakery_shop.get('rating_amt'), bakery_shop.get('name')))
            top_popular.append(popular_calc(bakery_shop.get('check_in'), bakery_shop.get('bookmarked'), bakery_shop.get('name')))
        menu_counts.pop("No Bakery Related Menu", None)
        menu_counts_sorted = dict(sorted(menu_counts.items(), key=lambda x: x[1], reverse=True))
        filtered_time_period = {k: v for k, v in time_counts.items() if ":30" not in k}
        sorted_top_rating = sorted(top_rating, key=lambda x: x['rating_score'], reverse=True)[:5]
        sorted_top_popular = sorted(top_popular, key=lambda x: x['popularity_score'], reverse=True)[:5]
        result_data = {
            'location': str(address).replace('_', ' '),
            'amount': find_amt,
            'menu_counts': menu_counts_sorted,
            'price_counts': price_counts,
            'time_period': filtered_time_period,
            'preferences': {
                'for_kids': for_kids_count,
                'for_group': for_group_count,
                'for_kid_and_group': for_both_count,
                'not_mention': no_preference_count
            },
            'top_rating': sorted_top_rating,
            'top_popularity': sorted_top_popular
        }
        return jsonify(result_data), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # pdf_train_llm('../Material/Kent State University_20 ways to Enhance Your Communication Skills.pdf', "This is a document to make you reply to a people humanly since I find that you're reply when I say thanks is not good.")
    app.run(debug=True)