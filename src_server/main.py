from fastapi import FastAPI, WebSocket, websockets
from fastapi.concurrency import run_until_first_complete

from redis_vsc.redis_vsc import RedisVSC


app = FastAPI()
broadcast_channel = 'anonymity'


async def chat_receiver(websocket: WebSocket, redis_client: RedisVSC):
    async for message in websocket.iter_text():
        await redis_client.publish(channel=broadcast_channel, message=message)


async def chat_sender(websocket: WebSocket, redis_client: RedisVSC):
    await redis_client.subscribe(channel=broadcast_channel)
    async for dict_message in redis_client:
        await websocket.send_text(dict_message['message'])


@app.websocket('/broad_chat/{client_id}')
async def chat_room(websocket: WebSocket, client_id: str):
    await websocket.accept()
    redis_client = RedisVSC('localhost', 6379)
    await redis_client.connect()
    await run_until_first_complete(
        (chat_receiver, {'websocket': websocket, 'redis_client': redis_client}),
        (chat_sender, {'websocket': websocket, 'redis_client': redis_client})
    )
    await redis_client.publish(broadcast_channel, f'Client #{client_id} left the chat')
    redis_client.disconnect()
