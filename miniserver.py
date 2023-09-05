import websockets
import asyncio
import time
import json
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

connection=mp.Manager().Namespace()
connection.web=None

async def _handle_msg(signal):
    pool = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context())
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(pool, process_wrapper, signal)

    except asyncio.CancelledError as e:
        # print("外层捕获")
        print("cancel received")
        for _, process in pool._processes.items():
            print(f"terminating process{process.pid}")
            process.terminate()
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
        # await web.send(json.dumps(stop))
        print(json.dumps(stop))


def kill(pool):
    print("cancel received")
    for _, process in pool._processes.items():
        print(f"terminating process{process.pid}")
        process.terminate()
    pool.shutdown(wait=False, cancel_futures=True)
    print("cancel finished")


def process_wrapper(signal):
    async def _process(signal):
        try:
            if signal == "stop":
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
                await connection.web.send(json.dumps(stop))
                pass
            else:
                while True:
                    question = {
                        "chatId": 1,
                        "questionId": 1,
                        "created": time.time(),
                        "code": 0,
                        "msg": "",
                        "index": 0,
                        "delta": {
                            "content": "hello",
                        },
                        "finish_reason": "",
                    }
                    j = json.dumps(question)
                    print(j)
                    print("question pid", mp.current_process().pid)
                    await connection.web.send(j)
                    await asyncio.sleep(1)
        except Exception as e:
            print(e)

    asyncio.run(_process(signal))


async def _handle(websocket):
    
    connection.web=1
    # web = websocket
    task = None
    print("1")
    async for message in websocket:
        json_msg = json.loads(message)
        action = json_msg["data"]["action"]
        if action == "stop":
            print("stop接收到了")
            # kill
            
            if task!=None:
                print(task.cancel())
                task=None
        
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
            # await task
            # loop=asyncio.get_event_loop()
            # await loop.run_in_executor(websockets.serve(_handle, "localhost", 7777))
            await connection.web.send(json.dumps(stop))
            print("stop pid", mp.current_process().pid)
        else:
            task = asyncio.create_task(_handle_msg("question"))


import asyncio
import websockets


async def main():
    async with websockets.serve(_handle, "localhost", 7712):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
