from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from processor.defined_tools import *


class Assistant:
    def __init__(self, runnable):
        self.runnable = runnable

    async def __call__(self, state: State):
        while True:
            result = await self.runnable.ainvoke(state)
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list) and not result.content[0].get("text")
            ):
                state["messages"].append(("user", "Respond with a real output."))
            else:
                break
        return {"messages": result}


class Agent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.query_tools = [
            search_at_thong_tin_truong_dai_hoc,
            search_at_thong_tin_khoa_cong_nghe_thong_tin,
            search_at_thong_tin_chi_phi,
        ]

        self.primary_assistant_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful assistant. If you don't know the answer, use the provided tools to query the vector database for information before responding to the user. "
                "Chat history summary: {summary}"
            ),
            ("placeholder", "{messages}"),
        ])

        self.chain = self.primary_assistant_prompt | llm.bind_tools(self.query_tools)

    def build_graph(self):
        builder = StateGraph(State)

        builder.add_node("summarizer", add_chat_history(llm=self.llm))
        builder.add_node("history", get_chat_history)
        builder.add_node("tools", ToolNode(self.query_tools))
        builder.add_node("assistant", Assistant(self.chain))

        builder.add_edge(START, "history")
        builder.add_edge("history", "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
        builder.add_edge("summarizer", END)

        return builder.compile()
