import json
from functools import lru_cache

from fastapi import FastAPI, WebSocket, Depends
from fastapi.concurrency import run_until_first_complete

from redis_vsc.redis_vsc import RedisVSC
from config import config


app = FastAPI()
broadcast_channel = 'anonymity'


@lru_cache()
def get_settings() -> config.Settings:
    return config.Settings()


async def chat_receiver(websocket: WebSocket, redis_client: RedisVSC):
    async for message in websocket.iter_json():
        if isinstance(message, dict):
            await redis_client.publish(channel=message.get('channel', broadcast_channel),
                                       message=json.dumps({'from': redis_client.client_id,
                                                           'message': message['message']}))


async def chat_sender(websocket: WebSocket, redis_client: RedisVSC):
    await redis_client.subscribe(channel=redis_client.client_id)
    async for dict_message in redis_client:
        await websocket.send_json(dict_message)


@app.websocket('/secure_chat/{client_id}')
async def chat_room(websocket: WebSocket, client_id: str, settings: config.Settings = Depends(get_settings)):
    await websocket.accept()
    redis_client = RedisVSC(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_PASSWORD,
                            settings.REDIS_DB_NUMBER, client_id)
    await redis_client.connect()
    await redis_client.publish(broadcast_channel, f'Client #{client_id} joined')
    await run_until_first_complete(
        (chat_receiver, {'websocket': websocket, 'redis_client': redis_client}),
        (chat_sender, {'websocket': websocket, 'redis_client': redis_client})
    )
    await redis_client.publish(broadcast_channel, f'Client #{client_id} left the chat')
    redis_client.disconnect()
