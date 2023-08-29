import websockets
import asyncio


class BaseHandler:
    def __init__(self, addr, port) -> None:
        self.addr = addr
        self.port = port

    async def _handle():
        pass

    async def arun(self):
        async with websockets.serve(
            self._handle, self.addr, self.port, max_size=100000000
        ):
            await asyncio.Future()


class SequentialHandler(BaseHandler):
    def __init__(self, addr, port) -> None:
        super().__init__(addr, port)

    async def _handle():
        pass
