import config
import processor.models as models
import httpx

database_api_host = "localhost"
vectordb_api_host = "localhost"
embedding_api_host = "128.214.255.226"
llm_api_host = "localhost"
processor_api_host = "localhost"
textsplitter_api_host = "localhost"



async def split_document(content: str, chunk_size: int = 100, chunk_overlap: int = 20):
    url = f"http://{textsplitter_api_host}:{config.textsplitter_api_port}/split_text"
    
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

    return response

async def add_document_name_and_tagname_to_db(request: models.AddDocumentRequestDatabase):
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.text


async def vectorize(request: models.VectorizeRequest):
    url = f"http://{vectordb_api_host}:{config.vectordb_api_port}/vectorize"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.text


async def add_document_to_vectordb(request: models.CreateDocumentRequestVectorDatabase):
    url = f"http://{vectordb_api_host}:{config.vectordb_api_port}/add"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.text


async def remove_document_from_db(document_name: str):
    url = f"http://{database_api_host}:{config.database_api_port}/db/documents?name={document_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
    
    return response.text


async def remove_document_from_vectordb(document_name: str):
    url = f"http://{vectordb_api_host}:{config.vectordb_api_port}/retriever?document_name={document_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url)
    
    return response.text


async def get_chat_history(user: str):
    url = f"http://{database_api_host}:{config.database_api_port}/db/history?user={user}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    return response.text


async def query_vectordb(request: models.QueryRequestVectorDatabase):
    url = f"http://{vectordb_api_host}:{config.vectordb_api_port}/query"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.text


async def generate_by_llm(request: models.GenerateLLMRequest):
    url = f"http://{llm_api_host}:{config.llm_api_port}/generate"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.text


async def add_chat_history(request: models.AddChatHistoryRequestDatabase):
    url = f"http://{database_api_host}:{config.database_api_port}/db/history"
    
    payload = request.model_dump_json()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
    
    return response.text
