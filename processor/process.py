from processor.utils import *
from processor.models import *


class Processor:
    def __init__(self):
        pass


    async def search(self, request: SearchRequest):
        user = request.user
        query = request.query
        limit = 7

        print("user:", user)
        print("query:", query)


        chat_history = await get_chat_history(user)
        print("chat history:")
        print(chat_history)
        

        query_vector = await vectorize(VectorizeRequest(content=[query]))
        print("vector size:")
        print(len(query_vector[0]))
        
        
        search_results = await query_vectordb(
            QueryVectorDatabase(
                content=query,
                vector=query_vector[0],
                limit=limit,
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