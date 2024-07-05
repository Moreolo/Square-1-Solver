from time import time

import numpy as np
import multiprocessing as mp

n_processes = mp.cpu_count()

def _init(idx_queue, shared_locks_, shared_table_):
    global idx
    global shared_locks
    global shared_table
    idx = idx_queue.get()
    shared_locks = shared_locks_
    shared_table = shared_table_

def shared_to_numpy(shared_arr) -> np.ndarray:
    try:
        return np.frombuffer(shared_arr.get_obj(), dtype=np.int64)
    except:
        return np.frombuffer(shared_arr, dtype=np.int64)

def create_shared_table(size: int):
    cdtype = np.ctypeslib.as_ctypes_type(np.int64)
    shared_table = mp.RawArray(cdtype, size)
    table = shared_to_numpy(shared_table)
    table[:] = np.full(size, 255, dtype=np.int64)
    return shared_table, table

def create_shared_locks():
    cdtype = np.ctypeslib.as_ctypes_type(np.int64)
    shared_locks = mp.Array(cdtype, n_processes)
    locks = shared_to_numpy(shared_locks)
    locks[:] = np.full(n_processes, -1)
    return shared_locks


def square(x: int):
    locks = shared_to_numpy(shared_locks)
    with shared_locks.get_lock():
        while (x >> 2) in locks:
            print("--------------------------")
        locks[idx] = (x >> 2)
    result: int = x * x
    print(idx, "calculating", x, "*", x, "=", result)
    table = shared_to_numpy(shared_table)
    table[x] = result
    locks[idx] = -1
    return result

if __name__ == '__main__':
    shared_table_, table = create_shared_table(10000)
    shared_locks_ = create_shared_locks()
    tasks = [_ for _ in range(10000)]
    idx_queue = mp.Queue()
    for i in range(n_processes):
        idx_queue.put(i)
    start = time()
    with mp.get_context("fork").Pool(n_processes, initializer=_init, initargs=(idx_queue, shared_locks_, shared_table_)) as pool:
        for i in pool.imap_unordered(square, tasks):
            pass
    print(time() - start)
    if 255 in table:
        print("255 in table")