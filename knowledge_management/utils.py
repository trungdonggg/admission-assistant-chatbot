from config import *
import httpx
from typing import List, Dict
from pydantic import BaseModel
    
    
class AddDocumentRequestVectorDatabase(BaseModel):
    document_name: str
    chunks: List[str]
    vectors: List[List[float]]
    metadata: Dict




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



async def vectorize(request: List[str]) -> List[List[float]]:
    url = f"http://{embedding_api_host}:{embedding_api_port}/vectorize"
    
    payload = request.model_dump()

    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=60.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json().get("vectors")



async def add_document_to_vectordb(request: AddDocumentRequestVectorDatabase):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever"
    
    payload = request.model_dump()

    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=60.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json()




async def remove_document_from_vectordb(document_name: str):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever?document_name={document_name}"
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=60.0, pool=10.0)
        response = await client.delete(url, timeout=timeout)
        response.raise_for_status()
    
    return response.json()