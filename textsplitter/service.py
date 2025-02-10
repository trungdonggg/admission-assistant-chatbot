import asyncio
import logging
from aio_pika import connect_robust
from aio_pika.patterns import RPC
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import rabbitmq_url, all_queues

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

chunk_size = 200
chunk_overlap = 20

async def split_text_handler(request: str) -> dict:
    """Handler for text splitting requests"""
    try:
        logger.info(f"Received text splitting request with length: {len(request)}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", "."],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        chunks = text_splitter.split_text(request)
        logger.info(f"Successfully split text into {len(chunks)} chunks")
        logger.debug(f"First chunk preview: {chunks[0][:100]}...")
        
        return {"chunks": chunks}

    except Exception as e:
        logger.error(f"Error in splitting text: {str(e)}", exc_info=True)
        raise Exception(f"Error in splitting text: {str(e)}")

async def main():
    """Main entry point to start the RPC server."""
    logger.info("Starting text splitter service...")
    try:
        # Establish connection with RabbitMQ
        logger.info(f"Connecting to RabbitMQ at {rabbitmq_url}")
        connection = await connect_robust(rabbitmq_url)
        channel = await connection.channel()
        logger.info("Successfully connected to RabbitMQ")

        # Create RPC server
        rpc = await RPC.create(channel)
        logger.info("RPC server created")

        # Register handler for text splitting requests
        queue_name = all_queues["textsplitter"]
        await rpc.register(queue_name, split_text_handler, auto_delete=True)
        logger.info(f"Registered handler for queue: {queue_name}")

        logger.info("Text splitter service is running and waiting for RPC calls...")

        # Keep the service running
        await asyncio.Future()

    except Exception as e:
        logger.error(f"Critical error in text splitter service: {str(e)}", exc_info=True)
        raise

    finally:
        logger.info("Shutting down text splitter service...")
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