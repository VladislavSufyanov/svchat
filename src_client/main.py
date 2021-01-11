import json
import os
import asyncio
import websockets
from threading import Thread


def read_conf(conf_path_: str):
    with open(conf_path_) as conf_file:
        return json.load(conf_file)


async def get_messages(websocket: websockets.WebSocketClientProtocol):
    async for message in websocket:
        try:
            dict_message = json.loads(message)
        except (TypeError, ValueError):
            pass
        else:
            print(f'\nNew message from {dict_message["message"].get("from", "Anonymous")}: '
                  f'{dict_message["message"]["message"]}')


async def simple_client(input_queue: asyncio.Queue, client_id: str,
                        server_host: str, server_port: int):
    uri = f'ws://{server_host}:{server_port}/secure_chat/{client_id}'
    async with websockets.connect(uri) as websocket:
        asyncio.create_task(get_messages(websocket))
        my_message = await input_queue.get()
        while my_message != '_end':
            await websocket.send(my_message)
            my_message = await input_queue.get()


def run_async_client(input_queue: asyncio.Queue, loop: asyncio.BaseEventLoop, client_id: str,
                     server_host: str, server_port: int):
    loop.run_until_complete(simple_client(input_queue, client_id, server_host, server_port))


def input_message_and_channel() -> str:
    channel = input('Send message to (for exit _end): ')
    if channel == '_end':
        return '_end'
    message = input('Write message (for exit _end): ')
    if message == '_end':
        return '_end'
    return json.dumps({'channel': channel, 'message': message})


def terminal_input(settings_: dict):
    input_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    client_id = input('Username: ')
    input_thread = Thread(target=run_async_client, args=(input_queue, loop, client_id,
                                                         settings_['server_host'],
                                                         settings_['server_port']))
    input_thread.start()
    my_message = input_message_and_channel()
    while my_message != '_end':
        asyncio.run_coroutine_threadsafe(input_queue.put(my_message), loop=loop)
        my_message = input_message_and_channel()
    asyncio.run_coroutine_threadsafe(input_queue.put(my_message), loop=loop)
    input_thread.join()


if __name__ == '__main__':
    conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'settings.json')
    settings = read_conf(conf_path)
    terminal_input(settings)
