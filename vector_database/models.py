from typing import List, Dict, Optional, Literal
from pydantic import BaseModel


class GeneralRequest(BaseModel):
    method: Literal["add_document", "query", "remove_document"]
    data: Dict

class AddDocumentRequest(BaseModel):
    collection_name: List[categry.categories]
    document_name: str
    chunks: List[str]
    vectors: List[List[float]]
    metadata: Dict

class QueryRequest(BaseModel):
    collection_name: List[categry.categories]
    content: Optional[str]
    vector: List[float]
    limit: int

class DeleteDocumentRequest(BaseModel):
    collection_name: List[categry.categories]
    document_name: str