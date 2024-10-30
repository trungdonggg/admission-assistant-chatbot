
from aiohttp import web
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_AI_API_KEY")
)

prompt = "Dùng dữ liệu tôi đưa để trả lời câu hỏi. Trả lời bằng Tiếng Việt."

async def generate_stream(inputs):
    async for chunk in llm.agenerate(inputs):
        yield chunk

async def generate_response(request):
    data = await request.json()
    context = data.get('context')

    if not context:
        return web.json_response({"error": "No input provided"}, status=400)

    try:
        full_prompt = prompt + "\n\n" + context

        async def stream():
            async for chunk in generate_stream(full_prompt):
                yield chunk

        return web.Response(body=stream(), content_type='text/plain')

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


