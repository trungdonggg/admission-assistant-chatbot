from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import categry


class DocumentMetadata(BaseModel):
    name: str = Field(..., description="Name of the file")
    size: int = Field(..., description="Size of the file in bytes")
    type: str = Field(..., description="Type of the file")
    content: str = Field(..., description="Content of the file in text format")
    owner: str = Field(..., description="Owner of the file")
    category: List[categry.categories] = Field(..., description="Category of the file")
    department: str = Field(..., description="Department associated with the file")
    description: str = Field(..., description="Description of the file")
    university: str = Field(..., description="University associated with the file")
    addition: Optional[dict] = Field(None, description="Additional information about the file (if any)")
    minio: Dict = Field(..., description="Minio return data")
    url: str = Field(..., description="url to download the file")

class AddChatHistoryRequest(BaseModel):
    user: str = Field(..., description="User name")
    messages: List = Field(..., description="List of all kind of messages to add to messages")
    conversation: List = Field(..., description="List of messages of human and assistant")
    summary: str = Field(..., description="Summary of conversation")

class AddDocumentToVectorDatabaseRequest(BaseModel):
    collection_name: List[categry.categories] 
    document_name: str
    chunks: List[str]
    vectors: List[List[float]]
    metadata: Dict

class RemoveDocumentFromVectorDatabaseRequest(BaseModel):
    collection_name: List[categry.categories] 
    document_name: str

