from agent.utils import *
from pydantic import BaseModel
from typing import List

class ChatTemplate(BaseModel):
    history: List = []
    context: str = ""
    input: str
    
    
class Generator:
    def __init__(self):
        self.model = get_model()

    async def ainvoke(self, prompt_components: ChatTemplate):
        promt = await get_chatbot_prompt().ainvoke(prompt_components.model_dump())
        return await self.model.ainvoke(promt)
    

