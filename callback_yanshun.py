import asyncio
from typing import Any, Dict, List
from langchain.llms import AzureOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import LLMResult, HumanMessage
from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler
from dotenv import load_dotenv
import openai
import os

from typing import Callable, Any


class MyCustomSyncHandler(BaseCallbackHandler):
    def __init__(self, custom_callback: Callable[[str], Any]) -> None:
        # self.queue = []
        super().__init__()

        self._cb = custom_callback

    def on_llm_new_token(self, token: str, **kwargs):
        # self.queue.append(token)
        # print(f"Sync handler being called in a `thread_pool_executor`: token: {token}")

        self._cb(token)

        # nobody is accepting this return
        # refer to: /home/jesse/.local/lib/python3.10/site-packages/langchain/callbacks/manager.py:305
        # return token


class MyCustomAsyncHandler(AsyncCallbackHandler):
    """Async callback handler that can be used to handle callbacks from langchain."""

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        print("zzzz....")
        await asyncio.sleep(0.3)
        # class_name = serialized["name"]
        print("Hi! I just woke up. Your llm is starting")

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when chain ends running."""
        print("zzzz....")
        await asyncio.sleep(0.3)
        print("Hi! I just woke up. Your llm is ending")



    # return token

def _main():
    global tokens
    tokens = list()  # container for all tokens return by LLM

    # await websocket.send(...)
    def _token_cb(token):
        tokens.append(token)
        print(f"MY_CALLBACK, {token}")
        return token
    
    load_dotenv("azure.env", override=True)
    myhandler = MyCustomSyncHandler(_token_cb)
    llm = AzureOpenAI(
        deployment_name="gpt-35-turbo",
        model_name="text-davinci-002",
        streaming=True,
        callbacks=[myhandler],
    )

    print(llm.predict("Tell me a joke"))

    with open("tokens_join.txt", "w") as f:
        f.write("".join(tokens))


if __name__ == "__main__":
    _main()
