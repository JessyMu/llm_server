import json
import multiprocessing as mp
import time
import asyncio
import websockets


async def _handle_msg():
    try:
        print("1")
        # while True:
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
        await web.send(question)
    except asyncio.CancelledError as ex:
        print(f"Cancelled! {ex}")


async def _handle(websocket):
    global web
    web = websocket
    loop = asyncio.get_event_loop()

    SLEEP_INTERVAL = 0.1  # wait some time to let task be dispatched

    async for message in websocket:
        print(f"start loop {message}")
        task = loop.create_task(coro=_handle_msg())
        await asyncio.sleep(SLEEP_INTERVAL)
        task.cancel("task0")

        task1 = loop.create_task(coro=_handle_msg())
        await asyncio.sleep(SLEEP_INTERVAL)
        task1.cancel("task1")


async def main():
    async with websockets.serve(_handle, "localhost", 8989):
        print("ready to serve")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
