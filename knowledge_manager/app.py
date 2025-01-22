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
from knowledge_manager.models import *
from aio_pika import connect_robust
from aio_pika.patterns import RPC
from config import RABBITMQ_URL, knowledge_management_api_port
import uvicorn
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



doc: Document = None
history: History = None
minioClient: MinioHandler = None
rpc: RPC = None


app = FastAPI()
origins = [
    "http://localhost:3000",
    "*"  # Allow all origins (use with caution)
]

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
    category: List[categry.categories] = Form(...),
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
        
        vectors = await vectorize(chunks, rpc)
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
            ), 
            rpc
        )
        print('Document added to vector database')

        return {
            "response": "Document added successfully",
            "success": True,
        }

    except Exception as e:
        minioClient.delete(res['object_name'])
        await doc.delete(file.filename)
        await remove_document_from_vectordb(
            RemoveDocumentFromVectorDatabaseRequest(
                document_name=file.filename,
                collection_name=category
            ),
            rpc
        )
        
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
        await remove_document_from_vectordb(
            RemoveDocumentFromVectorDatabaseRequest(
                document_name=document_name,
                collection_name=collection_name
            ),
            rpc
        )
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
    









async def setup_rpc():
    """Sets up RPC client."""
    connection = await connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    rpc = await RPC.create(channel)
    return rpc

async def initialize_resources():
    """Initialize global resources."""
    global doc, history, minioClient, rpc
    try:
        rpc = await setup_rpc()
        doc = Document()
        history = History()
        minioClient = MinioHandler()
        logger.info("Resources initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing resources: {str(e)}", exc_info=True)
        raise RuntimeError("Failed to initialize resources")

async def cleanup_resources():
    """Clean up global resources."""
    try:
        if rpc:
            await rpc.close()
            logger.info("RPC connection closed.")
    except Exception as e:
        logger.error(f"Error cleaning up resources: {str(e)}", exc_info=True)

def main():
    """Runs the FastAPI app with Uvicorn."""
    try:
        asyncio.run(initialize_resources())
        uvicorn.run("app:app", host="0.0.0.0", port=knowledge_management_api_port, reload=True)
    finally:
        asyncio.run(cleanup_resources())

if __name__ == "__main__":
    main()