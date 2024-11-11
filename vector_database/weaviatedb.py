from typing import List
import weaviate
import weaviate.classes as wvc
from weaviate.classes.data import DataObject
from weaviate.connect import ConnectionParams
from weaviate.collections import CollectionAsync
from weaviate.classes.query import Filter
import logging
import config


class WeaviateDB:
    def __init__(self):
        self.client = weaviate.WeaviateAsyncClient(
            connection_params=ConnectionParams.from_params(
                http_host="localhost",
                http_port=config.weaviate_service,
                http_secure=0,
                grpc_host="localhost",
                grpc_port=config.weaviate_grpc,
                grpc_secure=0,
            )
        )

    async def connect(self):
        await self.client.connect()
        logging.info("Connected to Weaviate")

    async def create_collection(self, collection_name: str):
        await self.client.collections.create(
            name=collection_name,
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
        )
        logging.info(f"Collection '{collection_name}' created")

    async def delete_collection(self, collection_name: str):
        await self.client.collections.delete(collection_name)
        logging.info(f"Collection '{collection_name}' deleted")

    def get_collection(self, collection_name: str) -> CollectionAsync:
        return self.client.collections.get(name=collection_name)

    async def add_document(self, collection_name: str, document_name: str, tag_name: str, chunks: List[str], vectors: List[List[float]]):
        collection = self.get_collection(collection_name)
        data_objects = [
            DataObject(
                properties={
                    "collection_name": collection_name,
                    "document_name": document_name,
                    "tag_name": tag_name,
                    "chunk": chunk,
                },
                vector=vector
            )
            for chunk, vector in zip(chunks, vectors)
        ]
        return (await collection.data.insert_many(objects=data_objects)).all_responses

    async def remove_document(self, collection_name: str, document_name: str):
        collection = self.get_collection(collection_name)
        response = await collection.data.delete_many(
            where=Filter.by_property("document_name").equal(val=document_name)
        )
        return response

    async def query(self, collection_name: str, vector: List[float], content: str, limit: int = 10):
        collection = self.get_collection(collection_name)
        response = await collection.query.hybrid(
            query=content,
            alpha=0.2,
            vector=vector,
            limit=limit,
            return_metadata=wvc.query.MetadataQuery(certainty=True)
        )
        print(response.objects)
        return response.objects
    
    async def close_connection(self):
        await self.client.close()
        logging.info("Disconnected from Weaviate")

# alpha=0 pure keywords search
