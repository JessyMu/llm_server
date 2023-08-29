from typing import Union, Optional
from abc import ABC, abstractmethod

import logging

import asyncio
import concurrent.futures

import websockets
import multiprocessing as mp
logger = logging.getLogger(__name__)

WsData = Union[bytes, str]


class BaseHandler(ABC):
    def __init__(self, addr: str, port: int) -> None:
        self._addr = addr
        self._port = port

    @property
    def addr(self) -> str:
        return self._addr

    @property
    def port(self) -> int:
        return self._port

    @staticmethod
    @abstractmethod
    def _process_data(data_client: WsData) -> WsData:
        pass

    async def _handle(self, websocket):
        data_client = await websocket.recv()
        data_server = self._process_data(data_client)
        await websocket.send(data_server)

    async def arun(self):
        # TODO: shutdown gracefully
        # logger.info(f"addr:{self._addr}")
        async with websockets.serve(
            self._handle, self._addr, self._port, max_size=100000000
        ):
            await asyncio.Future()


class SequentialHandler(BaseHandler):
    def __init__(
        self,
        addr: str,
        port: int,
        executor: Optional[concurrent.futures.Executor] = None,
    ) -> None:
        super().__init__(addr, port)

        self._lock_event = asyncio.Lock()
        self._event_last = asyncio.Event()
        self._event_last.set()

        self._executor = executor

    @property
    def executor(self) -> Optional[concurrent.futures.Executor]:
        return self._executor

    async def _handle(self, websocket):
        """
        * coroutine invocations form a "linked list"
        * each invocation acquires an event from previous invocation, and assign its
        own event to class attribute `_event_last`.
        * each invocation set (or releases) its own event on finish
        * `_process_data` wouldn't start until `_event_prev` was set
        """

        taskname = asyncio.current_task().get_name()
        async with self._lock_event:
            event_prev = self._event_last
            event_curr = asyncio.Event()
            self._event_last = event_curr
            # logger.debug(
            #     'task init: taskname="%s", prev=%s, curr=%s',
            #     taskname,
            #     event_prev,
            #     event_curr,
            # )

        try:
            async for message in websocket:
                print('receive message',mp.current_process().pid)
                client_data = message
                # client_data = await websocket.recv()

                # wait until previous request is finished (server_data sent to client)
                await event_prev.wait()
                # logger.debug(
                #     'task run: taskname="%s", prev=%s, curr=%s',
                #     taskname,
                #     event_prev,
                #     event_curr,
                # )
                loop = asyncio.get_running_loop()
                server_data = await loop.run_in_executor(
                    self._executor, self._process_data, client_data
                )
                if server_data:
                    await websocket.send(server_data)

            # run potentially blocking code in executor, preventing it from
            # blocking other client websockets
            """
            REMARK:
            Putting `process_data` under `await` won't break the FIFO property.
            Any other coroutines (except for event locking and data receiving)
            won't be scheduled before this `run_in_executor`, since they are
            waiting in a linked-list behind this `event_curr`.
            """
            # loop = asyncio.get_running_loop()
            # server_data = await loop.run_in_executor(
            #     self._executor, self._process_data, client_data
            # )

            # await websocket.send(server_data)
        except BaseException as ex:
            logger.exception("Exception encountered")
        finally:
            # use try-finally to ensure current event would be released
            # even if exception was encountered
            event_curr.set()

            # logger.debug(
            #     'task finish: taskname="%s", prev=%s, curr=%s',
            #     taskname,
            #     event_prev,
            #     event_curr,
            # )
