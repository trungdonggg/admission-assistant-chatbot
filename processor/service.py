from processor.agent import Agent
from processor.history_adapter import HistoryAdapter
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
from aio_pika import connect_robust
from aio_pika.patterns import RPC
import asyncio
from config import rabbitmq_url, all_queues
import dotenv
# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: Agent = None

async def search(request: dict) -> dict:
    """
    Handles search requests using the initialized agent.
    """
    try:
        logger.info(f"Received search request for user {request['user']} with query: {request['query']}")
        res = await agent.ainvoke({
            "messages": [HumanMessage(content=request["query"])], 
            "user": request["user"]
        })

        logger.info(f"Response for user {request['user']} generated: {res['messages'][-1].content}")
        return {
            "user": request["user"],
            "response": res["messages"][-1].content
        }

    except KeyError as e:
        logger.error(f"Missing key in response: {str(e)}", exc_info=True)
        raise Exception("Unexpected response format")
    except Exception as e:
        logger.error(f"Error in searching: {str(e)}", exc_info=True)
        raise Exception(f"Error in searching: {str(e)}")

async def main():
    """
    Main function to set up RabbitMQ connections and initialize the agent.
    """
    global agent

    # Establish robust connection to RabbitMQ
    connection = await connect_robust(rabbitmq_url)
    logger.info("Connected to RabbitMQ")

    # Set up channels and RPCs
    channel_processor = await connection.channel()
    processor_rpc = await RPC.create(channel_processor)
    logger.info("Set up processor RPC")

    channel_embedder = await connection.channel()
    embedder_rpc = await RPC.create(channel_embedder)
    logger.info("Set up embedder RPC")

    channel_vectordb = await connection.channel()
    vectordb_rpc = await RPC.create(channel_vectordb)
    logger.info("Set up vector database RPC")

    # Initialize the language model
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=os.getenv("GOOGLE_AI_API_KEY"),
    )
    logger.info("Initialized language model")

    # Initialize the history adapter
    history_adapter = HistoryAdapter(llm=llm)
    logger.info("Initialized history adapter")

    # Build the agent with provided components
    agent = Agent(history_adapter=history_adapter, llm=llm, vdb_rpc=vectordb_rpc, emb_rpc=embedder_rpc).build_graph()
    logger.info("Built the agent graph")

    # Register the search function with the processor queue
    await processor_rpc.register(all_queues["processor"], search, auto_delete=True)
    logger.info("Registered search function with processor queue")

    logger.info("Processor is running and waiting for requests...")

    # Keep the service running
    try:
        await asyncio.Future()  # Run forever

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

    finally:
        logger.info("Closing RabbitMQ connection...")
        await connection.close()  # Ensure connection is closed properly

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted and shutting down gracefully.")

