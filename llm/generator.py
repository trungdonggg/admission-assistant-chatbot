from typing import AsyncGenerator
from llm.utils import *
from llm.chat_template import ChatTemplate


class Generator:
    def __init__(self):
        self.generator = get_chatbot_prompt() | get_model() | streaming_parser()

    async def astream(self, prompt_components: ChatTemplate) -> AsyncGenerator[str, None]:
        async for word in self.generator.astream(prompt_components.model_dump()):
            yield word

    async def ainvoke(self, prompt_components: ChatTemplate) -> str:
        return await self.generator.ainvoke(prompt_components.model_dump())
