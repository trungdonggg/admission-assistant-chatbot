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
    logger.info("Initializing embedder...")
    global embedder
    try:
        embedder = Embedding()
        logger.info("Embedder initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embedder: {str(e)}", exc_info=True)
        raise


async def embed_handler(request: List[str]) -> Dict:
    """Handler for embedding requests."""
    try:
        logger.info(f"Received embedding request for {len(request)} texts")
        logger.debug(f"First text preview: {request[0][:100]}..." if request else "Empty request")
        
        # Embed the content received in the RPC request
        response = await embedder.embed(request)
        
        logger.info(f"Successfully generated embeddings with shape: {len(response)}x{len(response[0]) if response else 0}")
        return {"vectors": response}
    
    except Exception as e:
        logger.error(f"Error in generating embedding: {str(e)}", exc_info=True)
        raise Exception("Error in generating embedding")


async def main():
    """Main entry point to start the RPC server."""
    logger.info("Starting embedding service...")
    try:
        await setup_embedder()  # Initialize the embedder

        # Establish connection with RabbitMQ
        logger.info(f"Connecting to RabbitMQ at {rabbitmq_url}")
        connection = await connect_robust(rabbitmq_url)
        channel = await connection.channel()
        logger.info("Successfully connected to RabbitMQ")

        # Create RPC server
        rpc = await RPC.create(channel)
        logger.info("RPC server created")

        # Register handler for embedding requests
        queue_name = all_queues["embedder"]
        await rpc.register(queue_name, embed_handler, auto_delete=True)
        logger.info(f"Registered handler for queue: {queue_name}")

        logger.info("Embedding service is running and waiting for RPC calls...")

        # Keep the service running
        await asyncio.Future()

    except Exception as e:
        logger.error(f"Critical error in embedding service: {str(e)}", exc_info=True)
        raise

    finally:
        logger.info("Shutting down embedding service...")
        if 'connection' in locals():
            await connection.close()
            logger.info("RabbitMQ connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.critical(f"Service crashed: {str(e)}", exc_info=True)
