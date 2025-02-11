from processor.models import State


class Assistant:
    def __init__(self, runnable):
        self.runnable = runnable
        
    async def __call__(self, state: State):
        max_retries = 3
        retries = 0
        
        while retries < max_retries:
            try:
                result = await self.runnable.ainvoke(state)
                
                if not result.tool_calls and (
                    not result.content
                    or isinstance(result.content, list) and not result.content[0].get("text")
                ):
                    state["messages"].append(("user", "Respond with a real output."))
                    retries += 1
                    continue
                
                return {"messages": result}
                
            except Exception as e:
                retries += 1
                if retries == max_retries:
                    raise RuntimeError(f"Failed to get valid response after {max_retries} attempts") from e
                continue