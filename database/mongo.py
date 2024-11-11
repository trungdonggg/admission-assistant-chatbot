from pymongo import MongoClient
from flask import request
from flask_restful import Resource
import config

# Initialize MongoDB client and database
client = MongoClient(f"mongodb://localhost:{config.mongo_service}/")
db = client["my_database"]

chat_history = db["history"]
chat_history_schema = {
    "user":str,
    "history": list
 }


documents = db["documents"]
documents_schema = {
    "document_name":str,
    "tag_name": str
}


class Documents(Resource):
    def get(self):
        document_name = request.args.get("document_name")
        
        if document_name:
            document = documents.find_one({"document_name": document_name})
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
        document_name = data.get("document_name")
        document_tagname = data.get("tag_name")
        
        if not document_name:
            return {"error": "Document name is required"}, 400
        
        if documents.find_one({"document_name": document_name}):
            return {"error": "Document with this name already exists"}, 400
        
        documents.insert_one({"document_name": document_name, "tag_name": document_tagname})
        return {"message": "Document added successfully"}, 200

    def delete(self):
        document_name = request.args.get("document_name")
        
        if not document_name:
            return {"error": "Document name is required"}, 400
        
        result = documents.delete_one({"document_name": document_name})
        
        if result.deleted_count == 0:
            return {"error": "Document not found"}, 404
        
        return {"message": f"Document '{document_name}' deleted successfully"}, 200




class ChatHistory(Resource):
    def get(self):
        user = request.args.get("user")
        
        if not user:
            return {"error": "User is required"}, 400
        
        history = chat_history.find_one({"user": user})
        
        if not history:
            return {"history": []}, 200
        
        last_10_messages = history.get("history", [])[-10:]
        
        history["_id"] = str(history["_id"])
        
        return {"history": last_10_messages}, 200



    # def post(self):
    #     data = request.json
    #     user = data.get("user")
    #     messages = data.get("messages")
        
    #     if not user or not messages:
    #         return {"error": "User and message are required"}, 400

    #     chat_history.update_one(
    #         {"user": user},
    #         {"$push": {"history": messages}},
    #         upsert=True
    #     )
        
    #     return {"message": "Chat message saved successfully"}, 200

    def post(self):
        data = request.json
        user = data.get("user")
        messages = data.get("messages")

        if not user or not messages:
            return {"error": "User and message are required"}, 400

        chat_history.update_one(
            {"user": user},
            {"$push": {"history": {"$each": messages}}},
            upsert=True
        )

        return {"message": "Chat message saved successfully"}, 200
