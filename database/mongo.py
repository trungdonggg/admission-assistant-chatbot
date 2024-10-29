from pymongo import MongoClient
from flask import request, jsonify
from flask_restful import Resource
from .. import config

client = MongoClient(f"mongodb://localhost:{config.mongo_service}/") 
db = client["my_database"]
chat_history = db["chat_history"]
documents = db['documents']



class MongoDB(Resource):
    def get(self, item_id):
        pass

    def post(self):
        pass
        
    def delete(self, item_id):
        pass


