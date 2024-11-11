from fastapi import FastAPI, HTTPException
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


weaviate_db: WeaviateDB = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global weaviate_db
    weaviate_db = WeaviateDB()
    await weaviate_db.connect()

    # testing purpose, should be removed
    await weaviate_db.delete_collection(config.weaviate_collection_name)

    collection = weaviate_db.get_collection(config.weaviate_collection_name)
    if not await collection.exists():
        await weaviate_db.create_collection(config.weaviate_collection_name)
    yield
    await weaviate_db.close_connection()


app = FastAPI(lifespan=lifespan)

@app.post("/retriever", response_model=dict)
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
        return HTTPException(status_code=500, detail=str(e))
    

@app.post("/retriever-get", response_model=list)
async def add_document(req: QueryRequest):
    try:
        response = await weaviate_db.query(
            config.weaviate_collection_name, 
            req.vector, 
            req.content, 
            req.limit)
        return {"query_results": response}, 200
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


# @app.get("/retriever", response_model=dict)
# async def query_document(content: str, vector: List[float], limit: int = 10):
#     try:
#         # Convert the comma-separated string to a list of floats
#         vector_list = [float(num) for num in vector.split(",")]

#         # Now use vector_list in place of vector
#         response = await weaviate_db.query(config.weaviate_collection_name, vector_list, content, limit)
#         return {"query_results": response}
#     except Exception as e:
#         return HTTPException(status_code=500, detail=str(e))


@app.delete("/retriever", response_model=list)
async def delete_document(document_name: str):
    try:
        response = await weaviate_db.remove_document(config.weaviate_collection_name, document_name)
        return {"message": "Document deleted successfully", "response": response}, 200
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
