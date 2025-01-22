from typing import List
from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    content: List[str]

class EmbeddingResponse(BaseModel):
    vectors: List[List[float]]

