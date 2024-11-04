from fastapi import FastAPI, HTTPException
from processor.models import AddDocument, QueryRequestVectorDatabase
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


@app.delete("/delete-document/{document_name}")
async def delete_document(document_name: str):
    try:
        await processor.delete_document(document_name)
        return {"status": f"Document '{document_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search(request: QueryRequestVectorDatabase):
    try:
        response = await processor.search(
            user=request.content.split()[0],  # assuming user identifier at start of content
            query=request.content,
            vector=request.vector,
            limit=request.limit
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


