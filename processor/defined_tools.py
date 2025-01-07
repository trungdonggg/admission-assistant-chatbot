from typing_extensions import TypedDict
import httpx
from typing import List, Dict, Any, Union, Annotated
from typing import Literal
from categry import *
from pydantic import BaseModel
from langgraph.graph.message import add_messages, AnyMessage
from config import *

async def query_vectordb(
        collection_name: categories,
        content: str,
        vector: List[float],
        limit: int,
    ) -> List:
 
    url = f"http://{vectordb_api_host}:{vectordb_api_port}/retriever/query"
    
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
    url = f"http://{embedding_api_host}:{embedding_api_port}/vectorize"
    
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
    Search for relevant documents in the "thong_tin_truong_dai_hoc" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_truong_dai_hoc", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_khoa_cong_nghe_thong_tin(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_khoa_cong_nghe_thong_tin" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_khoa_cong_nghe_thong_tin", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_khoa_ngon_ngu(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_khoa_ngon_ngu" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_khoa_ngon_ngu", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_khoa_kinh_te(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_khoa_kinh_te" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_khoa_kinh_te", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_khoa_y(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_khoa_y" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_khoa_y", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_khoa_cong_nghe_sinh_hoc(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_khoa_cong_nghe_sinh_hoc" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_khoa_cong_nghe_sinh_hoc", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_khoa_dieu_duong(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_khoa_dieu_duong" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_khoa_dieu_duong", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_khoa_khai_phong(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_khoa_khai_phong" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_khoa_khai_phong", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_giang_vien(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_giang_vien" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_giang_vien", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_nghien_cuu(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_nghien_cuu" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_nghien_cuu", content=query, vector=vector[0], limit=7)

async def search_at_thong_tin_chi_phi(query: str) -> str:
    """
    Search for relevant documents in the "thong_tin_chi_phi" collection using a query string.

    Args:
        query (str): The textual query to search for within the collection.

    Returns:
        str: The search results retrieved from the vector database, containing relevant documents.
    """
    vector = await vectorize(query)
    return await query_vectordb(collection_name="thong_tin_chi_phi", content=query, vector=vector[0], limit=7)

















