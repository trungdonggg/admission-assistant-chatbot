from config import all_queues, textsplitter_api_host, textsplitter_api_port
import httpx
from typing import List
from aio_pika.patterns import RPC
from knowledge_manager.models import *



async def split_document(content: str) -> List[str]:
    url = f"http://{textsplitter_api_host}:{textsplitter_api_port}/splittext"
    
    payload = {
        "text": content,
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=60.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()

    return response.json().get("chunks")   



async def vectorize(request: List[str], rpc: RPC) -> List[List[float]]:
    response = await rpc.call(
        all_queues["embedder"], 
        {
            "content": request
        })
    
    return response.json().get("vectors")



async def add_document_to_vectordb(request: AddDocumentToVectorDatabaseRequest, rpc: RPC):
    response = await rpc.call(
        all_queues["vectordb"], 
        {
            "method": "add_document",
            "data": request.model_dump()
        })

    return response.json()




async def remove_document_from_vectordb(request: RemoveDocumentFromVectorDatabaseRequest, rpc: RPC):
    response = await rpc.call(
        all_queues["vectordb"], 
        {
            "method": "remove_document",
            "data": request.model_dump()
        })

    return response.json()