from pydantic import BaseModel
from embed import Embedding
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embedder: Embedding = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedder
    embedder = Embedding()
    yield

app = FastAPI(lifespan=lifespan)


class VectorizeRequest(BaseModel):
    content: list[str]
    
    
@app.post("/vectorize")
async def generate_response(request: VectorizeRequest):
    try:
        response = await embedder.embed(request.content)
        return {"vectors": response}, 200
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

