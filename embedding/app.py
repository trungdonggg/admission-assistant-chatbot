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


class EmbeddingRequest(BaseModel):
    content: list[str]

class EmbeddingResponse(BaseModel):
    vectors: list[list[float]]
    
    
@app.post("/vectorize", response_model=EmbeddingResponse)
async def generate_response(request: EmbeddingRequest):
    try:
        response = await embedder.embed(request.content)
        return EmbeddingResponse(vectors=response)
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

