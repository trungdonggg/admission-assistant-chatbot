from pydantic import BaseModel
from typing import List


class ClassifierTemplate(BaseModel):
    history: List = []
    input: str

    