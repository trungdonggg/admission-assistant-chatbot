from quart import request, jsonify, Response
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the ChatGoogleGenerativeAI model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                             google_api_key=os.getenv("GOOGLE_AI_API_KEY"))

# Define the prompt
prompt = "Dùng dữ liệu tôi đưa để trả lời câu hỏi. Trả lời bằng Tiếng Việt."

async def generate_stream(inputs):
    async for chunk in llm.agenerate(inputs):
        yield chunk

# Route Handler
async def generate_response():
    # Get the data from the request JSON
    data = await request.get_json()
    context = data.get('context')

    if not context:
        return {"error": "No input provided"}, 400

    try:
        # Combine the prompt and user input
        full_prompt = prompt + "\n\n" + context

        # Stream the response asynchronously
        return Response(generate_stream(full_prompt), content_type='text/plain')

    except Exception as e:
        return {"error": str(e)}, 500
