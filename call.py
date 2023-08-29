from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage


class MyCustomHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(f"My custom handler, token: {token}")


# To enable streaming, we pass in `streaming=True` to the ChatModel constructor
# Additionally, we pass in a list with our custom handler
chat = ChatOpenAI(openai_api_key='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',max_tokens=25, streaming=True, callbacks=[MyCustomHandler()])

print(chat([HumanMessage(content="Tell me a joke")]))