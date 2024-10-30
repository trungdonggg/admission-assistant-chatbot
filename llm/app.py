from quart import Quart, request, Response
from llm.chat_template import ChatTemplate
from llm.generator import Generator
import config

app = Quart(__name__)


@app.route('/generate', methods=['POST'])
async def generate_response():
    data = await request.get_json()
    query = data.get('query')
    history = data.get('history')
    context = data.get('context')

    if not query:
        return {"error": "No query provided"}, 400

    prompt_components = ChatTemplate(
        history=history,
        context=context,
        input=query
    )

    async def generate_stream():
        bot = Generator()
        async for chunk in bot.astream(prompt_components):
            yield chunk

    return Response(generate_stream(), content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.llm_api_port)
