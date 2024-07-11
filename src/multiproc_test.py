import time
import numpy as np
from cube_table import CubeTable

from multiprocessing import get_context

table = CubeTable("test", 500)

def _double(val: int) -> int:
    return val * 2

if __name__ == '__main__':
    print("Writing 180 Million values")
    for i in range(180_000_000):
        table.write(i)
    print("Sleeping for 10 seconds")
    time.sleep(10)
    count: int = 0
    pr: int = 1
    
    while table:
        table.prepare_read()
        with get_context("fork").Pool() as pool:
            print("Reading array")
            for sq1s in pool.imap_unordered(_double, table.read(), chunksize=1000):
                count += 1
                if count >= 1_800_000 * pr:
                    print(f"{pr * .01:.0%}")
                    pr += 1
        print("Sleeping for 10 seconds")
        time.sleep(10)

    print("Sleeping for 10 seconds")
    time.sleep(10)
