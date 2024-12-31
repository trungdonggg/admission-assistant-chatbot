from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional, Dict
from weaviatedb import WeaviateDB
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentRequest(BaseModel):
    document_name: str
    chunks: List[str]
    vectors: List[List[float]]
    metadata: Dict


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

@app.post("/retriever")
async def add_document(doc: DocumentRequest) -> Dict:
    try:
        response = await weaviate_db.add_document(
            config.weaviate_collection_name,
            doc.document_name,
            doc.chunks,
            doc.vectors,
            doc.metadata,
        )
        return {"message": "Document added successfully", "response": response}
    except Exception as e:
        logger.error(f"Error in adding document to weaviate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/retriever/query")
async def query(req: QueryRequest) -> Dict:
    try:
        response = await weaviate_db.query(
            config.weaviate_collection_name, 
            req.vector, 
            req.content, 
            req.limit
        )
        return {"query_results": response}
    except Exception as e:
        logger.error(f"Error in querying: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.delete("/retriever")
async def delete_document(document_name: str) -> Dict:
    try:
        response = await weaviate_db.remove_document(config.weaviate_collection_name, document_name)
        return {"message": "Document deleted successfully", "response": response}
    except Exception as e:
        logger.error(f"Error in retrieving: {str(e)}", exc_info=True)
        return HTTPException(status_code=500, detail=str(e))
