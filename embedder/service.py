import asyncio
import logging
from aio_pika import connect_robust
from aio_pika.patterns import RPC
from embedder.embed import Embedding
from config import rabbitmq_url, all_queues
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global embedder
embedder: Embedding = None


async def setup_embedder():
    """Setup embedder instance."""
    global embedder
    embedder = Embedding()


async def embed_handler(request: List[str]) -> Dict:
    """Handler for embedding requests."""
    try:
        # Embed the content received in the RPC request
        response = await embedder.embed(request)
        return {"vectors": response}
    except Exception as e:
        logger.error(f"Error in generating embedding: {str(e)}", exc_info=True)
        raise Exception("Error in generating embedding")


async def main():
    """Main entry point to start the RPC server."""
    await setup_embedder()  # Initialize the embedder

    try:
        # Establish connection with RabbitMQ
        connection = await connect_robust(rabbitmq_url)
        channel = await connection.channel()

        # Create RPC server
        rpc = await RPC.create(channel)

        # Register handler for embedding requests
        await rpc.register(all_queues["embedder"], embed_handler, auto_delete=True)

        logger.info("Embedding service is running and waiting for RPC calls...")

        # Keep the service running
        await asyncio.Future()

    except Exception as e:
        logger.error(f"Error in embedding service: {str(e)}", exc_info=True)

    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
