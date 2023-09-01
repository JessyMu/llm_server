# import json
# try:
#     print(1/0)

# except json.decoder.JSONDecodeError as je:
#     print(f'{je}')
# except Exception as e:
#     print(f'{e}')
# print(type('sdfa'))
# print()
from typing import Union
def handle_exception(e: Union[Exception, KeyboardInterrupt]) -> None:
    if isinstance(e, Exception):
        print(f'{e}')
    elif isinstance(e, KeyboardInterrupt):
        print(f'{e}')
    else:
        print("未知类型的异常")

# 调用函数并传入不同的参数
handle_exception(ValueError("无效值"))
handle_exception(KeyboardInterrupt())