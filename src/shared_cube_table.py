import os
import multiprocessing as mp
import numpy as np

size: int = 2000 * 125000 # 2000 * 1 MB / 8 (int size)
opened_name: str = "opened"
closed_name: str = "closed"

def shared_cube_table_to_numpy(shared_arr) -> np.ndarray:
    return np.frombuffer(shared_arr, dtype=np.uint64)

def create_shared_table(name: str):
    shared_table = mp.RawArray('Q', size)
    shared_tab = mp.Value('B', 0, lock=False)
    shared_index = mp.Value('L', 0)
    file_write_sem = mp.Value('B', 0)
    return name, shared_table, shared_tab, shared_index, file_write_sem

def is_not_empty(table_name: str, shared_table, shared_tab, shared_index, file_write_sem) -> bool:
    return shared_tab.value > 0 or shared_index.value > 0

def get_size(table_name: str, shared_table, shared_tab, shared_index, file_write_sem) -> int:
    return shared_tab.value * size + shared_index.value

def clear_table(table_name: str, shared_table, shared_tab, shared_index, file_write_sem):
    while shared_tab.value > 0:
        shared_tab.value -= 1
        os.remove(_get_file_name(table_name, shared_tab.value))
    shared_index.value = 0

def read_table(table_name: str, shared_table, shared_tab, shared_index, file_write_sem) -> np.ndarray:
    table = shared_cube_table_to_numpy(shared_table)
    if shared_index.value != 0:
        index: int = shared_index.value
        shared_index.value = 0
        return table[:index]
    else:
        if _read_file(table_name, shared_table, shared_tab):
            return table
        else:
            raise LookupError

def write_table(value: int, table_name: str, shared_table, shared_tab, shared_index, file_write_sem):
    table = shared_cube_table_to_numpy(shared_table)
    index: int
    # waits for index to increase and potential file write to finish
    with shared_index.get_lock():
        index = shared_index.value
        if index == size:
            # waits for index writes to finish
            while file_write_sem.value != 0:
                pass
            _write_file(table_name, table, shared_tab)
            index = 0
            shared_index.value = 1
        else:
            shared_index.value += 1
        # registers index write
        with file_write_sem.get_lock():
            file_write_sem.value += 1
    
    table[index] = value
    # releases index write
    with file_write_sem.get_lock():
        file_write_sem.value -= 1

def _read_file(table_name: str, shared_table, shared_tab):
    if shared_tab.value > 0:
        shared_tab.value -= 1
        print("Reading file", _get_file_name(table_name, shared_tab.value))
        with open(_get_file_name(table_name, shared_tab.value), "rb") as file:
            arr: bytes = file.read()
        table = shared_cube_table_to_numpy(shared_table)
        table[:] = np.frombuffer(arr, dtype=np.uint64)
        os.remove(_get_file_name(table_name, shared_tab.value))
        return True
    return False

def _write_file(table_name: str, table: np.ndarray, shared_tab) -> None:
    print("Writing file", _get_file_name(table_name, shared_tab.value))
    arr: bytes = table.tobytes()
    with open(_get_file_name(table_name, shared_tab.value), "wb") as file:
        file.write(arr)
    shared_tab.value += 1

def _get_file_name(name: str, tab: int) -> str:
    return "temp/" + name + "_" + str(tab) + ".bin"