
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


load_dotenv()


def get_classifier_prompt(): 
    
    return ChatPromptTemplate.from_messages(
        [
            (
                "system", 
                "You are an assistant who speaks in Vietnamese. Your task is to extract the name of the university or universities the user is specifically asking about, based primarily on the last question in the conversation. Do not provide answers or summaries, only return a list of the universities the user is asking about. Your output should be in the format: List[str]. Only provide the list and nothing else."
            ),
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


