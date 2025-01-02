from langchain_core.tools import tool
import httpx
from typing import List, Dict
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from typing import Literal


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)


async def query_vectordb(
        collection_name: Literal[
            "thong_tin_truong_dai_hoc",   # thông tin về trường đại học
            "thong_tin_khoa_cong_nghe_thong_tin",  # thông tin về khoa công nghệ thông tin
            "thong_tin_khoa_ngon_ngu",  # thông tin về khoa ngôn ngữ
            "thong_tin_khoa_kinh_te",  # thông tin về khoa kinh tế
            "thong_tin_khoa_y",  # thông tin về khoa y
            "thong_tin_khoa_cong_nghe_sinh_hoc",  # thông tin về khoa công nghệ sinh học
            "thong_tin_khoa_dieu_duong",  # thông tin về khoa điều dưỡng
            "thong_tin_khoa_khai_phong",  # thông tin về khoa khai phóng
            "thong_tin_giang_vien",    # thông tin về giảng viên
            "thong_tin_nghien_cuu",     # thông tin về nghiên cứu
            "thong_tin_chi_phi",     # thông tin về tất cả chi phí (học phí, nợ môn, thi lại, v.v.)
        ],
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



@tool
async def vectorize(content: List[str]) -> List[List[float]]:
    """
    Sends a [query] to an embedding API for vectorization and retrieves their vector representations.

    Args:
        content (List[str]): A list of strings to be vectorized.

    Returns:
        List[List[float]]: A list of vector representations for the input content.
    """
    url = "http://128.214.255.226:5000/vectorize"
    
    payload = {
        "content": content}

    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json().get("vectors")


@tool
async def search_at_thong_tin_truong_dai_hoc(query: str, vector: List[float]) -> Dict:
    """
    Search for relevant documents in the "thong_tin_truong_dai_hoc" collection using a query string and a vector.

    Args:
        query (str): The textual query to search for within the collection.
        vector (List[float]): The vector representation of the query for vector-based search.

    Returns:
        Dict: The search results retrieved from the vector database, containing relevant documents.
    """
    return await query_vectordb(collection_name="thong_tin_truong_dai_hoc", content=query, vector=vector, limit=7)

@tool
async def search_at_thong_tin_khoa_cong_nghe_thong_tin(query: str, vector: List[float]) -> Dict:
    """
    Search for relevant documents in the "thong_tin_khoa_cong_nghe_thong_tin" collection using a query string and a vector.

    Args:
        query (str): The textual query to search for within the collection.
        vector (List[float]): The vector representation of the query for vector-based search.

    Returns:
        Dict: The search results retrieved from the vector database, containing relevant documents.
    """
    return await query_vectordb(collection_name="thong_tin_khoa_cong_nghe_thong_tin", content=query, vector=vector, limit=7)
    
@tool
async def search_at_thong_tin_chi_phi(query: str, vector: List[float]) -> Dict:
    """
    Search for relevant documents in the "thong_tin_chi_phi" collection using a query string and a vector.

    Args:
        query (str): The textual query to search for within the collection.
        vector (List[float]): The vector representation of the query for vector-based search.

    Returns:
        Dict: The search results retrieved from the vector database, containing relevant documents.
    """
    return await query_vectordb(collection_name="thong_tin_chi_phi", content=query, vector=vector, limit=7)

@tool
async def get_chat_history(user: str) -> List[str]:
    """
    Retrieve the chat history for a specific user.

    Args:
        user (str): The user for whom the chat history is to be retrieved.

    Returns:
        List[str]: The chat history for the specified user.
    """
    url = f"http://0.0.0.0:8000/knowledge/history?user={user}"
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.get(url, timeout=timeout)
        response.raise_for_status()

    return response.json().get("history")


@tool
async def add_chat_history(user: str, messages: List[str]) -> Dict:
    """
    Add chat history to the database.

    Args:
        user (str): The user for whom the chat history is to be added.
        messages (List[str]): The list of messages to be added to the chat history.

    Returns:
        Dict: The response from the database.
    """
    url = "http://0.0.0.0:8000/knowledge/history"
    
    payload = {
        "user": user,
        "messages": messages
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    
    return response.json()