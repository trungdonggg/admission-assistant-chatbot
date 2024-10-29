from flask import Flask
from flask_restful import Api
from mongo import MongoDB
from .. import config


app = Flask(__name__)
api = Api(app)


api.add_resource(MongoDB, "/db")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=config.database_api_port)