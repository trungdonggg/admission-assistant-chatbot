from processor.agent import Agent
from processor.history_adapter import HistoryAdapter
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from processor.models import SearchRequest
import os
from aio_pika import connect_robust
from aio_pika.patterns import RPC
import asyncio
from config import rabbitmq_url, all_queues
import dotenv
dotenv.load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

agent: Agent

async def search(request: SearchRequest):
    try:
        res = await agent.ainvoke({
            "messages": [HumanMessage(content=request.query)], 
            "user": request.user
            })
        
        return {
            "user": request.user,
            "response": res["messages"][-1].content
        }

    except Exception as e:
        logger.error(f"Error in searching: {str(e)}", exc_info=True)
        raise Exception("Error in searching")
    


async def main():
    global agent

    connection = await connect_robust(rabbitmq_url)
    
    channel_processor = await connection.channel()
    processor_rpc = await RPC.create(channel_processor)
    
    channel_embedder = await connection.channel()
    embedder_rpc = await RPC.create(channel_embedder)
    
    channel_vectordb = await connection.channel()
    vectordb_rpc = await RPC.create(channel_vectordb)

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=os.getenv("GOOGLE_AI_API_KEY"),
    )
    history_adapter = HistoryAdapter(llm=llm)
    
    agent = Agent(history_adapter=history_adapter, llm=llm, vdb_rpc=vectordb_rpc, emb_rpc=embedder_rpc).build_graph()
    
    await processor_rpc.register(all_queues["processor"], search, auto_delete=True)

    logger.info("Processor is running and waiting for requests...")

    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
