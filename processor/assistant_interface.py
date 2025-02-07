from processor.models import State


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

