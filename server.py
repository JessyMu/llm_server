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
from concurrent.futures import ProcessPoolExecutor


class LLMModel:
    def __init__(self) -> None:
        # 初始化gpt模型
        # %%
        load_dotenv("azure.env", override=True)

        # %%
        base_system_message = "You are a helpful assistant."

        self.system_message = f"{base_system_message.strip()}"

        load_dotenv("azure.env", override=True)
        self.chatgpt_model_name = "gpt-35-turbo"

        openai.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_base = os.environ["OPENAI_API_BASE"]
        openai.api_type = os.environ["OPENAI_API_TYPE"]
        openai.api_version = os.environ["OPENAI_API_VERSION"]

    def response(self, user_message):
        # This is the first user message that will be sent to the model. Feel free to update this.

        # Create the list of messages. role can be either "user" or "assistant"
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "name": "example_user", "content": user_message},
        ]

        # %%
        # Example of an OpenAI ChatCompletion request with stream=True
        # https://platform.openai.com/docs/guides/chat

        # record the time before the request is sent
        # start_time = time.time()

        # send a ChatCompletion request to count to 100
        # response = openai.ChatCompletion.create(
        #     model='gpt-3.5-turbo',
        #     messages=[
        #         {'role': 'user', 'content': 'Count to 100, with a comma between each number and no newlines. E.g., 1, 2, 3, ...'}
        #     ],
        #     temperature=0,
        #     stream=True  # again, we set stream=True
        # )

        response = openai.ChatCompletion.create(
            engine=self.chatgpt_model_name,
            messages=messages,
            # temperature=0.5,
            # max_tokens=500,
            # top_p=0.9,
            # frequency_penalty=0,
            # presence_penalty=0,
            # stream=True,
            # messages=messages,
            temperature=0,
            stream=True,
        )
        # create variables to collect the stream of chunks
        # collected_chunks = []
        collected_messages = []
        # iterate through the stream of events
        for chunk in response:
            # chunk_time = (
            #     time.time() - start_time
            # )  # calculate the time delay of the chunk
            # collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk["choices"][0]["delta"]  # extract the message\
            print(chunk_message.get("content", ""))
            # yield chunk_message.get("content", "")
            collected_messages.append(chunk_message)  # save the message
            # print(
            #     f"Message received : {chunk_message}",
            #     flush=True,
            # )  # print the delay and text

        # print the time delay and text received
        # print(f"Full response received {chunk_time:.2f} seconds after request")
        full_reply_content = "".join([m.get("content", "") for m in collected_messages])
        # print(f"Full conversation received: {full_reply_content}")
        return full_reply_content


def init_gpt_model():
    global llmmodel
    llmmodel = LLMModel()


class MyHandler(BaseHandler):
    def __init__(self, addr, port) -> None:
        from concurrent.futures import ProcessPoolExecutor

        self.cnt = 0

        init_gpt_model()
        # executor = ProcessPoolExecutor(
        #     max_workers=1, initializer=init_gpt_model, initargs=()
        # )
        # self.executor = executor
        super().__init__(addr, port)

    async def _handle_msg(self, websocket, data_client):
        pool = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context())
        # pool = ProcessPoolExecutor(max_workers=1)
        print(json.loads(data_client))
        try:
            self.cnt += 1
            loop = asyncio.get_event_loop()
            # async for data in await loop.run_in_executor(
            #     pool, self._process_data, data_client
            # ):
            #     await websocket.send(data)
            # data = await loop.run_in_executor(pool, self._process_data, data_client)
            # data=await future
            future = loop.run_in_executor(pool, self._process_data, data_client)
            data = await future
            # print((data))
            await websocket.send(data)
        except asyncio.CancelledError as e:
            print(self.cnt)
            for _, process in pool._processes.items():
                process.terminate()
                self.cnt -= 1
            print(self.cnt)
            pool.shutdown(wait=False, cancel_futures=True)

        except Exception as e:
            print(e)

    # @staticmethod
    async def _handle(self, websocket):
        loop = asyncio.get_event_loop()
        task = None
        # tasks:list[asyncio.Task]=list()
        # task=asyncio.create_task()
        async for message in websocket:
            json_client = json.loads(message)
            action = json_client["data"]["action"]
            if action == "stop":
                if task != None:
                    task.cancel()
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

                await websocket.send(json.dumps(json_return))
            else:
                task = loop.create_task(coro=self._handle_msg(websocket, message))

    @staticmethod
    def _process_data(data_client):
        try:
            # 解json

            json_recv = json.loads(data_client)
            json_data = json_recv["data"]
            # action = json_data["action"]
            chatId = json_data["chatId"]
            questionId = json_data["questionId"]
            content = json_data["content"][-1]
            print(content)

            index = 0
            # for value in llmmodel.response(content):
            value = llmmodel.response(content)
            # print(value)
            # print("process pid :", mp.current_process().pid)
            json_return = {
                "chatId": chatId,
                "questionId": questionId,
                "created": time.time(),
                "code": 0,
                "msg": "",
                "index": index,
                "delta": {
                    "content": value,
                },
                "finish_reason": "",
            }
            index += 1
            # print(json_return)
            # yield json.dumps(json_return)
            return json.dumps(json_return)
        except Exception as exception:
            json_return = {
                "chatId": chatId,
                "questionId": questionId,
                "created": time.time(),
                "code": 1,
                "msg": f"{exception}",
                "index": None,
                "delta": {
                    "content": "",
                },
                "finish_reason": "",
            }
            # yield json.dumps(json_return)
            return json.dumps(json_return)


if __name__ == "__main__":
    server = MyHandler("localhost", 9098)
    asyncio.run(server.arun())
