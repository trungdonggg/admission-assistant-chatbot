from pydantic import BaseModel
from typing import List
from mongo import ChatHistory, Documents
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AddDocumentRequest(BaseModel):
    user: str
    document_name: str
    tag_name: str
    content: str

class AddChatHistoryRequest(BaseModel):
    user: str
    messages: List
    
    
doc: Documents = None
history: ChatHistory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global doc, history
    doc = Documents() 
    history = ChatHistory()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/db/documents")
async def get_documents(document_name: str = None):
    try:
        return await doc.get({"document_name": document_name})
    except Exception as e:
        logger.error(f"Error in getting documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/db/documents")
async def add_document(request: AddDocumentRequest):
    try:
        await doc.post(request.model_dump())
        return {"status": 200}
    except Exception as e:
        logger.error(f"Error in adding document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/db/documents")
async def delete_document(document_name: str):
    try:
        await doc.delete({"document_name": document_name})
    except Exception as e:
        logger.error(f"Error in deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
    
@app.post("/db/history")
async def add_history(request: AddChatHistoryRequest):
    try:
        await history.post(request.model_dump()) 
    except Exception as e:
        logger.error(f"Error in adding history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/history")
async def get_history(user: str):
    try:
        his = await history.get({"user": user})
        return {"history": his}
    except Exception as e:
        logger.error(f"Error in getting history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))