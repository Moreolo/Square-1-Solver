from functools import partial
from time import time

from multiprocessing import get_context, cpu_count, Array, RawArray, Queue

import numpy as np
from cube_table import CubeTable

from square1 import Square1
from state.state_sq_sq import StateSqSq
from state.state_cs import StateCS
from state.state_all import StateAll

n_processes = cpu_count() // 2

class PruningTable:
    CS: int = 0
    SQSQ: int = 1
    ALL: int = 2

    def __init__(self, state_type: int = CS, block_generation: bool = False, force_generation: bool = False) -> None:
        self.state_type = state_type
        if state_type == PruningTable.CS:
            self.size = StateCS.size
            self.max_slices = StateCS.max_slices
        elif state_type == PruningTable.SQSQ:
            self.size = StateSqSq.size
            self.max_slices = StateSqSq.max_slices
        elif state_type == PruningTable.ALL:
            self.size = StateAll.size
            self.max_slices = StateAll.max_slices
        else:
            self.size = 0
            self.max_slices = 0

        self.table: np.ndarray
        if state_type == PruningTable.CS:
            self.table = np.full((self.size + 1) // 2, 255, dtype=np.uint8)
        else:
            self.shared_table, self.table = create_shared_table((self.size + 1) // 2)
            self.shared_locks = create_shared_locks()

        if force_generation:
            self.generate_pruning_table()
            print("Saving Table to file", self._get_filename())
            self.save_table()
            print("Table saved")
        else:
            try:
                self.load_table()
            except FileNotFoundError:
                print(self._get_filename(), "not found")
                if not block_generation:
                    self.generate_pruning_table()
                    print("Saving Table to file", self._get_filename())
                    self.save_table()
                    print("Table saved")
            else:
                print("Table successfully loaded from file", self._get_filename())

    def save_table(self) -> None:
        with open(self._get_filename(), "wb") as file:
            np.save(file, self.table)

    def load_table(self) -> None:
        with open(self._get_filename(), "rb") as file:
            self.table = np.load(file)

    def read(self, index: int) -> int:
        if index % 2 == 0:
            return self.table[index // 2] // 16
        else:
            return self.table[index // 2] % 16


    def generate_pruning_table(self) -> None:
        self.filled: int = 0
        if self.state_type == PruningTable.CS:
            self.step_rel: float = .1
        elif self.state_type == PruningTable.SQSQ:
            self.step_rel: float = .001
        elif self.state_type == PruningTable.ALL:
            self.step_rel: float = .0001
        self.step_abs: int = int(self.step_rel * self.size)
        self.step: int = 1
        if self.max_slices == 0:
            return
        print("Generating Pruning Table")
        start_time = time()
        if self.state_type == PruningTable.CS:
            self._gpt_cs()
        elif self.state_type == PruningTable.SQSQ:
            self._gpt_sqsq()
        elif self.state_type == PruningTable.ALL:
            self._gpt_all()
        dur = time() - start_time
        if dur < 30:
            print("Generation took", f"{dur:.2f}", "seconds")
        elif dur < 3 * 60:
            print("Generation took", int(dur), "seconds")
        elif dur < 3 * 3600:
            print("Generation took", int(dur) // 60, "minutes and", int(dur) % 60, "seconds")
        else:
            print("Generation took", int(dur) // 3600, "hours,", (int(dur) // 60) % 60, "minutes and", int(dur) % 60, "seconds")


    def _gpt_cs(self) -> None:
        print("Cube Shape")
        print("Maximum Slice Depth:", self.max_slices)
        print("Table Size:", self.size)
        slice_depth: int = 0
        opened: list[int] = [Square1().get_int()]
        while opened:
            print("Check and write states for slice depth", slice_depth)
            closed: list[int] = []
            while opened:
                sq1: int = opened.pop()
                if self._write(StateCS(Square1(sq1)).get_index(), slice_depth) and slice_depth < self.max_slices:
                    closed.append(sq1)

            if closed and (self.filled < self.size):
                slice_depth += 1
                print("Generate states for slice depth", slice_depth)
                while closed:
                    sq1: int = closed.pop()
                    for mirror in range(2):
                        base: Square1 = Square1(sq1)
                        if mirror:
                            base.mirror_layers()
                        turns: list[tuple[int, int]] = base.get_unique_turns()
                        for turn in turns:
                            square1: Square1 = base.get_copy()
                            square1.turn_layers(turn)
                            square1.turn_slice()
                            opened.append(square1.get_int())
        print("Maximum slice depth", slice_depth)

    def _gpt_sqsq(self) -> None:
        print("Square Square")
        print("Maximum Slice Depth:", self.max_slices)
        print("Table Size:", self.size)
        slice_depth: int = 0
        opened: CubeTable = CubeTable("opened", size=25)
        opened.write(Square1().get_int())
        closed: CubeTable = CubeTable("closed", size=2)

        while opened:
            print("Check", len(opened), "states for slice depth", slice_depth)
            job = partial(_fill_table_sqsq, slice_depth)
            while opened:
                opened.prepare_read()
                idx_queue: Queue = Queue()
                for i in range(n_processes):
                    idx_queue.put(i)
                with get_context("fork").Pool(n_processes, initializer=_init, initargs=(idx_queue, self.shared_locks, self.shared_table)) as pool:
                    for sq1 in pool.imap_unordered(job, opened.read(), chunksize=4000):
                        if sq1 is not None:
                            self._increase_fill(sq1[1])
                            if slice_depth < self.max_slices:
                                closed.write(sq1[0])
                    if self.filled == self.size:
                        break

            opened.clear()
            if closed and (self.filled < self.size):
                slice_depth += 1
                print("Generate states from", len(closed), "states for slice depth", slice_depth)
                step_rel: float = .1
                step_abs: int = int(step_rel * len(closed))
                step: int = 1
                counter: int = 0
                with get_context("spawn").Pool(n_processes * 2) as pool:
                    while closed:
                        closed.prepare_read()
                        for sq1s in pool.imap_unordered(_generate_next_cubes_sqsq, closed.read(), chunksize=1000):
                            for sq1 in sq1s:
                                opened.write(sq1)
                            if step_abs != 0:
                                counter += 1
                                while counter >= step * step_abs:
                                    print(f"{step * step_rel:.0%}", "of states generated")
                                    step += 1
        print("Maximum slice depth", slice_depth)

    def _gpt_all(self) -> None:
        print("Complete Cube")
        print("Maximum Slice Depth:", self.max_slices)
        print("Table Size:", self.size)
        slice_depth: int = 0
        opened: CubeTable = CubeTable("opened", 8000)
        opened.write(Square1().get_int())
        closed: CubeTable = CubeTable("closed", 500)

        while opened:
            print("Check", len(opened), "states for slice depth", slice_depth)
            job = partial(_fill_table_all, slice_depth)
            while opened:
                opened.prepare_read()
                idx_queue: Queue = Queue()
                for i in range(n_processes):
                    idx_queue.put(i)
                with get_context("fork").Pool(n_processes, initializer=_init, initargs=(idx_queue, self.shared_locks, self.shared_table)) as pool:
                    for sq1 in pool.imap_unordered(job, opened.read(), chunksize=4000):
                        if sq1 is not None:
                            self._increase_fill(sq1[1], slice_depth)
                            if slice_depth < self.max_slices:
                                closed.write(sq1[0])
                    if self.filled == self.size:
                        break

            opened.clear()
            if closed and (self.filled < self.size):
                slice_depth += 1
                print("Generate states from", len(closed), "states for slice depth", slice_depth)
                step_rel: float = .01
                step_abs: int = int(step_rel * len(closed))
                step: int = 1
                counter: int = 0
                with get_context("spawn").Pool(n_processes * 2) as pool:
                    while closed:
                        closed.prepare_read()
                        for sq1s in pool.imap_unordered(_generate_next_cubes_all, closed.read(), chunksize=1000):
                            for sq1 in sq1s:
                                opened.write(sq1)
                            if step_abs > 5000:
                                counter += 1
                                while counter >= step * step_abs:
                                    print(f"{step * step_rel:.0%}", "of states generated")
                                    step += 1
        print("Maximum slice depth", slice_depth)

    def _get_filename(self) -> str:
        if self.state_type == PruningTable.CS:
            return "pruning_table_cs.bin"
        elif self.state_type == PruningTable.SQSQ:
            return "pruning_table_sqsq.bin"
        elif self.state_type == PruningTable.ALL:
            return "pruning_table_all.bin"
        else:
            return "pruning_table_none.bin"

    def _write(self, index: int, value: int) -> bool:
        table_value: int = self.table[index >> 1]
        if not index & 1:
            left: int = table_value >> 4
            if left == 15:
                right: int = table_value % 16
                self.table[index >> 1] = (value << 4) + right
                self._increase_fill()
                return True
        else:
            right: int = table_value % 16
            if right == 15:
                left: int = table_value >> 4
                self.table[index >> 1] = (left << 4) + value
                self._increase_fill()
                return True
        return False

    def _increase_fill(self, increase: int = 1, slice_depth: (int | None) = None) -> None:
        slices: str = ""
        if slice_depth is not None:
            slices = "/" + str(slice_depth)
        self.filled += increase
        while self.filled >= self.step * self.step_abs:
            if self.state_type == PruningTable.CS:
                print(f"{self.step * self.step_rel:.0%}", "filled", slices)
            elif self.state_type == PruningTable.SQSQ:
                print(f"{self.step * self.step_rel:.1%}", "filled", slices)
            else:
                print(f"{self.step * self.step_rel:.2%}", "filled", slices)
            self.step += 1

# gets next cubes for square square
def _generate_next_cubes_sqsq(sq1: int) -> np.ndarray:
    square1: Square1 = Square1(sq1)
    turns: list[tuple[int, int]] = square1.get_unique_turns_sq_sq()
    sq1s: np.ndarray = np.empty(16, dtype=np.uint64)
    for i in range(len(turns)):
        square1.turn_layers(turns[i])
        square1.turn_slice()
        sq1s[i] = square1.get_int()
        square1 = Square1(sq1)
    return sq1s

# gets next cubes for all
def _generate_next_cubes_all(sq1: int) -> np.ndarray:
    square1: Square1 = Square1(sq1)
    turns: list[tuple[int, int]] = square1.get_unique_turns()
    sq1s: np.ndarray = np.empty(len(turns), dtype=np.uint64)
    for i in range(len(turns)):
        square1.turn_layers(turns[i])
        square1.turn_slice()
        sq1s[i] = square1.get_int()
        square1 = Square1(sq1)
    return sq1s

def _init(idx_queue: Queue, shared_locks_, shared_table_) -> None:
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
        return np.frombuffer(shared_arr, dtype=np.uint8)

def create_shared_table(size: int):
    cdtype = np.ctypeslib.as_ctypes_type(np.uint8)
    shared_table = RawArray(cdtype, size)
    table = shared_to_numpy(shared_table)
    table[:] = np.full(size, 255, dtype=np.uint8)
    return shared_table, table

def create_shared_locks():
    cdtype = np.ctypeslib.as_ctypes_type(np.int64)
    shared_locks = Array(cdtype, n_processes)
    locks = shared_to_numpy(shared_locks)
    locks[:] = np.full(n_processes, -1, np.int64)
    return shared_locks

# returns cube and number of successful writes if state is new in slice depth
def _fill_table_sqsq(slice_depth: int, sq1: int) -> (tuple[int, int] | None):
    state: StateSqSq = StateSqSq(Square1(sq1))
    if _shared_write(state.get_index(), slice_depth):
        fill_increase: int = 1
        for index in state.get_symmetric_indecies():
            if _shared_write(index, slice_depth):
                fill_increase += 1
        return state.square1.get_int(), fill_increase

# returns cube and number of successful writes if state is new in slice depth
def _fill_table_all(slice_depth: int, sq1: int) -> (tuple[int, int] | None):
    state: StateAll = StateAll(Square1(sq1))
    if _shared_write(state.get_index(), slice_depth):
        fill_increase: int = 1
        for index in state.get_symmetric_indecies():
            if _shared_write(index, slice_depth):
                fill_increase += 1
        return state.square1.get_int(), fill_increase

def _shared_write(index: int, slice_depth: int) -> bool:
    table_index: int = index >> 1
    # accquires lock for table entry
    locks = shared_to_numpy(shared_locks)
    table = shared_to_numpy(shared_table)
    with shared_locks.get_lock():
        while table_index in locks:
            pass
        locks[idx] = table_index
    # checks and writes table entry
    new_entry: bool = False
    table_value: int = table[table_index]
    if not index & 1:
        left: int = table_value >> 4
        if left == 15:
            # writes to table if empty
            right: int = table_value % 16
            table[table_index] = (slice_depth << 4) + right
            new_entry = True
    else:
        right: int = table_value % 16
        if right == 15:
            # writes to table if empty
            left: int = table_value >> 4
            table[table_index] = (left << 4) + slice_depth
            new_entry = True
    # releases lock
    locks[idx] = -1
    return new_entry