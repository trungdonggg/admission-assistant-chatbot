from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.prompts import ChatPromptTemplate
from processor.defined_tools import *
from langchain_core.language_models import BaseChatModel



class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    summary: str
    user: str
    

class HistoryAdapter:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
    
    async def get_chat_history(self, state: State):
        user = state["user"]
        url = f"http://{knowledge_management_api_host}:{knowledge_management_api_port}/knowledge/history?user={user}"
        
        async with httpx.AsyncClient() as client:
            timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()

        return {
            "summary": response.json().get("summary"),
        }


    async def add_chat_history(self, state: State) -> None:

        while True:
            summary = await self.llm.ainvoke(
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
        
        return state
        
        # url = f"http://{knowledge_management_api_host}:{knowledge_management_api_port}/knowledge/history"
        
        # payload = {
        #     "user": state["user"],
        #     "messages": state["messages"],
        #     "conversation": [state["messages"][0], state["messages"][-1]],
        #     "summary": summary
        # }
        
        # print(payload)
        
        # headers = {
        #     'Content-Type': 'application/json'
        # }
        # print('\nAdd chat history\n')
        # async with httpx.AsyncClient() as client:
        #     timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
        #     response = await client.post(url, headers=headers, json=payload, timeout=timeout)
        #     response.raise_for_status()
        
        # return response.json()
        


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
    def __init__(self, history_adapter: HistoryAdapter, llm: BaseChatModel):
        self.history_adapter = history_adapter
        self.llm = llm
        self.query_tools = [
            search_at_thong_tin_truong_dai_hoc,
            search_at_thong_tin_khoa_cong_nghe_thong_tin,
            search_at_thong_tin_chi_phi,
        ]

        self.primary_assistant_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful assistant for Bach Khoa University. You speak in Vietnamese. "
                "Remember all the questions of user is asks about Bach Khoa University. "
                "If you don't know the answer, dont respond yet, you first priority is to use the provided tools to find information."
                "Chat history summary: {summary}"
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

#  If you don't know the answer, use the provided tools to query the vector database for information before responding to the user.