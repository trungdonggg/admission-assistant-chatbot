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

        try:
            await add_document_to_db(
                AddDocumentRequestDatabase(
                    document_name=document_name,
                    tag_name=tag_name,
                    content=document_content,
                )
            )
            print("document added to db")

            text_chunks = await split_document(content=document_content)
            print("text chunked")
            
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
            
        except Exception as e:
            await self.delete_document(document_name)
            raise Exception(f"Error in adding document: {str(e)}")


    async def delete_document(self, document_name: str):
        await remove_document_from_db(document_name)
        print("document removed from db")
        await remove_document_from_vectordb(document_name)
        print("document removed from vectordb")


    async def search(self, request: SearchRequest):
        user = request.user
        query = request.query
        limit = 5

        print("user:", user)
        print("query:", query)


        chat_history = await get_chat_history(user)
        print("chat history:")
        print(chat_history)
        
        
        tagnames = await tagnames_cls(
            TagnameClassifier(
                history=chat_history[-6:],
                input=query
            )
        )
        print("tagnames:")
        print(tagnames)


        query_vector = await vectorize(VectorizeRequest(content=[query]))
        print("vector size:")
        print(len(query_vector[0]))
        
        
        search_results = await query_vectordb_tagnames(
            QueryVectorDatabaseTagname(
                content=query,
                vector=query_vector[0],
                limit=limit,
                tagname=tagnames
            )
        )
        print("search results:")
        print(search_results)
        

        similar_text = []
        for result in search_results[0]["query_results"]:
            similar_text.append(result["properties"]["chunk"])
        print("query results:")
        print(similar_text)


        generated_response = await generate_by_llm(
            GenerateLLMRequest(
                input=query,
                context=str(similar_text),
                history=chat_history[-6:]
            )
        )
        print("generated response:")
        print (generated_response)


        await add_chat_history(
            AddChatHistoryRequestDatabase(
                user=user,
                messages = [
                    {"role": "human", "content": query},
                    {"role": "ai", "content": generated_response}
                ]
            )
        )

        return generated_response