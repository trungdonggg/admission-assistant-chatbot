import asyncio
import logging
from aio_pika import connect_robust
from aio_pika.patterns import RPC
from vector_database.weaviatedb import WeaviateDB
import categry
from config import all_queues, rabbitmq_url
from vector_database.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



weaviate_db: WeaviateDB = None

async def setup_database():
    """Setup the database connection and initialize collections."""
    global weaviate_db
    weaviate_db = WeaviateDB()
    await weaviate_db.connect()

    # Ensure collections exist
    for collection in categry.collkts:
        collection_vdb = weaviate_db.get_collection(collection)
        if not await collection_vdb.exists():
            await weaviate_db.create_collection(collection)


async def teardown_database():
    """Close the database connection."""
    global weaviate_db
    if weaviate_db:
        await weaviate_db.close_connection()


async def add_document_handler(data: AddDocumentRequest):
    """Handler for adding a document."""
    try:
        for c in data.collection_name:
            await weaviate_db.add_document(**data.model_dump(), collection_name=c)
        return {"message": "Document added successfully"}
    except Exception as e:
        logger.error(f"Error in adding document: {str(e)}", exc_info=True)
        # Rollback
        for c in data.collection_name:
            await weaviate_db.remove_document(c, data.document_name)
        raise Exception("Error in adding document")


async def query_handler(data: QueryRequest):
    """Handler for querying documents."""
    try:
        response = await weaviate_db.query(**data.model_dump())
        return {"query_results": response}
    except Exception as e:
        logger.error(f"Error in querying: {str(e)}", exc_info=True)
        raise Exception("Error in querying")


async def remove_document_handler(data: DeleteDocumentRequest):
    """Handler for removing a document."""
    try:
        collection_name = data.collection_name
        document_name = data.document_name
        for c in collection_name:
            await weaviate_db.remove_document(c, document_name)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        logger.error(f"Error in deleting document: {str(e)}", exc_info=True)
        raise Exception("Error in deleting document")


async def general_handler(request: GeneralRequest):
    """Handler for general RPC calls."""
    method = request.method
    data = request.data

    if method == "add_document":
        return await add_document_handler(data)
    elif method == "query":
        return await query_handler(data)
    elif method == "remove_document":
        return await remove_document_handler(data)
    else:
        raise ValueError(f"Invalid method: {method}")


async def main():
    """Main entry point to start the RPC server."""
    await setup_database()

    try:
        connection = await connect_robust(rabbitmq_url)
        channel = await connection.channel()
        rpc = await RPC.create(channel)

        # Register RPC handlers
        await rpc.register(all_queues["vectordb"], general_handler, auto_delete=True)

        logger.info("Vector Database is running and waiting for RPC calls...")

        # Keep the service running
        await asyncio.Future()

    except Exception as e:
        logger.error(f"Error in Vector Database: {str(e)}", exc_info=True)

    finally:
        await connection.close()
        await teardown_database()


if __name__ == "__main__":
    asyncio.run(main())
