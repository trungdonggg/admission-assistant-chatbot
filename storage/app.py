from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from storage.handler import MinioHandler
from contextlib import asynccontextmanager
from datetime import datetime
import io
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
    try:
        key = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        res = minio_client.upload(key, file.file)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/download")
async def download_file(key: str):
    try:
        res = minio_client.download(key)
        return StreamingResponse(io.BytesIO(res))
                             
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.delete("/delete")
async def delete_file(key: str):
    try:
        res = minio_client.delete(key)   
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}") 