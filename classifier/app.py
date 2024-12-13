import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from classifier.utils import *
from classifier.cls_template import ClassifierTemplate
from classifier.cls import Classifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot: Classifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot
    bot = Classifier()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/classify")
async def generate_response(request: ClassifierTemplate):
    try:
        response = await bot.ainvoke(request)
        print(response.content)
        return Response(content=response.content, status_code=200)
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
