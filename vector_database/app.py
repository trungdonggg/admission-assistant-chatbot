from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional, Dict
from vector_database.weaviatedb import WeaviateDB
import logging
import categry


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AddDocumentRequest(BaseModel):
    collection_name: categry.categories
    document_name: str
    chunks: List[str]
    vectors: List[List[float]]
    metadata: Dict


class QueryRequest(BaseModel):
    collection_name: categry.categories
    content: Optional[str]
    vector: List[float]
    limit: int 


class RemoveDocumentRequest(BaseModel):
    collection_name: categry.categories
    document_name: str


weaviate_db: WeaviateDB = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global weaviate_db
    weaviate_db = WeaviateDB()
    await weaviate_db.connect()

    # testing purpose, should be removed
    for collection in categry.collkts:
        await weaviate_db.delete_collection(collection)

    for collection in categry.collkts:
        collection_vdb = weaviate_db.get_collection(collection)
        if not await collection_vdb.exists():
            await weaviate_db.create_collection(collection)

    yield

    await weaviate_db.close_connection()


app = FastAPI(lifespan=lifespan)

@app.post("/retriever")
async def add_document(doc: AddDocumentRequest) -> Dict:
    try:
        response = await weaviate_db.add_document(**doc.model_dump())
        return {"message": "Document added successfully", "response": response}
    except Exception as e:
        logger.error(f"Error in adding document to weaviate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

# @app.post("/retriever/query")
# async def query(req: QueryRequest) -> Dict:
#     try:
#         response = await weaviate_db.query(
#             config.weaviate_collection_name, 
#             req.vector, 
#             req.content, 
#             req.limit
#         )
#         return {"query_results": response}
#     except Exception as e:
#         logger.error(f"Error in querying: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/retriever/query")
async def query(req: QueryRequest) -> Dict:
    try:
        response = await weaviate_db.query(**req.model_dump())
        return {"query_results": response}
    except Exception as e:
        logger.error(f"Error in querying: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.delete("/retriever")
async def delete_document(req: RemoveDocumentRequest) -> Dict:
    try:
        response = await weaviate_db.remove_document(**req.model_dump())
        return {"message": "Document deleted successfully", "response": response}
    except Exception as e:
        logger.error(f"Error in retrieving: {str(e)}", exc_info=True)
        return HTTPException(status_code=500, detail=str(e))

# check delete request