from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from llm.utils import *
from llm.chat_template import ChatTemplate
from llm.generator import Generator

class ChatRequest(BaseModel):
    query: str
    history: list = []
    context: str = ""

bot: Generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot
    bot = Generator()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/generate")
async def generate_response(request: ChatRequest):
    
    prompt_components = ChatTemplate(
        history=request.history,
        context=request.context,
        input=request.query
    )

    try:
        response = await bot.ainvoke(prompt_components)
        return Response(content=response.content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
