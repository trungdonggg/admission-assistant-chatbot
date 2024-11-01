from llm.utils import *
from llm.chat_template import ChatTemplate

class Generator:
    def __init__(self):
        self.generator = get_chatbot_prompt() | get_model()

    async def ainvoke(self, prompt_components: ChatTemplate):
        return await self.generator.ainvoke(prompt_components.model_dump())
    
    def invoke(self, prompt_components: ChatTemplate):
        return self.generator.invoke(prompt_components.model_dump())

