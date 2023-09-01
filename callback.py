import asyncio
from typing import Any, Dict, List
from langchain.llms import AzureOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import LLMResult, HumanMessage
from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler
from dotenv import load_dotenv
import openai
import os
from concurrent.futures import ProcessPoolExecutor


class MyCustomSyncHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        self.queue = []
        super().__init__()

    def on_llm_new_token(self, token: str, **kwargs):
        self.queue.append(token)
        print(f"Sync handler being called in a `thread_pool_executor`: token: {token}")
        return token



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
    async def on_llm_new_token(self, token: str, **kwargs):
        print(f"Sync handler being called in a `thread_pool_executor`: token: {token}")

# To enable streaming, we pass in `streaming=True` to the ChatModel constructor
# Additionally, we pass in a list with our custom handler
async def main():
    load_dotenv("azure.env", override=True)
    openai.api_key = os.environ["OPENAI_API_KEY"]
    openai.api_base = os.environ["OPENAI_API_BASE"]
    openai.api_type = os.environ["OPENAI_API_TYPE"]
    openai.api_version = os.environ["OPENAI_API_VERSION"]
    myhandler=MyCustomAsyncHandler()
    llm = AzureOpenAI(
        deployment_name="gpt-35-turbo",
        model_name="text-davinci-002",
        streaming=True,
        callbacks=[myhandler],
    )
    await llm.apredict("Tell me a joke")


asyncio.run(main())
