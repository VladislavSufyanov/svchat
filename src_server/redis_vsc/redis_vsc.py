import typing

import asyncio_redis


class RedisVSC:

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._pub_conn = None
        self._sub_conn = None
        self._subscriber = None

    async def __anext__(self):
        if self._subscriber is None:
            raise StopIteration
        message = await self.get_message()
        return message

    def __aiter__(self):
        return self

    async def connect(self) -> None:
        self._pub_conn = await asyncio_redis.Connection.create(self._host, self._port)
        self._sub_conn = await asyncio_redis.Connection.create(self._host, self._port)
        self._subscriber = await self._sub_conn.start_subscribe()

    def disconnect(self) -> None:
        self._pub_conn.close()
        self._sub_conn.close()

    async def subscribe(self, channel: str) -> None:
        await self._subscriber.subscribe([channel])

    async def unsubscribe(self, channel: str) -> None:
        await self._subscriber.unsubscribe([channel])

    async def publish(self, channel: str, message: str) -> None:
        await self._pub_conn.publish(channel, message)

    async def get_message(self) -> typing.Dict[str, str]:
        message = await self._subscriber.next_published()
        return {'channel': message.channel, 'message': message.value}
