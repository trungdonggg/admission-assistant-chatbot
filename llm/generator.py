from llm.utils import *
from llm.chat_template import ChatTemplate

class Generator:
    def __init__(self):
        self.model = get_model()

    async def ainvoke(self, prompt_components: ChatTemplate):
        promt = await get_chatbot_prompt().ainvoke(prompt_components.model_dump())

        return await self.model.ainvoke(promt)
    

