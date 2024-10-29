from flask import Flask
from flask_restful import Api
from embed import Embedding
from .. import config

# Initialize the Flask app and API
app = Flask(__name__)
api = Api(app)

# Add the resource to the API
api.add_resource(Embedding, '/get-vector')

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.embedding_api_port)
