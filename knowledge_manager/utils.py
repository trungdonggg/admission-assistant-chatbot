from config import all_queues
import httpx
from typing import List, Dict
from aio_pika.patterns import RPC
from knowledge_manager.models import *
import logging

logger = logging.getLogger(__name__)

async def split_document(content: str, rpc: RPC) -> List[str]:
    """Split document content into chunks using text splitter service."""
    try:
        logger.info("Sending text to splitter service")
        response = await rpc.call(
            all_queues["textsplitter"],
            kwargs={"request": content}
        )
        
        chunks = response.get("chunks")
        logger.info(f"Successfully split text into {len(chunks)} chunks")
        return chunks

    except httpx.HTTPError as e:
        logger.error(f"HTTP error in split_document: {str(e)}", exc_info=True)
        raise Exception(f"Text splitter service error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in split_document: {str(e)}", exc_info=True)
        raise Exception(f"Failed to split document: {str(e)}")

async def vectorize(chunks: List[str], rpc: RPC) -> List[List[float]]:
    """Generate vectors for text chunks using embedder service."""
    try:
        logger.info(f"Sending {len(chunks)} chunks to embedder")
        response = await rpc.call(
            all_queues["embedder"],
            kwargs={"request": chunks}
        ) 
        
        vectors = response.get("vectors")
        if not vectors:
            raise Exception("No vectors returned from embedder service")
            
        logger.info(f"Successfully generated {len(vectors)} vectors")
        return vectors

    except Exception as e:
        logger.error(f"Error in vectorize: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate vectors: {str(e)}")

async def add_document_to_vectordb(request: AddDocumentToVectorDatabaseRequest, rpc: RPC) -> Dict:
    """Add document chunks and vectors to vector database."""
    try:
        logger.info(f"Adding document '{request.document_name}' to vector database")
        response = await rpc.call(
            all_queues["vectordb"],
            kwargs={
                "request": {
                    "method": "add_document",
                    "data": request.model_dump()
                }
            }
        )
        
        logger.info(f"Successfully added document to vector database")
        return response

    except Exception as e:
        logger.error(f"Error in add_document_to_vectordb: {str(e)}", exc_info=True)
        raise Exception(f"Failed to add document to vector database: {str(e)}")

async def remove_document_from_vectordb(request: RemoveDocumentFromVectorDatabaseRequest, rpc: RPC) -> Dict:
    """Remove document from vector database."""
    try:
        logger.info(f"Removing document '{request.document_name}' from vector database")
        response = await rpc.call(
            all_queues["vectordb"],
            kwargs={
                "request": {
                    "method": "remove_document",
                    "data": request.model_dump()
                }
            }
        )
        
        logger.info(f"Successfully removed document from vector database")
        return response

    except Exception as e:
        logger.error(f"Error in remove_document_from_vectordb: {str(e)}", exc_info=True)
        raise Exception(f"Failed to remove document from vector database: {str(e)}")