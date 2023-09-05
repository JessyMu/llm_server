import asyncio
import json
import time
from typing import Optional

import multiprocessing as mp
import multiprocessing.connection
from concurrent.futures import ProcessPoolExecutor

import websockets

_print = print


def print(*args, **kwargs):
    _print(mp.current_process().pid, *args, **kwargs)


def child_function(parent_conn: multiprocessing.connection.Connection, text: str):
    CHILD_SEND_INTERVAL = 0.2
    # Inform the parent process to execute a function
    print("in child process")
    for character in text:
        parent_conn.send(character)
        print("child", character)
        time.sleep(CHILD_SEND_INTERVAL)
    parent_conn.send("")
    print("child EOF")


async def _handle_msg_mp_executor(websocket, json_client: dict):
    pool = ProcessPoolExecutor(max_workers=1)
    try:
        print("msg_json", json_client)
        loop = asyncio.get_event_loop()

        parent_conn, child_conn = multiprocessing.Pipe()

        content = json_client["data"]["content"]
        assert isinstance(content, list) and len(content) == 1
        (text,) = content

        # with pool:
        print("new process created!")

        loop.run_in_executor(pool, child_function, parent_conn, text)

        while True:
            # TODO: break on chyld stop???
            child_msg = await asyncio.get_event_loop().run_in_executor(
                None, child_conn.recv
            )
            if child_msg != "":
                print("child_msg", child_msg)

                json_server = {
                    "chatId": 1,
                    "questionId": 1,
                    "created": time.time(),
                    "code": 0,
                    "msg": "",
                    "index": 0,
                    "delta": {"content": child_msg},
                    "finish_reason": "",
                }
                msg_server = json.dumps(json_server)
                await websocket.send(msg_server)
            else:
                json_server = {
                    "chatId": 1,
                    "questionId": 1,
                    "created": time.time(),
                    "code": 0,
                    "msg": "",
                    "index": 0,
                    "delta": {"content": ""},
                    "finish_reason": "natural",
                }
                msg_server = json.dumps(json_server)
                await websocket.send(msg_server)
                break  # no data to proceed!
    except asyncio.CancelledError as ex:
        print("cancelling...", ex)
        for _, process in pool._processes.items():
            print(f"terminating process{process.pid}")
            process.kill()
        pool.shutdown(wait=False, cancel_futures=True)
        print("cancelled", ex)


async def _handle_msg_mp_only(websocket, json_client: dict):
    process = None
    try:
        print("msg_json", json_client)
        loop = asyncio.get_event_loop()

        parent_conn, child_conn = multiprocessing.Pipe()

        content = json_client["data"]["content"]
        assert isinstance(content, list) and len(content) == 1
        (text,) = content

        # with pool:
        print("new process created!")

        process = mp.Process(target=child_function, args=(child_conn, text))
        process.start()

        print("parent after start")
        while True:
            print("parent iter")
            # TODO: break on chyld stop???
            child_msg = await asyncio.get_event_loop().run_in_executor(
                None, child_conn.recv
            )
            if child_msg != "":
                print("child_msg", child_msg)

                json_server = {
                    "chatId": 1,
                    "questionId": 1,
                    "created": time.time(),
                    "code": 0,
                    "msg": "",
                    "index": 0,
                    "delta": {"content": child_msg},
                    "finish_reason": "",
                }
                msg_server = json.dumps(json_server)
                await websocket.send(msg_server)
            else:
                json_server = {
                    "chatId": 1,
                    "questionId": 1,
                    "created": time.time(),
                    "code": 0,
                    "msg": "",
                    "index": 0,
                    "delta": {"content": ""},
                    "finish_reason": "natural",
                }
                msg_server = json.dumps(json_server)
                await websocket.send(msg_server)
                break  # no data to proceed!

        process.join()
    except asyncio.CancelledError as ex:
        print("cancelling...", ex)
        if process is not None:
            print(f"terminating process{process.pid}")
            process.terminate()
        print("cancelled", ex)


async def _handle(websocket):
    tasks = list()
    loop = asyncio.get_event_loop()

    # FIXME: watch out!
    _handle_msg = _handle_msg_mp_executor

    async for msg in websocket:
        msg_json = json.loads(msg)  # FIXME: check json format???
        if msg_json["data"]["action"] == "stop":
            for task in tasks:
                task.cancel()

            json_server = {
                "chatId": 1,
                "questionId": 1,
                "created": time.time(),
                "code": 0,
                "msg": "",
                "index": 0,
                "delta": {"content": ""},
                "finish_reason": "provided",
            }
            msg_server = json.dumps(json_server)
            await websocket.send(msg_server)
        else:
            task = loop.create_task(coro=_handle_msg(websocket, msg_json))
            tasks.append(task)


async def _main():
    async with websockets.serve(_handle, "localhost", 10001):
        print("ready to serve!")
        await asyncio.Future()


if __name__ == "__main__":
    # Create a pipe for communication between parent and child processes
    asyncio.run(_main())
