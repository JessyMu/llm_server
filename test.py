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

def test(a,b,*c):
    cnt=0
    print(c)
    e,f,g=c
    cnt=a+b+e+f+g
    return cnt

a=test(1,2,3,1,2)
print(a)