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
        limit = 5

        print(user, query)

        query_vector = await vectorize(VectorizeRequest(content=[query]))
        print(len(query_vector[0]))

        chat_history = await get_chat_history(user)
        print(chat_history)

        search_results = await query_vectordb(
            QueryVectorDatabase(
                content=query,
                vector=query_vector[0],
                limit=limit
            )
        )
        print(search_results)

        generated_response = await generate_by_llm(
            GenerateLLMRequest(
                input=query,
                context=str(search_results + chat_history)
            )
        )
        print (type(generated_response))
        print (generated_response)


        await add_chat_history(
            AddChatHistoryRequestDatabase(
                user=user,
                messages = [
                    f"role: human, content: {query}",
                    f"role: AI, content: {generated_response}"
                ]
            )
        )

        return generated_response
