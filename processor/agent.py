from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from processor.defined_tools import *
from processor.models import State
from processor.history_adapter import HistoryAdapter
from processor.assistant_interface import Assistant
from aio_pika.patterns import RPC
from processor.defined_tools import *
from typing import Callable, Awaitable, Any


def create_async_search_wrapper(
    func: Callable[[str, Any, Any], Awaitable[str]], 
    name: str, 
    description: str,
    vdb_rpc: Any,
    emb_rpc: Any
) -> Callable[[str], Awaitable[str]]:
    """Create an async search wrapper with injected RPC clients.
    
    Args:
        func: The async search function to wrap
        name: Name of the function
        description: Description of what the function does
        vdb_rpc: Vector database RPC client
        emb_rpc: Embedder RPC client
    """
    async def wrapper(query: str) -> str:
        """
        Args:
            query: The search query string
            
        Returns:
            Search results as a string
        """
        return await func(query, vdb_rpc=vdb_rpc, emb_rpc=emb_rpc)
    
    wrapper.__name__ = name
    wrapper.__doc__ = description
    return wrapper


class Agent:
    def __init__(
        self,
        history_adapter: HistoryAdapter,
        llm: BaseChatModel,
        vdb_rpc: RPC,
        emb_rpc: RPC
    ):
        self.history_adapter = history_adapter
        self.llm = llm
        
        self.query_tools = [
            create_async_search_wrapper(
                search_at_thong_tin_chi_phi,
                "search_at_thong_tin_chi_phi",
                "Tìm kiếm thông tin về học phí và chi phí",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_truong_dai_hoc,
                "search_at_thong_tin_truong_dai_hoc",
                "Tìm kiếm thông tin chung về Đại học Tân Tạo",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_khoa_cong_nghe_thong_tin,
                "search_at_thong_tin_khoa_cong_nghe_thong_tin",
                "Tìm kiếm thông tin về Khoa Công nghệ Thông tin",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_khoa_ngon_ngu,
                "search_at_thong_tin_khoa_ngon_ngu",
                "Tìm kiếm thông tin về Khoa Ngôn ngữ",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_khoa_kinh_te,
                "search_at_thong_tin_khoa_kinh_te",
                "Tìm kiếm thông tin về Khoa Kinh tế",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_khoa_y,
                "search_at_thong_tin_khoa_y",
                "Tìm kiếm thông tin về Khoa Y",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_khoa_cong_nghe_sinh_hoc,
                "search_at_thong_tin_khoa_cong_nghe_sinh_hoc",
                "Tìm kiếm thông tin về Khoa Công nghệ Sinh học",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_khoa_dieu_duong,
                "search_at_thong_tin_khoa_dieu_duong",
                "Tìm kiếm thông tin về Khoa Điều dưỡng",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_khoa_khai_phong,
                "search_at_thong_tin_khoa_khai_phong",
                "Tìm kiếm thông tin về Khoa Khai Phong",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_giang_vien,
                "search_at_thong_tin_giang_vien",
                "Tìm kiếm thông tin về giảng viên và giáo sư",
                vdb_rpc,
                emb_rpc
            ),
            create_async_search_wrapper(
                search_at_thong_tin_nghien_cuu,
                "search_at_thong_tin_nghien_cuu",
                "Tìm kiếm thông tin về hoạt động và dự án nghiên cứu",
                vdb_rpc,
                emb_rpc
            )
        ]

        

        self.primary_assistant_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an assistant for Tan Tao University. You speak in Vietnamese. "
                "Your first priority is to use the provided tools to search for information to assist with user queries. "
                "Always attempt to find answers using the tools before considering other methods. "
                "Be persistent and flexible in using the tools. If a search does not return results, expand the search scope or combine multiple tools to increase accuracy. "
                "When encountering complex questions, use multiple tools simultaneously to provide the most accurate information. "
                "Here is a summary of the chat history: {summary}. "
                "Most recent chat history: {old_conversation}. "
            ),
            ("placeholder", "{messages}"),
        ])

        
        # Create chain with tools that have RPC clients injected
        self.chain = self.primary_assistant_prompt | llm.bind_tools(self.query_tools)

    def build_graph(self):
        builder = StateGraph(State)
        
        # Add nodes
        builder.add_node("summarizer", self.history_adapter.add_chat_history)
        builder.add_node("history", self.history_adapter.get_chat_history)
        builder.add_node("tools", ToolNode(self.query_tools))
        builder.add_node("assistant", Assistant(self.chain))
        
        # Add edges
        builder.add_edge(START, "history")
        builder.add_edge("history", "assistant")
        builder.add_conditional_edges("assistant", router)
        builder.add_edge("tools", "assistant")
        builder.add_edge("summarizer", END)
        
        return builder.compile()
