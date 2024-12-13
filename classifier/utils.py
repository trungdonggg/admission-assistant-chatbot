
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
                "You are an assistant who speaks in Vietnamese. Based on the information provided, only find names of universities. "
                "Return the names in a Python list format, with the following format: List[str]. "
                "Do not answer anything else, do not make up any university name yourself. "
                "Only output the Python list, nothing else."
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


