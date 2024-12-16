from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class TextSplitRequest(BaseModel):
    text: str
    chunk_size: int = 200  
    chunk_overlap: int = 20 

class TextSplitResponse(BaseModel):
    chunks: List[str]


@app.post("/splittext", response_model=TextSplitResponse)
async def split_text(request: TextSplitRequest):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\n\n",
                "\n",
                " ",
                ".",
                ",",
                "\u200b",  # Zero-width space
                "\uff0c",  # Fullwidth comma
                "\u3001",  # Ideographic comma
                "\uff0e",  # Fullwidth full stop
                "\u3002",  # Ideographic full stop
                "",
            ],
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        # Split the text into chunks
        texts = text_splitter.create_documents([request.text])
        
        # Extract text from each chunk document
        chunks = [text.page_content for text in texts]
        
        return TextSplitResponse(chunks=chunks)

    except Exception as e:
        logger.error(f"Error in splitting text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

