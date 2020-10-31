import asyncio
import websockets
from threading import Thread


async def get_messages(websocket: websockets.WebSocketClientProtocol):
    async for message in websocket:
        print(f'New message: {message}')


async def simple_client(input_queue: asyncio.Queue, client_id: str):
    uri = f'ws://localhost:8000/broad_chat/{client_id}'
    async with websockets.connect(uri) as websocket:
        asyncio.create_task(get_messages(websocket))
        my_message = await input_queue.get()
        while my_message != '_end':
            await websocket.send(my_message)
            my_message = await input_queue.get()


def run_async_client(input_queue: asyncio.Queue, loop: asyncio.BaseEventLoop, client_id: str):
    loop.run_until_complete(simple_client(input_queue, client_id))


def terminal_input():
    input_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    client_id = input('Name: ')
    input_thread = Thread(target=run_async_client, args=(input_queue, loop, client_id))
    input_thread.start()
    my_message = input('Write message (for exit _end): ')
    while my_message != '_end':
        asyncio.run_coroutine_threadsafe(input_queue.put(my_message), loop=loop)
        my_message = input('Write message (for exit _end): ')
    asyncio.run_coroutine_threadsafe(input_queue.put(my_message), loop=loop)
    input_thread.join()


if __name__ == '__main__':
    terminal_input()
