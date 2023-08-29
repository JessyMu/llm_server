from typing import Optional
import asyncio
import json
import base64
import logging
import multiprocessing as mp
import numpy as np
import time
import websockets
from jsonschema import validate
from scipy.io import wavfile
import ws_handler  # for its __name__
from ws_handler import SequentialHandler, WsData
import argparse
from scipy import interpolate


# def _init_global_mod(weight_path, config_path, initfile):
def _init_global_mod(input):
    print("init global mod:",mp.current_process().pid)
def _hello_from_new_process():
    print('hello new process:',mp.current_process().pid)
    return mp.current_process().pid
class MyHandler(SequentialHandler):
    def __init__(self, addr: str, port: int) -> None:
        from concurrent.futures import ProcessPoolExecutor
        print('MyHandler init function:',mp.current_process().pid)
        executor = ProcessPoolExecutor(
            max_workers=1, initializer=_init_global_mod, initargs=("nihao",)
        )
        future_init = executor.submit(_hello_from_new_process)
        pid_child = future_init.result()
        print('pid_child',pid_child)
        super().__init__(addr, port,executor)

    @staticmethod
    def _process_data(data_client: WsData) -> WsData:
        print('process data',mp.current_process().pid)
        return "hello," + data_client



if __name__ == "__main__":
    print('main',mp.current_process().pid)
    handler = MyHandler(addr="0.0.0.0", port=8848)
    asyncio.run(handler.arun())
