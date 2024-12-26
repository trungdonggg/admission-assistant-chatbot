from fastapi import FastAPI, File, HTTPException, UploadFile
from storage.handler import MinioHandler
from contextlib import asynccontextmanager
from datetime import datetime
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


@app.post("/upload")
async def upload_file(file: UploadFile):
    print(file.filename)
    print(file.file)
    print(file.content_type)
    print(type(file.file))
    
    print(file.file.read(256))
    try:
        key = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        res = minio_client.upload(key, file.file)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
