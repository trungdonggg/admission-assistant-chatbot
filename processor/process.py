class Processor:
    def __init__(self):
        pass

    def add_document(self):
        add_document_name_and_tagname_to_db()
        vectorize()
        add_to_vectordb()


    def delete_document(self):
        remove_document_name_from_db()
        remove_from_vectordb()
    

    def search(self):
        vectorize()
        get_chat_history()
        query_vectordb()
        generate_by_llm()
        add_chat_history()
    
    
