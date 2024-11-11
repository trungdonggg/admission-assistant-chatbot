from pydantic import BaseModel
from typing import List


class AddDocumentRequestDatabase(BaseModel):
    document_name: str
    tag_name: str

class AddChatHistoryRequestDatabase(BaseModel):
    user: str
    messages: List

class VectorizeRequest(BaseModel):
    content: List[str]

class CreateDocumentRequestVectorDatabase(BaseModel):
    document_name: str
    tag_name: str
    chunks: List[str]
    vectors: List[List[float]]

class QueryVectorDatabase(BaseModel):
    content: str        #query + history
    vector: List[float]
    limit: int

class GenerateLLMRequest(BaseModel):
    input: str
    context: str

class SearchRequest(BaseModel):
    user: str
    query: str

class AddDocument(BaseModel):
    user: str
    document_name: str
    tag_name: str
    document_content: str
