import websockets
import asyncio
from handler import BaseHandler, SequentialHandler
import time
import json
import threading
import queue
import os
import openai
from dotenv import load_dotenv
import multiprocessing as mp
import multiprocessing.connection
from concurrent.futures import ProcessPoolExecutor
from langchain.llms import AzureOpenAI
from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler
from typing import Any, Dict, List
from langchain.schema import LLMResult, HumanMessage
from typing import Callable, Union


class MyCustomSyncHandler(BaseCallbackHandler):
    def __init__(self, call_back: Callable[[str], Any]) -> None:
        super().__init__()
        self.cb = call_back

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.cb(token)


class MyCustomAsyncHandler(AsyncCallbackHandler):
    """Async callback handler that can be used to handle callbacks from langchain."""

    def __init__(self, call_back: Callable[[str], Any]) -> None:
        super().__init__()
        self.cb = call_back

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        # print(token)
        # await asyncio.sleep(1)
        self.cb(token)

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.cb(response)

    async def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs
    ) -> None:
        self.cb(error)


class LLMModel:
    def __init__(self) -> None:
        self.websocket = None
        self.index = 0
        self.p = None

        def token_cb(token):
            try:
                if isinstance(token, str):  # 发了个字符串on_llm_new_token
                    if self.p == None:
                        self.p = self.json_client["data"]["questionId"]
                    else:
                        if self.p != self.json_client["data"]["questionId"]:
                            self.index = 0
                    json_return = {
                        "chatId": self.json_client["data"]["chatId"],
                        "questionId": self.json_client["data"]["questionId"],
                        "created": time.time(),
                        "code": 0,
                        "msg": "",
                        "index": self.index,
                        "delta": {
                            "content": token,
                        },
                        "finish_reason": "",
                    }
                    # print(json.dumps(json_return))
                    # await asyncio.sleep(1)
                    time.sleep(1)
                    # print("callback pid :", mp.current_process().pid)
                    self.websocket.send(json.dumps(json_return))
                    self.index += 1
                elif isinstance(token, LLMResult):
                    json_return = {
                        "chatId": self.json_client["data"]["chatId"],
                        "questionId": self.json_client["data"]["questionId"],
                        "created": time.time(),
                        "code": 0,
                        "msg": "",
                        "index": None,
                        "delta": {
                            "content": "",
                        },
                        "finish_reason": "natural",
                    }
                    # await asyncio.sleep(1)
                    self.websocket.send(json.dumps(json_return))
                else:
                    json_return = {
                        "chatId": self.json_client["data"]["chatId"],
                        "questionId": self.json_client["data"]["questionId"],
                        "created": time.time(),
                        "code": 1,
                        "msg": "error when llm running",
                        "index": None,
                        "delta": {
                            "content": "",
                        },
                        "finish_reason": "",
                    }
                    # await asyncio.sleep(1)
                    self.websocket.send(json.dumps(json_return))
            except Exception as e:
                json_return = {
                    "chatId": self.json_client["data"]["chatId"],
                    "questionId": self.json_client["data"]["questionId"],
                    "created": time.time(),
                    "code": 1,
                    "msg": f"{e}",
                    "index": None,
                    "delta": {
                        "content": "",
                    },
                    "finish_reason": "",
                }
                self.websocket.send(json.dumps(json_return))

        load_dotenv("azure.env", override=True)
        # self.chatgpt_model_name = "gpt-35-turbo"
        openai.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_base = os.environ["OPENAI_API_BASE"]
        openai.api_type = os.environ["OPENAI_API_TYPE"]
        openai.api_version = os.environ["OPENAI_API_VERSION"]
        # myhandler = MyCustomSyncHandler(token_cb)
        myhandler = MyCustomAsyncHandler(token_cb)
        self.llm = AzureOpenAI(
            deployment_name="gpt-35-turbo",
            model_name="text-davinci-002",
            streaming=True,
            callbacks=[myhandler],
        )

    async def response(self, connection, data_client):
        self.websocket = connection
        try:
            self.json_client = json.loads(data_client)
            user_message = self.json_client["data"]["content"][0]
            await self.llm.apredict(user_message)
        except json.decoder.JSONDecodeError as json_error:
            json_return = {
                "chatId": -1,
                "questionId": -1,
                "created": time.time(),
                "code": 1,
                "msg": f"{json_error}",
                "index": None,
                "delta": {
                    "content": "",
                },
                "finish_reason": "",
            }
            connection.send(json.dumps(json_return))
        except Exception as e:
            json_return = {
                "chatId": self.json_client["data"]["chatId"],
                "questionId": self.json_client["data"]["questionId"],
                "created": time.time(),
                "code": 1,
                "msg": f"{e}",
                "index": None,
                "delta": {
                    "content": "",
                },
                "finish_reason": "",
            }
            connection.send(json.dumps(json_return))


def init_gpt_model():
    global llmmodel
    llmmodel = LLMModel()


# flag = True


class MyHandler(BaseHandler):
    def __init__(self, addr, port) -> None:
        from concurrent.futures import ProcessPoolExecutor

        self.cnt = 0

        super().__init__(addr, port)

    async def _handle_msg(self, websocket, data_client):
        # pool = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context())
        # print(json.loads(data_client))
        pool = ProcessPoolExecutor(max_workers=1)
        try:
            loop = asyncio.get_event_loop()

            parent_conn, child_conn = multiprocessing.Pipe()
            # TODO: ????
            # await must be added
            # to get llm inference stopped correctly
            loop.run_in_executor(pool, self.process_wrapper, parent_conn, data_client)

            while True:
                # TODO: break on chyld stop???
                child_msg = await asyncio.get_event_loop().run_in_executor(
                    None, child_conn.recv
                )
                print(child_msg)
                await websocket.send(child_msg)

        except asyncio.CancelledError as e:
            print("cancel received")
            for _, process in pool._processes.items():
                print(f"terminating process{process.pid}")
                process.terminate()
            pool.shutdown(wait=False, cancel_futures=True)
            print("cancel finished")

        except Exception as e:
            print("------", e)

    # @staticmethod
    async def _handle(self, websocket):
        # !!!!
        init_gpt_model()

        loop = asyncio.get_event_loop()
        tasks: list[asyncio.Task] = list()
        # print('1')
        async for message in websocket:
            json_client = json.loads(message)
            action = json_client["data"]["action"]
            if action == "stop":
                print("stop received")
                for task in tasks:
                    # await asyncio.sleep(1)
                    task.cancel()
                tasks.clear()
                json_return = {
                    "chatId": json_client["data"]["chatId"],
                    "questionId": json_client["data"]["questionId"],
                    "created": time.time(),
                    "code": 0,
                    "msg": "",
                    "index": None,
                    "delta": {
                        "content": "",
                    },
                    "finish_reason": "provided",
                }
                # flag = False
                signal = json.dumps(json_return)
                # print("handle pid :", mp.current_process().pid)
                await websocket.send(json.dumps(json_return))
            else:
                # flag=True
                task_msg = loop.create_task(coro=self._handle_msg(websocket, message))
                tasks.append(task_msg)

    @staticmethod
    def process_wrapper(connection, data_client):
        async def _process_data(connection, data_client):
            await llmmodel.response(connection, data_client)

        asyncio.run(_process_data(connection, data_client))


if __name__ == "__main__":
    server = MyHandler("localhost", 7776)
    asyncio.run(server.arun())
