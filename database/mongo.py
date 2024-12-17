from pymongo import AsyncMongoClient
import config

# Initialize MongoDB client and database
client = AsyncMongoClient(host="localhost", port=config.mongo_service)
db = client["my_database"]

chat_history = db["history"]
documents = db["documents"]


class Documents:
    def __init__(self):
        pass
    
    async def get(self, request):
        document_name = request["document_name"]
        
        if document_name:
            document = await documents.find_one({"document_name": document_name})
            if document:
                document["_id"] = str(document["_id"])  # Convert ObjectId to string if needed
                return document
            else:
                return NameError

        else:
            all_documents = await documents.find({}).to_list(None)
            document_list = []

            for document in all_documents:
                document["_id"] = str(document["_id"])  # Convert ObjectId to string if needed
                document_list.append(document)
                
            return document_list

    async def post(self, request):
        print(request)
        document_name = request["document_name"]
        
        if await documents.find_one({"document_name": document_name}):
            return NameError
        await documents.insert_one(request)


    async def delete(self, request):
        document_name = request["document_name"]
        
        if not document_name:
            return NameError
        
        await documents.delete_one({"document_name": document_name})
        return {"status": 200}




class ChatHistory:
    def __init__(self):
        pass
    
    async def get(self, request):
        user = request["user"]
        
        if not user:
            return {"error": "User is required"}, 400
        
        history = await chat_history.find_one({"user": user})
        
        if not history:
            return []
        
        history["_id"] = str(history["_id"])
        
        return history["history"]


    async def post(self, request):
        print(request)
        user = request["user"]
        messages = request["messages"]

        if not user or not messages:
            return ValueError

        await chat_history.update_one(
            {"user": user},
            {"$push": {"history": {"$each": messages}}},
            upsert=True
        )

        return {"status": 200}
