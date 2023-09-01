import multiprocessing as mp

_print = print


def print(*args, **kwargs):
    _print(mp.current_process().pid, *args, **kwargs)


def func():
    print("hello")


def func_wrapper(function):
    function()


def _main():
    # func()
    func_wrapper(function)

    proc = mp.Process(target=func_wrapper, args=func)
    proc.start()
    proc.join()


if __name__ == "__main__":
    _main()
