import config
from processor.models import *
import httpx
import json


database_api_host = "localhost"
vectordb_api_host = "localhost"
embedding_api_host = "128.214.255.226"
llm_api_host = "localhost"
processor_api_host = "localhost"
textsplitter_api_host = "localhost"



async def split_document(content: str, chunk_size: int = 100, chunk_overlap: int = 20):
    url = f"http://{textsplitter_api_host}:{config.textsplitter_api_port}/splittext"
    
    payload = {
        "text": content,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        # response.raise_for_status()

    return response.json().get("chunks")       #List[str]     

async def add_document_name_and_tagname_to_db(request: AddDocumentRequestDatabase):
    url = f"http://{database_api_host}:{config.database_api_port}/db/documents"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.json()


async def vectorize(request: VectorizeRequest):
    url = f"http://{vectordb_api_host}:{config.vectordb_api_port}/vectorize"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.json()


async def add_document_to_vectordb(request: CreateDocumentRequestVectorDatabase):
    url = f"http://{vectordb_api_host}:{config.vectordb_api_port}/add"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.json()


async def remove_document_from_db(document_name: str):
    url = f"http://{database_api_host}:{config.database_api_port}/db/documents?name={document_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
    
    return response.json()


async def remove_document_from_vectordb(document_name: str):
    url = f"http://{vectordb_api_host}:{config.vectordb_api_port}/retriever?document_name={document_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url)
    
    return response.json()


async def get_chat_history(user: str):
    url = f"http://{database_api_host}:{config.database_api_port}/db/history?user={user}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    return response.json()


async def query_vectordb(request: QueryRequestVectorDatabase):
    url = f"http://{vectordb_api_host}:{config.vectordb_api_port}/query"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.json()


async def generate_by_llm(request: GenerateLLMRequest):
    url = f"http://{llm_api_host}:{config.llm_api_port}/generate"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.json()


async def add_chat_history(request: AddChatHistoryRequestDatabase):
    url = f"http://{database_api_host}:{config.database_api_port}/db/history"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.json()
