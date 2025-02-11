import asyncio
import logging
from aio_pika import connect_robust
from aio_pika.patterns import RPC
from vector_database.weaviatedb import WeaviateDB
import categry
from config import all_queues, rabbitmq_url
from vector_database.models import *

# Configure logging with more detailed format
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

weaviate_db: WeaviateDB = None

async def setup_database():
    """Setup the database connection and initialize collections."""
    logger.info("Initializing vector database connection...")
    global weaviate_db
    weaviate_db = WeaviateDB()
    await weaviate_db.connect()
    logger.info("Successfully connected to Weaviate")

    # Ensure collections exist
    for collection in categry.collkts:
        collection_vdb = weaviate_db.get_collection(collection)
        if not await collection_vdb.exists():
            await weaviate_db.create_collection(collection)
            logger.info(f"Created collection: {collection}")
        else:
            logger.info(f"Collection exists: {collection}")


async def teardown_database():
    """Close the database connection."""
    logger.info("Closing database connection...")
    global weaviate_db
    if weaviate_db:
        await weaviate_db.close_connection()
        logger.info("Database connection closed")


async def add_document_handler(data: Dict) -> Dict:
    """Handler for adding a document."""
    try:
        logger.info(f"Adding document '{data.get('document_name')}' to collections: {data['collection_name']}")
        # Create a copy of data without collection_name
        document_data = {k: v for k, v in data.items() if k != "collection_name"}
        
        for c in data["collection_name"]:
            logger.debug(f"Adding to collection {c}")
            await weaviate_db.add_document(collection_name=c, **document_data)
            logger.info(f"Successfully added document to collection {c}")
        return {"message": "Document added successfully"}
    except Exception as e:
        logger.error(f"Error in adding document: {str(e)}", exc_info=True)
        # Rollback
        try:
            logger.info("Starting rollback process...")
            for c in data["collection_name"]:
                await weaviate_db.remove_document(c, data["document_name"])
                logger.info(f"Rolled back document from collection {c}")
        except Exception as cleanup_error:
            logger.error(f"Error during rollback: {str(cleanup_error)}", exc_info=True)
        raise Exception("Error in adding document")


async def query_handler(data: Dict) -> Dict:
    """Handler for querying documents."""
    try:
        logger.info("Processing query request")
        logger.debug(f"Query parameters: {data}")
        response = await weaviate_db.query(data)
        logger.info(f"Query returned {len(response) if response else 0} results")
        return {"query_results": response}
    except Exception as e:
        logger.error(f"Error in querying: {str(e)}", exc_info=True)
        raise Exception("Error in querying")


async def remove_document_handler(data: Dict) -> Dict:
    """Handler for removing a document."""
    try:
        logger.info(f"Removing document '{data['document_name']}' from collections: {data['collection_name']}")
        for c in data["collection_name"]:
            logger.debug(f"Removing from collection {c}")
            await weaviate_db.remove_document(c, data["document_name"])
            logger.info(f"Successfully removed document from collection {c}")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        logger.error(f"Error in deleting document: {str(e)}", exc_info=True)
        raise Exception("Error in deleting document")


async def general_handler(request: Dict) -> Dict:
    """Handler for general RPC calls."""
    try:
        method = request["method"]
        data = request["data"]
        logger.info(f"Received RPC request with method: {method}")
        
        if method == "add_document":
            return await add_document_handler(data)
        elif method == "query":
            return await query_handler(data)
        elif method == "remove_document":
            return await remove_document_handler(data)
        else:
            logger.error(f"Invalid method received: {method}")
            raise ValueError(f"Invalid method: {method}")
            
    except Exception as e:
        logger.error(f"Error in general handler: {str(e)}", exc_info=True)
        raise


async def main():
    """Main entry point to start the RPC server."""
    logger.info("Starting vector database service...")
    await setup_database()

    try:
        logger.info(f"Connecting to RabbitMQ at {rabbitmq_url}")
        connection = await connect_robust(rabbitmq_url)
        channel = await connection.channel()
        rpc = await RPC.create(channel)
        logger.info("Successfully connected to RabbitMQ")

        # Register RPC handlers
        queue_name = all_queues["vectordb"]
        await rpc.register(queue_name, general_handler, auto_delete=True)
        logger.info(f"Registered RPC handler for queue: {queue_name}")

        logger.info("Vector Database is running and waiting for RPC calls...")

        # Keep the service running
        await asyncio.Future()

    except Exception as e:
        logger.error(f"Critical error in Vector Database: {str(e)}", exc_info=True)
        raise

    finally:
        logger.info("Shutting down vector database service...")
        if 'connection' in locals():
            await connection.close()
            logger.info("RabbitMQ connection closed")
        await teardown_database()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.critical(f"Service crashed: {str(e)}", exc_info=True)
