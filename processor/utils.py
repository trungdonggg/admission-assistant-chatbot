from config import *
from processor.models import *
import httpx
from typing import List




async def vectorize(request: VectorizeRequest) -> List[List[float]]:
    url = f"http://{embedding_api_host}:{embedding_api_port}/vectorize"
    
    payload = request.model_dump()

    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json().get("vectors")



async def add_chat_history(request: AddChatHistoryRequestDatabase):
    url = f"http://{database_api_host}:{knowledge_management_api_port}/knowledge/history"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json()

async def get_chat_history(user: str):
    url = f"http://{database_api_host}:{knowledge_management_api_port}/knowledge/history?user={user}"
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.get(url, timeout=timeout)
        response.raise_for_status()

    return response.json().get("history")


async def query_vectordb(request: QueryVectorDatabase):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever/query"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json()


async def generate_by_llm(request: GenerateLLMRequest):
    url = f"http://{llm_api_host}:{llm_api_port}/generate"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.text



