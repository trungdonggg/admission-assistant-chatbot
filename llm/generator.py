from typing import AsyncGenerator
from flask import request
from flask_restful import Resource
from llm.utils import *
from llm.chat_template import ChatTemplate


class Generator:
    def __init__(self):
        # self.generator = get_chatbot_prompt() | get_model() | streaming_parser()
        self.generator = get_chatbot_prompt() | get_model()


    # async def astream(self, prompt_components: ChatTemplate) -> AsyncGenerator[str, None]:
    #     async for word in self.generator.astream(prompt_components.model_dump()):
    #         yield word

    async def ainvoke(self, prompt_components: ChatTemplate):
        return await self.generator.ainvoke(prompt_components.model_dump())
    
    def invoke(self, prompt_components: ChatTemplate):
        return self.generator.invoke(prompt_components.model_dump())


class GenerateResponse(Resource):

    def __init__(self):
        self.bot = Generator()
    async def post(self):
        data = request.json

        query = data.get('query')
        history = data.get('history')
        context = data.get('context')

        if not query:
            return {"error": "No query provided"}, 400

        prompt_components = ChatTemplate(
            history=history,
            context=context,
            input=query
        )

        try:
            response = await self.bot.ainvoke(prompt_components)

            return {"response": response.content}, 200

        except Exception as e:
            return {"error": str(e)}, 500