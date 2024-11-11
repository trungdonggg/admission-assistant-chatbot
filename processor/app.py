from fastapi import FastAPI, HTTPException
from processor.models import AddDocument, SearchRequest
from processor.process import Processor

app = FastAPI()
processor = Processor()


@app.post("/add-document")
async def add_document(request: AddDocument):
    try:
        await processor.add_document(request)
        return {"status": "Document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-document")
async def delete_document(document_name: str):
    try:
        await processor.delete_document(document_name)
        return {"status": f"Document '{document_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search(request: SearchRequest):
    try:
        response = await processor.search(request)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


