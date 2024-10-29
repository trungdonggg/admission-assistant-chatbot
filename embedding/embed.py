from flask import request, jsonify
from flask_restful import Resource
from langchain_huggingface import HuggingFaceEmbeddings

modelname = "dangvantuan/vietnamese-embedding"

class Embedding(Resource):

    def __init__(self):
        self.embed_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

    def post(self):
        data = request.json
        content = data.get('content')

        if not content:
            return {"error": "No content provided"}, 400

        vector = self.embed_model.embed_query(content)

        return {"vector": vector}, 200

