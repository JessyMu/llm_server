import websockets
import asyncio
import time
import json
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp


async def _handle_msg(str):
    # pool = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context())
    pool = ThreadPoolExecutor(max_workers=1)
    try:
        loop = asyncio.get_event_loop()
        if str == "1":
            await loop.run_in_executor(pool, process_wrapper, str)
        elif str == "2":
            await loop.run_in_executor(pool, process_wrapper2, str)

    except asyncio.CancelledError as e:
        # print("外层捕获")
        print("cancel received")
        # for _, process in pool._processes.items():
        #     print(f"terminating process{process.pid}")
        #     process.terminate()
        pool.shutdown(wait=False, cancel_futures=True)
        print("cancel finished")
        stop = {
            "chatId": 1,
            "questionId": 1,
            "created": time.time(),
            "code": 0,
            "msg": "",
            "index": None,
            "delta": {
                "content": "",
            },
            "finish_reason": "provided",
        }
        # await asyncio.sleep(5)
        # await web.send(json.dumps(stop))
        # print(json.dumps(stop))


def process_wrapper(str):
    async def _process(str):
        try:
            start = time.time()
            while time.time() - start < 5:
                if int(time.time()) % 2 == 0:
                    question = {
                        "chatId": 1,
                        "questionId": 1,
                        "created": time.time(),
                        "code": 0,
                        "msg": str,
                        "index": 0,
                        "delta": {
                            "content": "hello",
                        },
                        "finish_reason": "",
                    }
                    j = json.dumps(question)
                    print(j)
                    print("question pid", mp.current_process().pid)
                    await web.send(j)
                    await asyncio.sleep(1)
        except Exception as e:
            print(e)

    asyncio.run(_process(str))


def process_wrapper2(str):
    async def _process2(str):
        try:
            start = time.time()
            while True:
            # while time.time() - start < 10:
                if int(time.time()) % 2 != 0:
                    question = {
                        "chatId": 1,
                        "questionId": 1,
                        "created": time.time(),
                        "code": 0,
                        "msg": str,
                        "index": 0,
                        "delta": {
                            "content": "hello",
                        },
                        "finish_reason": "",
                    }
                    j = json.dumps(question)
                    print(j)
                    print("question pid", mp.current_process().pid)
                    await web.send(j)
                    await asyncio.sleep(1)
        except Exception as e:
            print(e)

    asyncio.run(_process2(str))


async def _handle(websocket):
    global web
    global flag
    flag=True
    web = websocket
    task = None
    print("1")
    async for message in websocket:
        json_msg = json.loads(message)
        action = json_msg["data"]["action"]
        if action == "stop":
            print("stop接收到了",time.time())
            # kill
            task.cancel()
            flag=False
            stop = {
                "chatId": 1,
                "questionId": 1,
                "created": time.time(),
                "code": 0,
                "msg": "",
                "index": None,
                "delta": {
                    "content": "",
                },
                "finish_reason": "provided",
            }
            # await asyncio.sleep(2.4)
            await web.send(json.dumps(stop))
            print("stop pid", mp.current_process().pid)

        else:
            task = asyncio.create_task(_handle_msg("2"))
            flag=True
            # await asyncio.sleep(1)
            # task.cancel()
            # await task

            # await asyncio.sleep(10)
            # task1 = asyncio.create_task(_handle_msg("1"))
            # await asyncio.sleep(1)
            # task1.cancel()
            # await task1


import asyncio
import websockets


async def main():
    async with websockets.serve(_handle, "localhost", 1245):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
