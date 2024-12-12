from processor.utils import *
from processor.models import *


class Processor:
    def __init__(self):
        pass

    async def add_document(self, request: AddDocument):
        user = request.user
        document_name = request.document_name
        tag_name = request.tag_name
        document_content = request.document_content
        
        text_chunks = await split_document(content=document_content)
        print("text chunked")

        await add_document_name_and_tagname_to_db(
            AddDocumentRequestDatabase(
                document_name=document_name,
                tag_name=tag_name
            )
        )
        print("document added to db")

        vectors = await vectorize(
            VectorizeRequest(
                content=text_chunks
            )
        )
        print("vectors generated")
        
        await add_document_to_vectordb(
            CreateDocumentRequestVectorDatabase(
                document_name=document_name,
                tag_name=tag_name,
                chunks=text_chunks,
                vectors=vectors
            )
        )
        print("document added to vectordb")


    async def delete_document(self, document_name: str):
        await remove_document_from_db(document_name)
        print("document removed from db")
        await remove_document_from_vectordb(document_name)
        print("document removed from vectordb")

    async def search(self, request: SearchRequest):
        user = request.user
        query = request.query
        limit = 10

        print("user:", user)
        print("query:", query)

        query_vector = await vectorize(VectorizeRequest(content=[query]))
        print("vector size:")
        print(len(query_vector[0]))

        chat_history = await get_chat_history(user)
        print("chat history:")
        print(chat_history)

        search_results = await query_vectordb(
            QueryVectorDatabase(
                content=query + str(chat_history[-10:]),
                vector=query_vector[0],
                limit=limit
            )
        )

        similar_text = []
        for result in search_results[0]["query_results"]:
            similar_text.append(result["properties"]["chunk"])
        print("query results:")
        print(similar_text)

        generated_response = await generate_by_llm(
            GenerateLLMRequest(
                input=query,
                context=similar_text,
                history=chat_history[-10:]
            )
        )
        print (type(generated_response))
        print("generated response:")
        print (generated_response)


        await add_chat_history(
            AddChatHistoryRequestDatabase(
                user=user,
                messages = [
                    {"role": "human", "content": query},
                    {"role": "AI", "content": generated_response}
                ]
            )
        )

        return generated_response

async def search_tagname(self, request: SearchRequest):
        user = request.user
        query = request.query
        limit = 5

        print("user:", user)
        print("query:", query)

        query_vector = await vectorize(VectorizeRequest(content=[query]))
        print("vector size:")
        print(len(query_vector[0]))

        chat_history = await get_chat_history(user)
        print("chat history:")
        print(chat_history)

        tagnames = await tagnames_cls(
            TagnameClassifier(
                history=chat_history[-10:],
                input=query
            )
        )
        print("tagnames:")
        print(tagnames)

        search_results = await query_vectordb_tagnames(
            QueryVectorDatabaseTagname(
                content=query,
                vector=query_vector[0],
                limit=limit,
                tagname=list(tagnames)
            )
        )

        similar_text = []
        for result in search_results[0]["query_results"]:
            similar_text.append(result["properties"]["chunk"])
        print("query results:")
        print(similar_text)

        generated_response = await generate_by_llm(
            GenerateLLMRequest(
                input=query,
                context=similar_text,
                history=chat_history[-10:]
            )
        )
        print (type(generated_response))
        print("generated response:")
        print (generated_response)


        await add_chat_history(
            AddChatHistoryRequestDatabase(
                user=user,
                messages = [
                    {"role": "human", "content": query},
                    {"role": "AI", "content": generated_response}
                ]
            )
        )

        return generated_response