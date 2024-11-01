from flask_restful import Resource
import weaviate
import weaviate.classes as wvc
from weaviate.classes.data import DataObject
from weaviate.collections import CollectionAsync
from weaviate.classes.query import Filter
from weaviate.collections.classes.internal import Object
from typing import List
import logging
import config
from flask import request



class Weaviate():
    def __init__(self) -> None:
        super().__init__()
        self.client = weaviate.WeaviateAsyncClient(
            http_host='localhost',
            http_port=str(config.weaviate_service),
            http_secure=0,
            grpc_host='localhost',
            grpc_port=str(config.weaviate_grpc),
            grpc_secure=0,
        )
        
    async def connect(self) -> None:
        await self.client.connect()
        logging.info("Connected to vector database")

    async def create_collection(self, weaviate_collection_name: str) -> None:
        
        await self.client.collections.create(
            name=weaviate_collection_name,
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
        )
        logging.info(f"Successfully created collection for organization [{weaviate_collection_name}]")

    async def delete_collection(self, weaviate_collection_name: str) -> None:
        
        await self.client.collections.delete(weaviate_collection_name)
        logging.info(f"Successfully deleted collection of organization [{weaviate_collection_name}]")

    def _get_collection(self, weaviate_collection_name: str) -> CollectionAsync:
        logging.info(f"Getting collection for organization [{weaviate_collection_name}]")
        return self.client.collections.get(name=weaviate_collection_name)

    async def add_document(self,
                         weaviate_collection_name: str,
                         document_name: str,
                         tag_name: str,
                         chunks: List[str],
                         represent_vectors: List[List[float]]
                         ):

        data_objects: List[DataObject] = []
        for vector, chunk in zip(represent_vectors, chunks):
            data_objects.append(DataObject(
                properties={
                    weaviate_collection_name:weaviate_collection_name,
                    document_name:document_name,
                    tag_name: tag_name,
                    chunk:chunk,
                },
                vector=vector
            ))
        collection: CollectionAsync = self._get_collection(weaviate_collection_name=weaviate_collection_name)
        logging.info("Adding chunks to vector database")

        return (await collection.data.insert_many(objects=data_objects)).all_responses

    async def remove_document(self, weaviate_collection_name: str, document_name: str) -> None:
        
        collection: CollectionAsync = self._get_collection(weaviate_collection_name=weaviate_collection_name)

        response = await collection.data.delete_many(
            where=Filter.by_property("document_name").equal(val=document_name)
        )
        logging.info(f"failed={response.failed}, matches={response.matches}, successful={response.successful}")

    async def close_connection(self) -> None:

        await self.client.close()
        logging.info("Successfully closed connection to vector database")

    async def query(self,
                    weaviate_collection_name: str,
                    vector: List[float],
                    content: str,
                    limit: int = 10
                    ) -> List[Object]:

        collection: CollectionAsync = self._get_collection(weaviate_collection_name=weaviate_collection_name)
        response = await collection.query.hybrid(
            query=content,
            alpha=0.5,
            vector=vector,
            limit=limit,
            return_metadata=wvc.query.MetadataQuery(certainty=True)
        )
        logging.info(f"Query found [{len(response.objects)}] result(s)")

        return response.objects






class VectorDatabase(Resource):

    def __init__(self) -> None:
        super().__init__()
        self.colection_name=config.weaviate_collection_name
        self.weaviate = Weaviate()
        self.weaviate.connect()
        self.weaviate.create_collection(weaviate_collection_name=self.colection_name)

    async def get(self):
        
        # query

        vector="?"
        content="?"
        
        return await self.weaviate.query(weaviate_collection_name=self.colection_name, vector=vector, content=content)
    
    async def post(self):
        data = request.json
        document_name = data.get("document_name")
        tagname = data.get("tagname")
        chunks = data.get("chunks")
        represent_vectors=data.get("represent_vectors")

        return await self.weaviate.add_document(
            weaviate_collection_name=self.colection_name,
            document_name=document_name,
            tag_name=tagname,
            chunks=chunks,
            represent_vectors=represent_vectors
            )
    
    async def delete(self):
        pass

    
