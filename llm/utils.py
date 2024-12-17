from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()


def get_chatbot_prompt(): 

    return ChatPromptTemplate.from_messages(
        [
            ("system", "You are a friendly and helpful AI chatbot, who speaks in Vietnamese. Respond in 200 words or fewer. \
                        Given a query, search the provided context for relevant information only. \
                        If the answer cannot be found in the context, do not speculate or provide irrelevant responses. \
                        Here is the context provided: {context}."),
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





