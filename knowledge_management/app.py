from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from database import History, Document
from storage import MinioHandler
from fastapi import FastAPI, HTTPException, UploadFile
from contextlib import asynccontextmanager
import datetime
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class AddDocumentRequest(BaseModel):
    file: UploadFile = Field(..., description="Data of the file in binary format")
    content: str = Field(..., description="Content of the file in text format")
    owner: str = Field(..., description="Owner of the file")
    department: str = Field(..., description="Department associated with the file")
    description: str = Field(..., description="Description of the file")
    university: str = Field(..., description="University associated with the file")
    addition: Optional[dict] = Field(None, description="Additional information about the file (if any)")

    

class AddChatHistoryRequest(BaseModel):
    user: str
    messages: List
    
    


doc: Document = None
history: History = None
minioClient: MinioHandler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global doc, history
    doc = Document() 
    history = History()
    minioClient = MinioHandler()
    yield

app = FastAPI(lifespan=lifespan)




# @app.get("/knowledge/document")
# async def get_documents(document_name: str = None) -> Union[Dict, List]:
#     try:
#         return await doc.get(document_name)
#     except Exception as e:
#         logger.error(f"Error in getting documents: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/knowledge/documents")
async def add_document(request: AddDocumentRequest) -> str:
    try:
        print("request")
        print(request)

        print("request.file")
        print(request.file)
        # key = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.file.filename}"

        # await minioClient.upload()



        # info = request.model_dump(exclude={"file"})

        # await doc.post()

    except Exception as e:
        logger.error(f"Error in adding document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    


# @app.delete("/knowledge/documents")
# async def delete_document(document_name: str) -> str:
#     try:
#         return await doc.delete(document_name)
#     except Exception as e:
#         logger.error(f"Error in deleting document: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))
    
    
    
    
# @app.post("/knowledge/history")
# async def add_history(request: AddChatHistoryRequest):
#     try:
#         await history.post(request.model_dump()) 
#         return {"status": 200}
#     except Exception as e:
#         logger.error(f"Error in adding history: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/knowledge/history")
# async def get_history(user: str):
#     try:
#         his = await history.get({"user": user})
#         return {"history": his}
#     except Exception as e:
#         logger.error(f"Error in getting history: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.delete("/knowledge/history")
# async def delete_history(user: str):
#     try:
#         await history.delete({"user": user})
#         return {"status": 200}
#     except Exception as e:
#         logger.error(f"Error in deleting history: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))