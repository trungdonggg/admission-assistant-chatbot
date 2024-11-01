from pymongo import MongoClient
from flask import request
from flask_restful import Resource
import config

# Initialize MongoDB client and database
client = MongoClient(f"mongodb://localhost:{config.mongo_service}/")
db = client["my_database"]

chat_history = db["chat_history"]
chat_history_schema = {
    "user":str,
    "history": dict
 }


documents = db["documents"]
documents_schema = {
    "name":str,
    "tagname": list[str]
}


class Documents(Resource):
    def get(self):
        document_name = request.args.get("name")
        
        if document_name:
            document = documents.find_one({"name": document_name})
            if document:
                document["_id"] = str(document["_id"])  # Convert ObjectId to string if needed
                return {"document": document}, 200
            else:
                return {"error": "Document not found"}, 404
        else:
            all_documents = documents.find({})
            document_list = []

            for document in all_documents:
                document["_id"] = str(document["_id"])  # Convert ObjectId to string if needed
                document_list.append(document)
                
            return {"documents": document_list}, 200

    def post(self):
        data = request.json
        document_name = data.get("name")
        document_tagname = data.get("tagname")
        
        if not document_name:
            return {"error": "Document name is required"}, 400
        
        if documents.find_one({"name": document_name}):
            return {"error": "Document with this name already exists"}, 400
        
        documents.insert_one({"name": document_name, "tagname": document_tagname})
        return {"message": "Document added successfully"}, 200

    def delete(self):
        document_name = request.args.get("name")
        
        if not document_name:
            return {"error": "Document name is required"}, 400
        
        result = documents.delete_one({"name": document_name})
        
        if result.deleted_count == 0:
            return {"error": "Document not found"}, 404
        
        return {"message": f"Document '{document_name}' deleted successfully"}, 200




class ChatHistory(Resource):
    def get(self):
        user = request.args.get("user")
        
        if not user:
            return {"error": "User is required"}, 400
        
        history = chat_history.find_one({"user": user})
        history["_id"] = str(history["_id"])
        
        return {"history": history}, 200


    def post(self):
        data = request.json
        user = data.get("user")
        message = data.get("message")
        
        if not user or not message:
            return {"error": "User and message are required"}, 400

        chat_history.update_one(
            {"user": user},
            {"$push": {"history": message}},
            upsert=True
        )
        
        return {"message": "Chat message saved successfully"}, 200
