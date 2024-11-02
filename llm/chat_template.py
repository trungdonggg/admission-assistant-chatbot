from pydantic import BaseModel
from typing import List


class ChatTemplate(BaseModel):
    history: List = []
    context: str = ""
    input: str
