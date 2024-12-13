from config import *
from processor.models import *
import httpx
import ast
import re

async def split_document(content: str, chunk_size: int = 100, chunk_overlap: int = 20):
    url = f"http://{textsplitter_api_host}:{textsplitter_api_port}/splittext"
    
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
        response.raise_for_status()

    return response.json().get("chunks")       #List[str]     

async def add_document_name_and_tagname_to_db(request: AddDocumentRequestDatabase):
    url = f"http://{database_api_host}:{database_api_port}/db/documents"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    return response.json()


async def vectorize(request: VectorizeRequest):
    url = f"http://{embedding_api_host}:{embedding_api_port}/vectorize"
    
    payload = request.model_dump()

    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
    
    return response.json().get("vectors")


async def add_document_to_vectordb(request: CreateDocumentRequestVectorDatabase):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever"
    
    payload = request.model_dump()

    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
    
    return response.json()


async def remove_document_from_db(document_name: str):
    url = f"http://{database_api_host}:{database_api_port}/db/documents?document_name={document_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
        response.raise_for_status()
    
    return response.json()


async def remove_document_from_vectordb(document_name: str):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever?document_name={document_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
        response.raise_for_status()
    
    return response.json()

async def add_chat_history(request: AddChatHistoryRequestDatabase):
    url = f"http://{database_api_host}:{database_api_port}/db/history"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
    
    return response.json()

async def get_chat_history(user: str):
    url = f"http://{database_api_host}:{database_api_port}/db/history?user={user}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
    
    return response.json().get("history")


async def query_vectordb(request: QueryVectorDatabase):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever/query"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
    
    return response.json()


async def generate_by_llm(request: GenerateLLMRequest):
    url = f"http://{llm_api_host}:{llm_api_port}/generate"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
    
    return response.text


async def query_vectordb_tagnames(request: QueryVectorDatabaseTagname):
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever/query_tagname_based"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
    
    return response.json()

async def tagnames_cls(request: TagnameClassifier):
    print("finding universities tagnames...")
    url = f"http://{classifier_api_host}:{classifier_api_port}/classify"
    
    payload = request.model_dump()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    match = re.search(r"\[.*\]", response.text)

    if match:
        cleaned_input_str = match.group(0)
        university_list = ast.literal_eval(cleaned_input_str)
        return university_list
    else:
        print("No valid list found in the classified string.")
        return []


