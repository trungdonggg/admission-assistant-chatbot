from quart import Quart, request, Response
from llm.chat_template import ChatTemplate
from llm.generator import Generator
import config

app = Quart(__name__)
bot = Generator()

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

    try:
        response = await bot.ainvoke(prompt_components)

        return {"response": response}, 200

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.llm_api_port)
