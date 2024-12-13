from flask import Flask
from flask_restful import Api
from mongo import ChatHistory, Documents
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)


api.add_resource(Documents, "/db/documents")
api.add_resource(ChatHistory, "/db/history")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=config.database_api_port)