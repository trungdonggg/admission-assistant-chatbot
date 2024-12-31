from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from database import History, Document
from storage import MinioHandler
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from contextlib import asynccontextmanager
import logging
from utils import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class DocumentMetadata(BaseModel):
    name: str = Field(..., description="Name of the file")
    size: int = Field(..., description="Size of the file in bytes")
    type: str = Field(..., description="Type of the file")
    content: str = Field(..., description="Content of the file in text format")
    owner: str = Field(..., description="Owner of the file")
    department: str = Field(..., description="Department associated with the file")
    description: str = Field(..., description="Description of the file")
    university: str = Field(..., description="University associated with the file")
    addition: Optional[dict] = Field(None, description="Additional information about the file (if any)")
    minio: Dict = Field(..., description="Minio return data")

    

class AddChatHistoryRequest(BaseModel):
    user: str = Field(..., description="User name")
    messages: List = Field(..., description="List of messages to add to history")
    
    


doc: Document = None
history: History = None
minioClient: MinioHandler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global doc, history, minioClient
    doc = Document() 
    history = History()
    minioClient = MinioHandler()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/knowledge/documents")
async def add_document(
    file: UploadFile = File(...), 
    content: str = Form(...),
    owner: str = Form(...),
    department: str = Form(...),
    description: str = Form(...),
    university: str = Form(...),
    addition: Optional[Dict] = Form(None)
) -> Dict:
    try:
        if await doc.already_exists(file.filename):
            raise HTTPException(status_code=400, detail="Document already exists")

        res = minioClient.upload(file.filename, file.file)
        print('Document uploaded to Minio')

        data = DocumentMetadata(
                name=file.filename,
                size=file.size,
                type=file.content_type,
                content=content,
                owner=owner,
                department=department,
                description=description,
                university=university,
                addition=addition,
                minio=res,
            ).model_dump()
        
        await doc.post(data)
        data.pop("_id", None)
        print('Document added to database')
        
        chunks = await split_document(content)
        print('Text chunked')
        
        vectors = await vectorize(chunks)
        print('Vectors generated')
        
        await add_document_to_vectordb(
            AddDocumentRequestVectorDatabase(
                document_name=file.filename,
                chunks=chunks,
                vectors=vectors,
                metadata=data
            )
        )
        print('Document added to vector database')

        return data

    except Exception as e:
        minioClient.delete(file.filename)
        await doc.delete(file.filename)
        await remove_document_from_vectordb(file.filename)
        
        logger.error(f"Error in adding document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/knowledge/document")
# async def get_documents(document_name: str = None) -> Dict:
#     try:
#         return await doc.get(document_name)
#     except Exception as e:
#         logger.error(f"Error in getting documents: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))
    


@app.delete("/knowledge/documents")
async def delete_document(document_name: str) -> Dict:
    try:
        minioClient.delete(document_name)
        print('Document deleted from Minio')
        await doc.delete(document_name)
        print('Document deleted from database')
        await remove_document_from_vectordb(document_name)
        print('Document deleted from vector database')
        
        return {"deleted": document_name}
    except Exception as e:
        logger.error(f"Error in deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    
    



    
@app.post("/knowledge/history")
async def add_history(request: AddChatHistoryRequest) -> Dict:
    try:
        await history.post(**request.model_dump()) 
        return {"added": request.user}
    except Exception as e:
        logger.error(f"Error in adding history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/history")
async def get_history(user: str) -> Dict:
    try:
        his = await history.get(user)
        return {"history": his}
    except Exception as e:
        logger.error(f"Error in getting history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.delete("/knowledge/history")
async def delete_history(user: str) -> Dict:
    try:
        await history.delete(user)
        return {"deleted": user}
    except Exception as e:
        logger.error(f"Error in deleting history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))