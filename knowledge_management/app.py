from pydantic import BaseModel, Field
from typing import List, Optional
from knowledge_management.database import ChatHistory, Document
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AddDocumentRequest(BaseModel):
    name: str = Field(..., description="Name of the file")
    content: str = Field(..., description="Content of the file (could be a placeholder for now)")
    type: str = Field(..., description="Type or format of the file (e.g., pdf, doc, txt)")
    size: str = Field(..., description="Size of the file (e.g., in bytes or human-readable format)")
    url: str = Field(..., description="URL to access the file")
    owner: str = Field(..., description="Owner of the file")
    department: str = Field(..., description="Department associated with the file")
    description: str = Field(..., description="Description of the file")
    university: str = Field(..., description="University associated with the file")
    addition: Optional[dict] = Field(None, description="Additional information about the file (if any)")

    class Config:
        schema_extra = {
            "example": {
                "name": "Example File",
                "content": "This is a placeholder content",
                "type": "pdf",
                "size": "2MB",
                "url": "http://example.com/file.pdf",
                "owner": "John Doe",
                "department": "Computer Science",
                "description": "Project report for CS101",
                "university": "Example University",
                "addition": {
                    "tags": ["report", "project", "CS101"]
                }
            }
        }

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
        return {"status": 200}
    except Exception as e:
        logger.error(f"Error in deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
    
@app.post("/db/history")
async def add_history(request: AddChatHistoryRequest):
    try:
        await history.post(request.model_dump()) 
        return {"status": 200}
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