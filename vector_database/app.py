from flask import Flask
from flask_restful import Api
from weaviatedb import VectorDatabase
import config

app = Flask(__name__)
api = Api(app)

api.add_resource(VectorDatabase, '/retriver')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.vectordb_api_port)
