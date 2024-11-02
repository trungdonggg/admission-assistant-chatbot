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
        print(text_chunks)

        
        # await add_document_name_and_tagname_to_db(
        #     models.AddDocumentRequestDatabase(
        #         document_name=document_name,
        #         tag_name=tag_name
        #     )
        # )
        # await vectorize(
        #     models.VectorizeRequest(
        #         content=text_chunks
        #     )
        # )
        # await add_document_to_vectordb()


    # async def delete_document(self):
    #     await remove_document_from_db()
    #     await remove_document_from_vectordb()
    

    # async def search(self):
    #     await vectorize()
    #     await get_chat_history()
    #     await query_vectordb()
    #     await generate_by_llm()
    #     await add_chat_history()
    
    
