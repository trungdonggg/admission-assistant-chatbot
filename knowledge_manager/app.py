from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from knowledge_manager.database import History, Document
from knowledge_manager.storage import MinioHandler
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from contextlib import asynccontextmanager
import logging
from knowledge_manager.utils import *
import categry
from io import BytesIO


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentMetadata(BaseModel):
    name: str = Field(..., description="Name of the file")
    size: int = Field(..., description="Size of the file in bytes")
    type: str = Field(..., description="Type of the file")
    content: str = Field(..., description="Content of the file in text format")
    owner: str = Field(..., description="Owner of the file")
    category: categry.categories = Field(..., description="Category of the file")
    department: str = Field(..., description="Department associated with the file")
    description: str = Field(..., description="Description of the file")
    university: str = Field(..., description="University associated with the file")
    addition: Optional[dict] = Field(None, description="Additional information about the file (if any)")
    minio: Dict = Field(..., description="Minio return data")
    url: str = Field(..., description="url to download the file")

    

class AddChatHistoryRequest(BaseModel):
    user: str = Field(..., description="User name")
    messages: List = Field(..., description="List of all kind of messages to add to messages")
    conversation: List = Field(..., description="List of messages of human and assistant")
    summary: str = Field(..., description="Summary of conversation")
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    global doc, history, minioClient
    doc = Document() 
    history = History()
    minioClient = MinioHandler()
    yield

app = FastAPI(lifespan=lifespan)
# Define the list of allowed origins
origins = [
    "http://localhost:3000",
    "*"  # Allow all origins (use with caution)
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow credentials (e.g., cookies, authorization headers)
    allow_methods=["*"],  # Allow all HTTP methods (e.g., GET, POST)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/knowledge/documents")
async def add_document(
    file: UploadFile = File(...), 
    content: str = Form(...),
    owner: str = Form(...),
    category: categry.categories = Form(...),
    department: str = Form(...),
    description: str = Form(...),
    university: str = Form(...),    
    addition: Optional[Dict] = Form(None),
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
                category=category,
                department=department,
                description=description,
                university=university,
                addition=addition,
                minio=res,
                url=f'The address of frontend section to preview the file.'
            ).model_dump()
        
        await doc.post(data)
        data.pop("_id", None)
        print('Document added to database')
        
        chunks = await split_document(content)
        print('Text chunked')
        
        vectors = await vectorize(chunks)
        print('Vectors generated')
        
        keys_to_remove = ["content", "size", "type", "owner", "minio", "department", "university"]
        for key in keys_to_remove:
            data.pop(key, None)
        if not addition:
            data.pop("addition", None)
        await add_document_to_vectordb(
            AddDocumentToVectorDatabaseRequest(
                collection_name=category,
                document_name=file.filename,
                chunks=chunks,
                vectors=vectors,
                metadata=data 
            )
        )
        print('Document added to vector database')

        return {
            "response": "Document added successfully",
            "success": True,
        }

    except Exception as e:
        minioClient.delete(res['object_name'])
        await doc.delete(file.filename)
        await remove_document_from_vectordb(category, file.filename)
        
        logger.error(f"Error in adding document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/documents/document-info")
async def get_documents(document_name: str = None) -> Dict:
    try:
        res = await doc.get_document(document_name)
        return {"documents": res}
    except Exception as e:
        logger.error(f"Error in getting documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/documents/user")
async def get_user_documents(user: str) -> Dict:
    try:
        res = await doc.get_user_documents(user)
        return {"user": res}
    except Exception as e:
        logger.error(f"Error in getting documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/knowledge/documents")
async def delete_document(document_name: str) -> Dict:
    try:
        collection_name = (await doc.get_document(document_name))[0]['category']
        minioClient.delete(document_name)
        print('Document deleted from Minio')
        await doc.delete(document_name)
        print('Document deleted from database')
        await remove_document_from_vectordb(collection_name, document_name)
        print('Document deleted from vector database')
        
        return {
            "deleted": document_name,
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error in deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/knowledge/documents/download")
async def download_document(document_name: str) -> FileResponse:
    print(f"Downloading document: {document_name}")
    try:
        mtype = (await doc.get_document(document_name))[0]['type']
        data_stream = BytesIO(minioClient.download(document_name))
        response = StreamingResponse(
            content=data_stream,
            media_type=mtype,
            headers={"Content-Disposition": f"attachment; filename={document_name}"}
        )
        return response

    except Exception as e:
        logger.error(f"Error in downloading document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    









@app.post("/knowledge/history")
async def add_history(request: AddChatHistoryRequest) -> Dict:
    try:
        await history.post(**request.model_dump()) 
        return {"history_added": request.user}
    except Exception as e:
        logger.error(f"Error in adding history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/history")
async def get_history(user: str) -> Dict:
    try:
        his = await history.get(user)
        return his
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