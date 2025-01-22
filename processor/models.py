from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph.message import AnyMessage
from pydantic import BaseModel


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    old_conversation: list
    summary: str
    user: str

class SearchRequest(BaseModel):
    query: str 
    user: str