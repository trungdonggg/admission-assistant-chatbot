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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN")

app = FastAPI()

rpc: RPC

class MessageRequest(BaseModel):
    object: str
    entry: list

# Webhook verification (required by Messenger)
@app.get("/webhook")
async def verify_webhook(hub_mode: str, hub_verify_token: str, hub_challenge: str):
    if hub_mode and hub_verify_token == VERIFY_TOKEN:
        logger.info("Webhook Verified")
        return {"challenge": int(hub_challenge)}
    raise HTTPException(status_code=403, detail="Forbidden")

# Handling messages
@app.post("/webhook")
async def handle_webhook(message_request: MessageRequest):
    if message_request.object != "page":
        raise HTTPException(status_code=404, detail="Not Found")

    for entry in message_request.entry:
        event = entry["messaging"][0]
        sender_id = event["sender"]["id"]

        if "message" in event and "text" in event["message"]:
            user_message = event["message"]["text"]

            # Respond to the user
            await send_message(sender_id, user_message, rpc)

    return {"status": "EVENT_RECEIVED"}

# Function to send a message
async def send_message(recipient_id: str, user_message: str, rpc: RPC):
    url = f"https://graph.facebook.com/v16.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    reply_text = await rpc(
        all_queues["processor"],
        {
            "user": recipient_id,
            "query": user_message
        }
    )
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": reply_text}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"Error sending message: {e.response.text}")

async def initialize_resources():
    """Initialize global resources."""
    global rpc
    try:
        connection = await connect_robust(rabbitmq_url) 
        channel = await connection.channel()
        rpc = await RPC.create(channel)
        logger.info("Resources initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing resources: {str(e)}", exc_info=True)
        raise Exception("Failed to initialize resources")
    
async def cleanup_resources():
    """Clean up global resources."""
    try:
        if rpc:
            await rpc.close()
            logger.info("RPC connection closed.")
    except Exception as e:
        logger.error(f"Error cleaning up resources: {str(e)}", exc_info=True)
        raise Exception("Failed to clean up resources")

def main():
    """Runs the FastAPI app with Uvicorn."""
    try:
        asyncio.run(initialize_resources())
        uvicorn.run("app:app", host="0.0.0.0", port=messenger_adapter_api_port, reload=True)
    finally:
        asyncio.run(cleanup_resources())

if __name__ == "__main__":
    main()