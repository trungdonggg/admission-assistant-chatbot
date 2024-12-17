from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from llm.utils import *
from llm.chat_template import ChatTemplate
from llm.generator import Generator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


bot: Generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot
    bot = Generator()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/generate")
async def generate_response(request: ChatTemplate):
    try:
        response = await bot.ainvoke(request)
        print(response.content)
        return Response(content=response.content, status_code=200)
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 
