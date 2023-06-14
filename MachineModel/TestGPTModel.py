import unittest

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
from llama_index import StorageContext, load_index_from_storage
from GPTModel import reply
from GPTModel import get_and_read_pdf
from flask import Flask, request, Request
from flask_cors import CORS
from unittest.mock import patch
from pandas import DataFrame
from GPTModel import to_mongoDB
from unittest.mock import MagicMock, patch
from GPTModel import pdf_train_lmm
import tempfile
app = Flask(__name__)
CORS(app)
nest_asyncio.apply()
load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
# OpenAI APIKEY
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
openai.api_key = os.environ.get("OPENAI_API_KEY")
from werkzeug.datastructures import FileStorage
from werkzeug.test import create_environ
from werkzeug.datastructures import ImmutableMultiDict
class TestScriptSendDFToMongoDB(unittest.TestCase):
    @patch.dict(os.environ, {"MONGO_HOST": os.getenv("MONGO_HOST"), "MONGO_PORT": os.getenv("MONGO_PORT")})
    @patch('pymongo.MongoClient')
    def test_to_mongoDB_success(self, mock_client):
        df = pd.DataFrame({'name': ['GROON (GROON)', 'Saruda Finest Pastry'], 'address': [['Mueang_Chiang_Mai', 'Suthep'], ['Mueang_Chiang_Mai', 'Nimmanhaemin']]})

        # Mock MongoDB client and database
        mock_collection = mock_client.return_value['test_db']['test_collection']

        # Call the to_mongoDB function
        result = to_mongoDB(df)

        # Assertions
        mock_client.assert_called_with(os.getenv("MONGO_HOST"), int(os.getenv("MONGO_PORT")))
        mock_collection.insert_many.assert_called_with(df.to_dict(orient='records'))
        mock_client.return_value.close.assert_called_once()
        self.assertTrue(result)

    @patch.dict(os.environ, {"MONGO_HOST": "", "MONGO_PORT": os.getenv("MONGO_PORT")})
    @patch('pymongo.MongoClient')
    def test_to_mongoDB_failure(self, mock_client):
        df = pd.DataFrame({'name': ['GROON (GROON)', 'Saruda Finest Pastry'], 'address': [['Mueang_Chiang_Mai', 'Suthep'], ['Mueang_Chiang_Mai', 'Nimmanhaemin']]})

        # Raise an OSError to simulate a failure
        mock_client.side_effect = OSError()

        # Call the to_mongoDB function
        result = to_mongoDB(df)

        # Assertions
        mock_client.assert_called_with(os.getenv("MONGO_HOST"), int(os.getenv("MONGO_PORT")))
        mock_client.return_value.close.assert_not_called()
        self.assertFalse(result)

class TestScriptReplyMethod(unittest.TestCase):
    def setUp(self):
        # Create a test Flask app
        self.app = Flask(__name__)
        # Set the Flask app in testing mode
        self.app.testing = True
        # Create a test client
        self.client = self.app.test_client()

    def test_reply(self):
        with self.app.test_request_context('/ask', method='GET', query_string={'query': 'How many bakery shops/restaurant in Doi Suthep?'}):
            response = reply()
            # Assert the response status code
            self.assertEqual(response.status_code, 200)
            # Assert the response headers
            self.assertEqual(response.headers['Access-Control-Allow-Origin'], '*')
            self.assertEqual(response.headers['Access-Control-Allow-Credentials'], 'true')
            # Assert the response JSON content
            json_data = response.get_json()
            self.assertEqual(json_data['response'], '200')
            self.assertIsInstance(json_data['message']['response'], str)

if __name__ == '__main__':
    unittest.main()