from pydantic import BaseModel
from typing import List


class AddDocumentRequestDatabase(BaseModel):
    user: str
    document_name: str
    tag_name: str
    content: str

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
    content: str 
    vector: List[float]
    limit: int

class GenerateLLMRequest(BaseModel):
    input: str
    context: str
    history: List

class SearchRequest(BaseModel):
    user: str
    query: str

class AddDocument(BaseModel):
    user: str
    document_name: str
    tag_name: str
    document_content: str

class TagnameClassifier(BaseModel):
    history: List
    input: str

class QueryVectorDatabaseTagname(BaseModel):
    content: str 
    vector: List[float]
    limit: int
    tagname: List[str]