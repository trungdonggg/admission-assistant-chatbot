from flask import Flask
from flask_restful import Api
from embed import Embedding
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

api.add_resource(Embedding, '/vectorize')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.embedding_api_port)
