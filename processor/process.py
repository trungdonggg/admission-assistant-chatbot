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
        
        # Split the document content into chunks
        text_chunks = await split_document(content=document_content)
        print("text chunked: ")
        print(text_chunks)

        # Add document name and tag name to the database
        await add_document_name_and_tagname_to_db(
            AddDocumentRequestDatabase(
                document_name=document_name,
                tag_name=tag_name
            )
        )
        print("document added to db")

        # Vectorize the text chunks
        vectors = await vectorize(
            VectorizeRequest(
                content=text_chunks
            )
        )
        print("vectors: ")
        print(len(vectors))
        
        # Add the document with chunks and vectors to the vector database
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
        # Remove the document from the database and vector database
        await remove_document_from_db(document_name)
        await remove_document_from_vectordb(document_name)

    async def search(self, user: str, query: str, vector: List[float], limit: int = 10):
        # Vectorize the query and retrieve chat history
        query_vector = await vectorize(VectorizeRequest(content=[query]))
        chat_history = await get_chat_history(user)

        # Query the vector database using query vector and chat history
        search_results = await query_vectordb(
            QueryRequestVectorDatabase(
                content=query + ' ' + chat_history,
                vector=query_vector[0],  # Assuming vectorize returns a list of vectors
                limit=limit
            )
        )

        # Generate a response based on search results and add it to chat history
        generated_response = await generate_by_llm(
            GenerateLLMRequest(
                input=query,
                context=search_results
            )
        )

        # Save the generated response to chat history
        await add_chat_history(
            AddChatHistoryRequestDatabase(
                user=user,
                message=[query, generated_response]
            )
        )

        return generated_response
