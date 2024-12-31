from pymongo import AsyncMongoClient
import config
from typing import List, Union, Dict


client = AsyncMongoClient(host="localhost", port=config.mongo_service)
db = client["my_database"]

history = db["history"]
documents = db["documents"]


class Document:
    def __init__(self) -> None:
        pass
    
    async def get(self, name: str) -> Union[Dict, List]:
        if name:
            document = await documents.find_one({"name": name})
            if document:
                document["_id"] = str(document["_id"])
                return document
            else:
                raise NameError

        else:
            all_documents = await documents.find({}).to_list(None)
            document_list = []

            for document in all_documents:
                document["_id"] = str(document["_id"])
                document_list.append(document)
                
            return document_list

    async def post(self, request: Dict) -> str:
        name = request["name"]
        
        if await documents.find_one({"name": name}):
            raise NameError
        
        await documents.insert_one(request)
        return name


    async def delete(self, name: str) -> str:
        if not name:
            raise NameError
        
        await documents.delete_one({"name": name})
        return name




class History:
    def __init__(self) -> None:
        pass
    
    async def get(self, request) -> List:
        user = request["user"]
        
        if not user:
            return {"error": "User is required"}, 400
        
        history = await history.find_one({"user": user})
        
        if not history:
            return []
        
        history["_id"] = str(history["_id"])
        
        return history["history"]


    async def post(self, request) -> str:
        user = request["user"]
        messages = request["messages"]

        if not user or not messages:
            return ValueError

        await history.update_one(
            {"user": user},
            {"$push": {"history": {"$each": messages}}},
            upsert=True
        )

        return user
    
    async def delete(self, request) -> str:
        user = request["user"]
        
        if not user:
            raise NameError
        
        await history.delete_one({"user": user})
        return user

