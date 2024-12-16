from langchain_huggingface import HuggingFaceEmbeddings

modelname = "dangvantuan/vietnamese-embedding"

class Embedding:

    def __init__(self):
        self.embed_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

    def embed(self, content):
        if not content or not isinstance(content, list):
            return {"error": "Content must be a list of strings"}, 400

        try:
            vectors = [self.embed_model.embed_query(text) for text in content]
            return {"vectors": vectors}, 200
        except Exception as e:
            return {"error": str(e)}, 500
