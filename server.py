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
            chunk_message = chunk["choices"][0]["delta"]  # extract the message
            yield chunk_message.get("content", "")
            collected_messages.append(chunk_message)  # save the message
            # print(
            #     f"Message received {chunk_time:.2f} seconds after request: {chunk_message}",
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

        executor = ProcessPoolExecutor(
            max_workers=1, initializer=init_gpt_model, initargs=()
        )
        self.executor = executor
        super().__init__(addr, port)

    # @staticmethod
    async def _handle(self, websocket):
        async for message in websocket:
            print(json.loads(message)["data"]["action"])
            # message = await websocket.recv()
            # print("handle pid :", mp.current_process().pid)
            loop = asyncio.get_running_loop()
            print("123")
            server_data = loop.run_in_executor(
                self.executor, self._process_data, message,websocket
            )
            asyncio.ensure_future(websocket.send('1211'))
            # self.send(websocket,'123566')
            # await websocket.send('0000')
            print("890")
            # await websocket.send(server_data)
    # @staticmethod
    async def send(self,websocket,msg):
        print(msg)
        await websocket.send(msg)
    @staticmethod
    async def _process_data(data_client,websocket):
        try:
            # 解json
            json_recv = json.loads(data_client)
            json_data = json_recv["data"]
            action = json_data["action"]
            chatId = json_data["chatId"]
            questionId = json_data["questionId"]
            content = json_data["content"][-1]
            end = True
            print(content)
            if action == "stop":
                # 确认任务停止了
                json_return = {
                    "chatId": chatId,
                    "questionId": questionId,
                    "created": time.time(),
                    "code": 0,
                    "msg": "",
                    "index": None,
                    "delta": {
                        "content": "",
                    },
                    "finish_reason": "provided",
                }
            else:
                index = 0
                # for value in llmmodel.infer(content):
                for value in llmmodel.response(content):
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
                    print(json_return)
                    await websocket.send(json.dumps(json_return))
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
        finally:
            if end:
                data_server = json.dumps(json_return)
                # return data_server
                await websocket.send(data_server)


if __name__ == "__main__":
    server = MyHandler("localhost", 9098)
    asyncio.run(server.arun())
