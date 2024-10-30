from aiohttp import web
from llm.generate import generate_response
import config

app = web.Application()
app.router.add_post('/generate', generate_response)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=config.llm_api_port)
