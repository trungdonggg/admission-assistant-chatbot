from typing_extensions import TypedDict
from pydantic import BaseModel
# from processor.defined_tools import *
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated
from langgraph.graph.message import AnyMessage, add_messages
import os
import dotenv
dotenv.load_dotenv()

# class State(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]



# class Assistant:
#     def __init__(self, runnable: Runnable):
#         self.runnable = runnable

#     def __call__(self, state: State):
#         while True:
#             result = self.runnable.invoke(state)
#             # If the LLM happens to return an empty response, we will re-prompt it
#             # for an actual response.
#             if not result.tool_calls and (
#                 not result.content
#                 or isinstance(result.content, list)
#                 and not result.content[0].get("text")
#             ):
#                 messages = state["messages"] + [("user", "Respond with a real output.")]
#                 state = {**state, "messages": messages}
#             else:
#                 break
#         return {"messages": result}

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_AI_API_KEY"), temperature=0.7)


# primary_assistant_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful support assistant for university. You speak in Vietnamese."
#             " Use the provided tools to search for information to assist the user's queries. "
#             " When searching, be persistent. Expand your query bounds if the first search returns no results. "
#             " If a search comes up empty, expand your search before giving up."
#             "The current user is {user}"
#         ),
#         ("placeholder", "{messages}"),
#     ]
# ).partial(user="dongtrungtran")

# part_1_tools = [
#     vectorize,
#     add_chat_history,
#     search_at_thong_tin_truong_dai_hoc,
#     get_chat_history,
# ]
# part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(part_1_tools)


# from langgraph.graph import END, StateGraph, START
# from langgraph.prebuilt import tools_condition

# builder = StateGraph(State)


# builder.add_node("assistant", Assistant(part_1_assistant_runnable))
# builder.add_node("tools", create_tool_node_with_fallback(part_1_tools))

# builder.add_edge(START, "assistant")
# builder.add_conditional_edges(
#     "assistant",
#     tools_condition,
# )
# builder.add_edge("tools", "assistant")

# part_1_graph = builder.compile()

# tutorial_questions = [
#     "Dia chi dai hoc bach khoa",
#     "truong thanh lap nam nao",
#     "ai la hieu truong"
# ]



# _printed = set()
# for question in tutorial_questions:
#     events = part_1_graph.stream(
#         {"messages": ("user", question)}, stream_mode="values"
#     )
#     for event in events:
#         print_event(event, _printed)

from typing import Annotated
from langgraph.graph.message import add_messages

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


from langchain_core.messages import AIMessage, HumanMessage

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

llm_with_tools = llm.bind_tools([multiply])
tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 2 multiplied by 3", name="Lance")])
print(tool_call)