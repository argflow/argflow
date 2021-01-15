import asyncio
import watchgod

from starlette.websockets import WebSocket
from typing import List


class FileWatcher:
    watchers: List[WebSocket]

    def __init__(self, path: str, on_event):
        self.path = path
        self.on_event = on_event

    async def __watch(self):
        async for changes in watchgod.awatch(self.path):
            await self.on_event(changes)

    def start(self):
        asyncio.create_task(self.__watch())
