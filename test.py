# import time


# # 使用自定义函数生成回调函数
# def perform_operation(sentence, callback):
#     return callback(sentence)


# # 定义回调函数
# def infer(sentence):
#     words = []
#     for i in range(len(sentence)):
#         words.append(sentence[i])
#         time.sleep(1)

#     # return gptmodel.infer(sentence)
#     return words


# # 调用函数，并传递回调函数作为参数
# for w in perform_operation('今天天气好', infer):
#     print(w)
# # print(res)

import time
from server import LLMModel

# def output_generator():
#     # 假设这是一个每隔一秒输出一个字符的函数
#     for i in range(10):  # 假设输出10个字符
#         time.sleep(1)  # 模拟每隔一秒输出一个字符
#         yield i  # 返回当前字符的值

# # 使用生成器函数
# generator = output_generator()

# # 每次调用生成器的 next() 方法获取下一个字符的值
# for value in output_generator():
#     print("输出字符的值:", value)
# llm=LLMModel()
# llm.infer('ddfa')

# def test(a,b,*c):
#     cnt=0
#     print(c)
#     e,f,g=c
#     cnt=a+b+e+f+g
#     return cnt

# a=test(1,2,3,1,2)
# print(a)
# 初始化gpt模型
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
# %%
load_dotenv("azure.env", override=True)

# %%
base_system_message = "You are a helpful assistant."

system_message = f"{base_system_message.strip()}"

load_dotenv("azure.env", override=True)
chatgpt_model_name = "gpt-35-turbo"

openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_base = os.environ["OPENAI_API_BASE"]
openai.api_type = os.environ["OPENAI_API_TYPE"]
openai.api_version = os.environ["OPENAI_API_VERSION"]
user_message='你好'
messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "name": "example_user", "content": user_message},
]

response = openai.ChatCompletion.create(
    engine=chatgpt_model_name,
    messages=messages,
    temperature=0,
    stream=True,
)
collected_chunks = []
collected_messages = []
# iterate through the stream of events
for chunk in response:
    collected_chunks.append(chunk)  # save the event response
    chunk_message = chunk["choices"][0]["delta"]  # extract the message
    collected_messages.append(chunk_message)  # save the message
    print(
        f"{chunk_message}",
        flush=True,
    )  # print the delay and text

# print the time delay and text received
# print(f"Full response received {chunk_time:.2f} seconds after request")
# full_reply_content = "".join([m.get("content", "") for m in collected_messages])
# print(f"Full conversation received: {full_reply_content}")