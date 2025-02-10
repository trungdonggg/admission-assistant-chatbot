import asyncio
import logging
from aio_pika import connect_robust
from aio_pika.patterns import RPC
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import rabbitmq_url, all_queues

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


chunk_size = 200
chunk_overlap = 20

async def split_text_handler(request: str) -> dict:
    """Handler for text splitting requests"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", "."],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        chunks = text_splitter.split_text(request)
        return {"chunks": chunks}

    except Exception as e:
        logger.error(f"Error in splitting text: {str(e)}", exc_info=True)
        raise Exception(f"Error in splitting text: {str(e)}")

async def main():
    """Main entry point to start the RPC server."""
    try:
        # Establish connection with RabbitMQ
        connection = await connect_robust(rabbitmq_url)
        channel = await connection.channel()

        # Create RPC server
        rpc = await RPC.create(channel)

        # Register handler for text splitting requests
        await rpc.register(all_queues["textsplitter"], split_text_handler, auto_delete=True)

        logger.info("Text splitter service is running and waiting for RPC calls...")

        # Keep the service running
        await asyncio.Future()

    except Exception as e:
        logger.error(f"Error in text splitter service: {str(e)}", exc_info=True)

    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main()) 