from typing import List, Optional, Dict
from knowledge_manager.database import History, Document
from knowledge_manager.storage import MinioHandler
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import logging
from knowledge_manager.utils import *
import categry
from io import BytesIO
from knowledge_manager.models import *
from aio_pika import connect_robust
from aio_pika.patterns import RPC
from config import rabbitmq_url, knowledge_manager_api_port
import uvicorn
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
doc: Document = None
history: History = None
minioClient: MinioHandler = None
rpc: RPC = None
connection = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app"""
    global doc, history, minioClient, rpc, connection
    try:
        # Startup
        logger.info("Initializing resources...")
        connection = await connect_robust(rabbitmq_url)
        channel = await connection.channel()
        rpc = await RPC.create(channel)
        doc = Document()
        history = History()
        minioClient = MinioHandler()
        logger.info("Resources initialized successfully.")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise
    finally:
        # Shutdown
        logger.info("Cleaning up resources...")
        if rpc:
            await rpc.close()
            logger.info("RPC connection closed.")
        if connection:
            await connection.close()
            logger.info("RabbitMQ connection closed.")

app = FastAPI(lifespan=lifespan)
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
        logger.info('Document uploaded to Minio')

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
        logger.info('Document added to database')
        
        chunks = await split_document(content, rpc)
        logger.info('Text chunked')
        
        vectors = await vectorize(chunks, rpc)
        logger.info('Vectors generated')
        
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
        logger.info('Document added to vector database')

        return {
            "response": "Document added successfully",
            "success": True,
        }

    except Exception as e:
        # Cleanup on failure
        try:
            if 'res' in locals():
                minioClient.delete(res['object_name'])
            await doc.delete(file.filename)
            if 'category' in locals():
                await remove_document_from_vectordb(
                    RemoveDocumentFromVectorDatabaseRequest(
                        document_name=file.filename,
                        collection_name=category
                    ),
                    rpc
                )
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {str(cleanup_error)}", exc_info=True)
            
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
        logger.info('Document deleted from Minio')
        await doc.delete(document_name)
        logger.info('Document deleted from database')
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
    









def main():
    """Runs the FastAPI app with Uvicorn."""
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=knowledge_manager_api_port, 
        reload=True
    )

if __name__ == "__main__":
    main()