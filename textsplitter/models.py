from pydantic import BaseModel

class TextSplitRequest(BaseModel):
    text: str
    chunk_size: int = 200
    chunk_overlap: int = 20 