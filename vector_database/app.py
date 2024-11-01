from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
from weaviatedb import WeaviateDB
import config



class DocumentRequest(BaseModel):
    document_name: str
    tag_name: str
    chunks: List[str]
    vectors: List[List[float]]


class QueryRequest(BaseModel):
    content: Optional[str]
    vector: List[float]
    limit: int 


@asynccontextmanager
async def lifespan(app: FastAPI):
    global weaviate_db
    weaviate_db = WeaviateDB()
    await weaviate_db.connect()
    await weaviate_db.create_collection(config.weaviate_collection_name)
    yield
    await weaviate_db.close_connection()


app = FastAPI(lifespan=lifespan)

@app.post("/documents", response_model=dict)
async def add_document(doc: DocumentRequest):
    try:
        response = await weaviate_db.add_document(
            config.weaviate_collection_name,
            doc.document_name,
            doc.tag_name,
            doc.chunks,
            doc.vectors
        )
        return {"message": "Document added successfully", "response": response}
    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/documents", response_model=dict)
async def query_document(content: str, vector: List[float], limit: int = 10):
    try:
        response = await weaviate_db.query(config.weaviate_collection_name, vector, content, limit)
        return {"query_results": response}, 200
    except Exception as e:
        return {"error": str(e)}, 500


@app.delete("/documents", response_model=dict)
async def delete_document(document_name: str):
    try:
        response = await weaviate_db.remove_document(config.weaviate_collection_name, document_name)
        return {"message": "Document deleted successfully", "response": response}, 200
    except Exception as e:
        return {"error": str(e)}, 500
