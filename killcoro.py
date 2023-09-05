
import asyncio

async def my_coroutine():
    try:
        while True:
            print("Coroutine running")
            await asyncio.sleep(1)  # 模拟耗时的操作
            # print("Coroutine finished")
    except asyncio.CancelledError:
        print("Coroutine cancelled")

# 创建一个事件循环对象
loop = asyncio.get_event_loop()

# 创建一个Task对象
task = loop.create_task(my_coroutine())

# 在一段时间后取消协程
loop.call_later(3, task.cancel)

# 运行事件循环
loop.run_until_complete(task)

# 关闭事件循环
loop.close()