
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableGenerator
from typing import AsyncIterator

load_dotenv()


async def _streaming_parse(chunks) -> AsyncIterator[str]:
    async for chunk in chunks:
        yield chunk.content


def get_chatbot_prompt(): 
    system_prompt: str = """
            Your name is David, a friendly and helpful AI chatbot.
            You're an assistant who speaks in Vietnamese. Respond in 200 words or fewer.
            Given a query, search the provided context for relevant information. 
            Here is the context provided: {context}.
            If you don't know the answer, just say that you don't know.
        """
    
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

def get_model():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_AI_API_KEY"),
        temperature=0.7,
        max_tokens=500,
    )

def streaming_parser():
    return RunnableGenerator(_streaming_parse)





