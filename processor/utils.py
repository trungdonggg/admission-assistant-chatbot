from config import *
from processor.models import *
import httpx


async def split_document(content: str):
    url = f"http://{textsplitter_api_host}:{textsplitter_api_port}/splittext"
    
    payload = {
        "text": content,
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()

    return response.json().get("chunks")       #List[str]     

async def add_document_to_db(request: AddDocumentRequestDatabase):
    url = f"http://{database_api_host}:{database_api_port}/db/documents"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()

    return response.json()


async def vectorize(request: VectorizeRequest):
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


async def add_document_to_vectordb(request: CreateDocumentRequestVectorDatabase):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever"
    
    payload = request.model_dump()

    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json()


async def remove_document_from_db(document_name: str):
    url = f"http://{database_api_host}:{database_api_port}/db/documents?document_name={document_name}"
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.delete(url, timeout=timeout)
        response.raise_for_status()
    
    return response.json()


async def remove_document_from_vectordb(document_name: str):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever?document_name={document_name}"
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.delete(url, timeout=timeout)
        response.raise_for_status()
    
    return response.json()

async def add_chat_history(request: AddChatHistoryRequestDatabase):
    url = f"http://{database_api_host}:{database_api_port}/db/history"
    
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
    url = f"http://{database_api_host}:{database_api_port}/db/history?user={user}"
    
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



