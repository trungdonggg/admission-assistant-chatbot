from fastapi import FastAPI, File, HTTPException
from storage.handler import MinioHandler
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

minio_client: MinioHandler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global minio_client
    minio_client = MinioHandler()
    yield

app = FastAPI(lifespan=lifespan)

class UploadFileRequest(BaseModel):
    user: str
    file: File

@app.post("/upload/")
async def upload_file(req: UploadFileRequest):
    try:
        res = minio_client.upload('test', req.file.filename, req.file.fileno())
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
