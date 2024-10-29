from flask import Flask
from flask_restful import Api
from minio_storage import ChatHistory
from .. import config

# Initialize Flask app and API
app = Flask(__name__)
api = Api(app)

# Register the Chat History route
api.add_resource(ChatHistory, '/add-chat-history')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.storage_api_port)
