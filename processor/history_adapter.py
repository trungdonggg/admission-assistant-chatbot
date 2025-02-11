from config import knowledge_manager_api_host, knowledge_manager_api_port
from langchain_core.language_models import BaseChatModel
from processor.models import State
import httpx


class HistoryAdapter:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
    
    async def get_chat_history(self, state: State):
        user = state["user"]
        url = f"http://{knowledge_manager_api_host}:{knowledge_manager_api_port}/knowledge/history?user={user}"
        
        async with httpx.AsyncClient() as client:
            timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()

        return {
            "summary": response.json().get("summary"),
            "old_conversation": response.json().get("conversation")[-6:],
        }


    async def add_chat_history(self, state: State) -> None:

        while True:
            summary = await self.llm.ainvoke(
                    f"Using the previous summary: '{state['summary']}' and the conversation between the user and the assistant, "
                    f"which includes: \nUser: {state['messages'][0].content}\nAssistant: {state['messages'][-1].content}\n"
                    "provide a concise summary of the old summary and interaction."
                )
            if not summary.tool_calls and (
                not summary.content
                or isinstance(summary.content, list) and not summary.content[0].get("text")
            ):
                state["messages"].append(("user", "Respond with a real output."))
            else:
                break
        
        url = f"http://{knowledge_manager_api_host}:{knowledge_manager_api_port}/knowledge/history"
        
        payload = {
            "user": state["user"],
            "messages": [m.model_dump_json() for m in state["messages"]],
            "conversation": [
                {"role": "user", "content": state["messages"][0].content}, 
                {"role": "assistant", "content": state["messages"][-1].content}
            ],
            "summary": summary.content
        }
        
        print(payload)
        
        headers = {
            'Content-Type': 'application/json'
        }
        async with httpx.AsyncClient() as client:
            timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
            response = await client.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
        
        return response.json()
        