from langchain.callbacks import StdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# handler = StdOutCallbackHandler()
# llm = OpenAI(openai_api_key="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")




# print(llm.predict("hi!"))

# prompt = PromptTemplate.from_template("1 + {number} = ")

# # Constructor callback: First, let's explicitly set the StdOutCallbackHandler when initializing our chain
# chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler])
# chain.run(number=2)

# # Use verbose flag: Then, let's use the `verbose` flag to achieve the same result
# chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
# chain.run(number=2)

# # Request callbacks: Finally, let's use the request `callbacks` to achieve the same result
# chain = LLMChain(llm=llm, prompt=prompt)
# chain.run(number=2, callbacks=[handler])
import os
os.environ["OPENAI_API_KEY"] = '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'
from langchain.llms import OpenAI

llm = OpenAI(model_name="text-davinci-003",max_tokens=1024)
llm("怎么评价人工智能")