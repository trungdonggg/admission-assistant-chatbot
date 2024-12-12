from pydantic import BaseModel, Field
from typing import List


class ClassifierTemplate(BaseModel):
    history: List = []
    input: str


class OutputParser(BaseModel):
    tagnames: List[str] = Field(description="The names of the universities in the context")
    