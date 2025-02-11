from config import knowledge_manager_api_host, knowledge_manager_api_port
from langchain_core.language_models import BaseChatModel
from processor.models import State
import httpx


class HistoryAdapter:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.base_url = f"http://{knowledge_manager_api_host}:{knowledge_manager_api_port}/knowledge/history"
        self.timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)
    
    async def get_chat_history(self, state: State):
        try:
            url = f"{self.base_url}?user={state['user']}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                return {
                    "summary": data.get("summary"),
                    "old_conversation": data.get("conversation", [])[-6:],
                }
        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch chat history: {str(e)}") from e

    async def add_chat_history(self, state: State) -> None:
        max_retries = 3
        retries = 0
        
        while retries < max_retries:
            try:
                summary_prompt = (
                    f"Using the previous summary: '{state['summary']}' and the conversation between "
                    f"the user and the assistant, which includes: \n"
                    f"User: {state['messages'][0].content}\n"
                    f"Assistant: {state['messages'][-1].content}\n"
                    "provide a concise summary of the old summary and interaction."
                )
                
                summary = await self.llm.ainvoke(summary_prompt)
                
                if not summary.tool_calls and (
                    not summary.content
                    or isinstance(summary.content, list) and not summary.content[0].get("text")
                ):
                    state["messages"].append(("user", "Respond with a real output."))
                    retries += 1
                    continue
                
                payload = {
                    "user": state["user"],
                    "messages": [m.model_dump_json() for m in state["messages"]],
                    "conversation": [
                        {"role": "user", "content": state["messages"][0].content},
                        {"role": "assistant", "content": state["messages"][-1].content}
                    ],
                    "summary": summary.content
                }
                
                headers = {'Content-Type': 'application/json'}
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    return response.json()
                    
            except (httpx.HTTPError, Exception) as e:
                retries += 1
                if retries == max_retries:
                    raise RuntimeError(f"Failed to add chat history after {max_retries} attempts") from e
                continue