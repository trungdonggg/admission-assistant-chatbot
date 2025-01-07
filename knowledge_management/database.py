from pymongo import AsyncMongoClient
import config
from typing import List, Dict


client = AsyncMongoClient(host="localhost", port=config.mongo_service)
db = client["my_database"]

history = db["history"]
documents = db["documents"]


class Document:
    def __init__(self) -> None:
        pass
    
    async def already_exists(self, name: str) -> bool:
        if await documents.find_one({"name": name}):
            return True
        else:
            return False
    
    async def get_document(self, name: str | None) -> List:
        if name:
            document = await documents.find_one({"name": name})
            if document:
                document["_id"] = str(document["_id"])
                return [document]
            else:
                raise NameError

        else:
            all_documents = await documents.find({}).to_list(None)
            document_list = []

            for document in all_documents:
                document["_id"] = str(document["_id"])
                document_list.append(document)
                
            return document_list
        
    
    async def get_user_documents(self, user: str) -> List:
        if not user:
            raise NameError
        
        all_documents = await documents.find({"owner": user}).to_list(None)
        
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
    
    async def get(self, user: str) -> Dict:
        if not user:
            raise ValueError
        
        his = await history.find_one({"user": user})
        
        if not his:
            return {"user": user, "messages": [], "conversation": [], "summary": ""}
        
        his.pop("_id")
        
        return his


    async def post(self, user: str, messages: List, conversation: List, summary: str) -> str:

        await history.update_one(
            {"user": user},
            {
                "$push": {
                    "messages": {"$each": messages},
                    "conversation": {"$each": conversation}
                },
                "$set": {"summary": summary}
            },
            upsert=True
        )

        return user
    
    
    async def delete(self, user: str) -> str:
        
        if not user:
            raise NameError
        
        await history.delete_one({"user": user})
        return user

