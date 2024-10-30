from flask import Flask
from flask_restful import Api
import config
from llm.generator import GenerateResponse

app = Flask(__name__)
api = Api(app)

api.add_resource(GenerateResponse, '/generate')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.llm_api_port)
