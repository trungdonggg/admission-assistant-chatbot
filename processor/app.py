from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from processor.agent import Agent
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
import dotenv
dotenv.load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_AI_API_KEY"),
    )

class SearchRequest(BaseModel):
    query: str 
    user: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    agent = Agent(llm).build_graph()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/search")
async def search(request: SearchRequest):
    try:
        res = await agent.ainvoke({
            "messages": [HumanMessage(content=request.query)], 
            "user": request.user
            })
        
        return {
            "user": request.user,
            "response": res["messages"][-1].content
        }

    except Exception as e:
        logger.error(f"Error in searching: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))