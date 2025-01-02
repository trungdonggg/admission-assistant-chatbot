from pydantic import BaseModel
from typing import List
import categry



    
class AddChatHistoryRequestDatabase(BaseModel):
    user: str
    messages: List

class VectorizeRequest(BaseModel):
    content: List[str]


class QueryVectorDatabase(BaseModel):
    collection_name: categry.categories
    content: str 
    vector: List[float]
    limit: int

class GenerateLLMRequest(BaseModel):
    input: str
    context: str
    history: List


