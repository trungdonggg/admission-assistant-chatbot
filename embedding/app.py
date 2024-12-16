from embed import Embedding
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response

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

@app.post("/vectorize")
async def generate_response(request):
    try:
        print(request)
        print(type(request))
        content = request.content
        print(content)
        response = await embedder.embed(content)
        return Response(content=response, status_code=200)
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

