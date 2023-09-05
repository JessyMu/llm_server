
# import threading
# import time

# # 线程退出标志
# exit_flag = False

# # 线程执行函数
# def my_thread_function():
#     global exit_flag
#     while not exit_flag:
#         # 线程执行的工作
#         print("Thread is running...")
#         time.sleep(1)
#     print("Thread is exiting.")

# # 创建线程
# my_thread = threading.Thread(target=my_thread_function)

# # 启动线程
# my_thread.start()

# # 等待一段时间
# time.sleep(5)

# # 设置退出标志以终止线程
# exit_flag = True

# # 等待线程退出
# my_thread.join()

# print("Main thread exiting.")

import threading
import time

def child_thread():
    while True:
        print("Child thread is running...")
        time.sleep(1)

# 创建子线程并启动
thread = threading.Thread(target=child_thread)
thread.start()

# 主线程等待一段时间后终止子线程
time.sleep(5)
if thread.is_alive():
    thread.cancel()

print("Main thread exits.")