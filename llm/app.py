from quart import Quart
from llm.generate import generate_response
from .. import config

# Initialize the Quart app
app = Quart(__name__)

# Define the route for text generation
app.add_url_rule('/generate-text', view_func=generate_response, methods=['POST'])

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.llm_api_port)
