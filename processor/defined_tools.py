from typing_extensions import TypedDict
import httpx
from typing import List, Dict, Any, Union, Annotated
from typing import Literal
from categry import *
from pydantic import BaseModel
from langgraph.graph.message import add_messages, AnyMessage
from langchain_core.language_models.chat_models import BaseChatModel


async def query_vectordb(
        collection_name: categories,
        content: str,
        vector: List[float],
        limit: int,
    ) -> List:
 
    url = "http://0.0.0.0:8081/retriever/query"
    
    payload = {
        "collection_name": collection_name,
        "content": content,
        "vector": vector,
        "limit": limit
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json().get("query_results")


async def vectorize(content: str) -> List[List[float]]:
    url = "http://128.214.255.226:5000/vectorize"
    
    payload = {"content": [content]}

    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json().get("vectors")


def router(
    state: Union[list[AnyMessage], dict[str, Any], BaseModel],
    messages_key: str = "messages",
) -> Literal["tools", "summarizer"]:

    if isinstance(state, list):
        ai_message = state[-1]
    elif isinstance(state, dict) and (messages := state.get(messages_key, [])):
        ai_message = messages[-1]
    elif messages := getattr(state, messages_key, []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "summarizer"















async def search_at_thong_tin_truong_dai_hoc(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_truong_dai_hoc" collection using a query string and a vector.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_truong_dai_hoc", content=query, vector=vector, limit=7)

async def search_at_thong_tin_khoa_cong_nghe_thong_tin(query: str, vector: List[float]) -> str:
    """
    Search for relevant documents in the "thong_tin_khoa_cong_nghe_thong_tin" collection using a query string and a vector.

    Args:
        query (str): The textual query to search for within the collection.
        vector (List[float]): The vector representation of the query for vector-based search.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_khoa_cong_nghe_thong_tin", content=query, vector=vector, limit=7)
    
async def search_at_thong_tin_chi_phi(query: str, vector: List[float]) -> Dict:
    """
    Search for relevant documents in the "thong_tin_chi_phi" collection using a query string and a vector.

    Args:
        query (str): The textual query to search for within the collection.
        vector (List[float]): The vector representation of the query for vector-based search.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_chi_phi", content=query, vector=vector, limit=7)












class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    summary: str
    user: str

async def get_chat_history(state: State) -> List[str]:
    user = state["user"]
    url = f"http://0.0.0.0:8000/knowledge/history?user={user}"
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.get(url, timeout=timeout)
        response.raise_for_status()

    return {
        "summary": response.json().get("summary"),
    }


async def add_chat_history(state: State, llm: BaseChatModel) -> None:
    url = "http://0.0.0.0:8000/knowledge/history"

    while True:
        summary = await llm.ainvoke(
                f"Using the previous summary: '{state['summary']}' and the conversation between the user and the assistant, "
                f"which includes: \nUser: {state['messages'][0].content}\nAssistant: {state['messages'][-1].content}\n"
                "provide a concise summary of the interaction."
            )
        if not summary.tool_calls and (
            not summary.content
            or isinstance(summary.content, list) and not summary.content[0].get("text")
        ):
            state["messages"].append(("user", "Respond with a real output."))
        else:
            break
    
    payload = {
        "user": state["user"],
        "messages": [state["messages"][0], state["messages"][-1]],
        "summary": summary
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    


