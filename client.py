#!/usr/bin/env python

import asyncio
import websockets
import json
import time

question = {
    "messageId": "cdb84ddb843d90cb",
    "sendUserId": "client:oY/EQEgWXjCVNjW7qngcj99PWQsjEQj+aPbJ8KwSL0hM3VDlVhYLbQwpLn3IwGW2",
    "data": {
        "action": "question",
        "chatId": "13",
        "questionId": "16",
        "content": ["详细讲解一下随机梯度。"],
    },
}
stop = {
    "messageId": "cdb84ddb843d90cb",
    "sendUserId": "client:oY/EQEgWXjCVNjW7qngcj99PWQsjEQj+aPbJ8KwSL0hM3VDlVhYLbQwpLn3IwGW2",
    "data": {
        "action": "stop",
        "chatId": "13",
        "questionId": "16",
        "content": ["详细讲解一下随机梯度。"],
    },
}


async def hello():
    uri = "ws://localhost:7777"
    async with websockets.connect(uri) as websocket:

        await websocket.send(json.dumps(question))
        time1=time.time()
        async for message in websocket:
            greeting = await websocket.recv()
            if time.time()-time1 >10:
                print('我要发送stop了')
                await websocket.send(json.dumps(stop))
                stop_signal=await websocket.recv()
                print(stop_signal)
                # await asyncio.sleep(1)
                # await websocket.send(json.dumps(question))
                # greeting=await websocket.recv()
                time1=time.time()
            print(greeting)


if __name__ == "__main__":
    asyncio.run(hello())
