import json
import multiprocessing as mp
import time
import asyncio
import websockets
from concurrent.futures import ProcessPoolExecutor


async def _handle_msg(websocket, tag):
    try:
        # print("1")
        pool = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context())
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(pool, process_wrapper, tag)
    except asyncio.CancelledError as ex:
        print("cancel received")
        for _, process in pool._processes.items():
            print(f"terminating process{process.pid}")
            process.terminate()
        pool.shutdown(wait=False, cancel_futures=True)
        print("cancel finished")


def process_wrapper(tag):
    async def process_data(tag):
        SEND_INTERVAL = 0.5
        index = 0
        while True:
            question = {
                "chatId": 1,
                "questionId": 1,
                "created": time.time(),
                "code": 0,
                "msg": "",
                "index": index,
                "delta": {
                    "content": "hello",
                },
                "tag": tag,
                "finish_reason": "",
            }
            msg = json.dumps(question)
            print("process pid :", mp.current_process().pid)
            await web.send(msg)
            index += 1
            await asyncio.sleep(SEND_INTERVAL)

    asyncio.run(process_data(tag))


async def _handle(websocket):
    global web
    web = websocket
    loop = asyncio.get_event_loop()
    time0 = time.time()
    task = None
    SLEEP_INTERVAL = 0.5  # wait some time to let task be dispatched
    print("handle pid :", mp.current_process().pid)
    async for message in websocket:
        # print(f"start loop {message}")
        if json.loads(message)["data"]["action"] == "stop":
            task.cancel("task0")
            stop = {
                "chatId": 1,
                "questionId": 1,
                "created": time.time(),
                "code": 0,
                "msg": "",
                "index": None,
                "delta": {
                    "content": "hello",
                },
                "tag": "stop",
                "finish_reason": "",
            }
            msg = json.dumps(stop)
            await websocket.send(msg)
        else:
            task = loop.create_task(coro=_handle_msg(websocket, "task0"))


async def main():
    async with websockets.serve(_handle, "localhost", 8989):
        print("ready to serve")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
