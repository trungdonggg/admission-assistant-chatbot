from fastapi import FastAPI, HTTPException
from processor.models import AddDocument, SearchRequest
from processor.process import Processor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()
processor = Processor()


@app.post("/add-document")
async def add_document(request: AddDocument):
    try:
        await processor.add_document(request)
        return {"status": "Document added successfully"}
    except Exception as e:
        logger.error(f"Error in adding document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-document")
async def delete_document(document_name: str):
    try:
        await processor.delete_document(document_name)
        return {"status": f"Document '{document_name}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error in deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search(request: SearchRequest):
    try:
        response = await processor.search(request)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in searching: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search_tagname_based")
async def search_tagname(request: SearchRequest):
    try:
        response = await processor.search_tagname(request)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in searching: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))