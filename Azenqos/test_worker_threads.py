import worker
import global_config as gc
import time


def test():
    w = worker.Worker(work_func, 1)
    gc.threadpool.start(w)
    print("gc.threadpool.activeThreadCount0:", gc.threadpool.activeThreadCount())
    time.sleep(0.1)
    print("gc.threadpool.activeThreadCount1:", gc.threadpool.activeThreadCount())
    assert gc.threadpool.activeThreadCount() == 1
    time.sleep(0.6)
    print("gc.threadpool.activeThreadCount2:", gc.threadpool.activeThreadCount())
    assert gc.threadpool.activeThreadCount() == 0
    assert w.ret == 2


def work_func(a):
    print("work_func: a:", a)
    time.sleep(0.5)
    return a + 1


if __name__ == "__main__":
    test()
