from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from processor.defined_tools import *
from processor.models import State
from processor.history_adapter import HistoryAdapter
from processor.assistant_interface import Assistant
from aio_pika.patterns import RPC
from langchain.tools import Tool
from processor.defined_tools import *

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
            Tool.from_function(
                func=lambda x: search_at_thong_tin_truong_dai_hoc(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_truong_dai_hoc",
                description="""
                    Search for relevant documents in the 'thong_tin_truong_dai_hoc' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_khoa_cong_nghe_thong_tin(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_khoa_cong_nghe_thong_tin",
                description="""
                    Search for relevant documents in the 'thong_tin_khoa_cong_nghe_thong_tin' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_khoa_ngon_ngu(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_khoa_ngon_ngu",
                description="""
                    Search for relevant documents in the 'thong_tin_khoa_ngon_ngu' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_khoa_kinh_te(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_khoa_kinh_te",
                description="""
                    Search for relevant documents in the 'thong_tin_khoa_kinh_te' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_khoa_y(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_khoa_y",
                description="""
                    Search for relevant documents in the 'thong_tin_khoa_y' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_khoa_cong_nghe_sinh_hoc(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_khoa_cong_nghe_sinh_hoc",
                description="""
                    Search for relevant documents in the 'thong_tin_khoa_cong_nghe_sinh_hoc' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_khoa_dieu_duong(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_khoa_dieu_duong",
                description="""
                    Search for relevant documents in the 'thong_tin_khoa_dieu_duong' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_khoa_khai_phong(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_khoa_khai_phong",
                description="""
                    Search for relevant documents in the 'thong_tin_khoa_khai_phong' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_giang_vien(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_giang_vien",
                description="""
                    Search for relevant documents in the 'thong_tin_giang_vien' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_nghien_cuu(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_nghien_cuu",
                description="""
                    Search for relevant documents in the 'thong_tin_nghien_cuu' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
            Tool.from_function(
                func=lambda x: search_at_thong_tin_chi_phi(x, vdb_rpc, emb_rpc),
                name="search_at_thong_tin_chi_phi",
                description="""
                    Search for relevant documents in the 'thong_tin_chi_phi' collection using a query string.

                    Args:
                        query (str): The textual query to search for within the collection.

                    Returns:
                        str: The search results retrieved from the vector database, containing relevant documents.
                """,
            ),
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