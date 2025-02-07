from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from processor.defined_tools import *
from langchain_core.language_models import BaseChatModel
from processor.models import State
from processor.history_adapter import HistoryAdapter
from processor.assistant_interface import Assistant
from aio_pika.patterns import RPC
from functools import wraps


def with_rpc(vdb_rpc: RPC, emb_rpc: RPC):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, vdb_rpc, emb_rpc, **kwargs)
        return wrapper
    return decorator


class Agent:
    def __init__(self, history_adapter: HistoryAdapter, llm: BaseChatModel, vdb_rpc: RPC, emb_rpc: RPC):
        self.history_adapter = history_adapter
        self.llm = llm
        self.query_tools = [
            with_rpc(vdb_rpc, emb_rpc)(tool)
            for tool in [
                search_at_thong_tin_truong_dai_hoc,
                search_at_thong_tin_khoa_cong_nghe_thong_tin,
                search_at_thong_tin_khoa_ngon_ngu,
                search_at_thong_tin_khoa_kinh_te,
                search_at_thong_tin_khoa_y,
                search_at_thong_tin_khoa_cong_nghe_sinh_hoc,
                search_at_thong_tin_khoa_dieu_duong,
                search_at_thong_tin_khoa_khai_phong,
                search_at_thong_tin_giang_vien,
                search_at_thong_tin_nghien_cuu,
                search_at_thong_tin_chi_phi,
            ]
        ]
        self.primary_assistant_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Bạn là một trợ lý cho Đại học Tân Tạo. Bạn nói bằng tiếng Việt. "
                "Sử dụng các công cụ được cung cấp để tìm kiếm thông tin về trường đại học, học phí, và các thông tin khác để hỗ trợ các câu hỏi của người dùng. "
                "Hãy kiên trì và linh hoạt trong cách sử dụng các công cụ. Nếu một tìm kiếm không trả về kết quả, hãy mở rộng phạm vi tìm kiếm hoặc kết hợp nhiều công cụ để tăng độ chính xác. "
                "Khi gặp câu hỏi phức tạp, sử dụng nhiều công cụ cùng lúc để cung cấp thông tin chính xác nhất. "
                "Đây là tóm tắt của lịch sử trò chuyện: {summary}. "
                "Lịch sử trò chuyện gần nhất: {old_conversation}. "
            ),
            ("placeholder", "{messages}"),
        ])
        self.chain = self.primary_assistant_prompt | llm.bind_tools(self.query_tools)

    def build_graph(self):
        builder = StateGraph(State)

        builder.add_node("summarizer", self.history_adapter.add_chat_history)
        builder.add_node("history", self.history_adapter.get_chat_history)
        builder.add_node("tools", ToolNode(self.query_tools))
        builder.add_node("assistant", Assistant(self.chain))

        builder.add_edge(START, "history")
        builder.add_edge("history", "assistant")
        builder.add_conditional_edges("assistant", router)
        builder.add_edge("tools", "assistant")
        builder.add_edge("summarizer", END)

        return builder.compile()
