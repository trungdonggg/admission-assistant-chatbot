import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from aio_pika.patterns import RPC
from aio_pika import connect_robust
from dotenv import load_dotenv
from config import all_queues, rabbitmq_url, messenger_adapter_api_port
import asyncio
import uvicorn
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app"""
    global rpc
    try:
        # Startup
        connection = await connect_robust(rabbitmq_url) 
        channel = await connection.channel()
        rpc = await RPC.create(channel)
        logger.info("Resources initialized successfully.")
        yield
    finally:
        # Shutdown
        if rpc:
            await rpc.close()
            logger.info("RPC connection closed.")

app = FastAPI(lifespan=lifespan)

# class MessageRequest(BaseModel):
#     object: str
#     entry: list

# # Webhook verification (required by Messenger)
# @app.get("/webhook")
# async def verify_webhook(hub_mode: str, hub_verify_token: str, hub_challenge: str):
#     if hub_mode and hub_verify_token == VERIFY_TOKEN:
#         logger.info("Webhook Verified")
#         return {"challenge": int(hub_challenge)}
#     raise HTTPException(status_code=403, detail="Forbidden")

# # Handling messages
# @app.post("/webhook")
# async def handle_webhook(message_request: MessageRequest):
#     if message_request.object != "page":
#         raise HTTPException(status_code=404, detail="Not Found")

#     for entry in message_request.entry:
#         event = entry["messaging"][0]
#         sender_id = event["sender"]["id"]

#         if "message" in event and "text" in event["message"]:
#             user_message = event["message"]["text"]

#             # Respond to the user
#             await send_message(sender_id, user_message, rpc)

#     return {"status": "EVENT_RECEIVED"}

# # Function to send a message
# async def send_message(recipient_id: str, user_message: str, rpc: RPC):
#     url = f"https://graph.facebook.com/v16.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

#     reply_text = await rpc(
#         all_queues["processor"],
#         {
#             "user": recipient_id,
#             "query": user_message
#         }
#     )
#     payload = {
#         "recipient": {"id": recipient_id},
#         "message": {"text": reply_text}
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(url, json=payload)
#             return response
#         except httpx.HTTPStatusError as e:
#             logger.error(f"Error sending message: {e.response.text}")


class EmbedRequest(BaseModel):
    content: list[str]
@app.post("/test_embedder")
async def test_embedder(request: EmbedRequest):
    """Test endpoint to get embeddings for a list of strings"""
    try:
        print("request received")
        # Call embedder service through RPC
        embeddings = await rpc.call(
            all_queues["embedder"],
            kwargs={
                "request": request.content
            }
        )
        
        return {
            "status": "success",
            "content": request.content,
            "embeddings": embeddings
        }
    except Exception as e:
        logger.error(f"Error getting embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Runs the FastAPI app with Uvicorn."""
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=messenger_adapter_api_port, 
        reload=True
    )

if __name__ == "__main__":
    main()