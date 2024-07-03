from time import time

from multiprocessing import get_context

import numpy as np

from square1 import Square1
from state_sq_sq import StateSqSq
from state_cs import StateCS

class PruningTable:
    CS: int = 0
    SQSQ: int = 1

    def __init__(self, state_type: int = CS, force_generation: bool = False) -> None:
        self.state_type = state_type
        if state_type == PruningTable.CS:
            self.size = StateCS.size
            self.max_slices = StateCS.max_slices
        elif state_type == PruningTable.SQSQ:
            self.size = StateSqSq.size
            self.max_slices = StateSqSq.max_slices
        else:
            self.size = 0
            self.max_slices = 0

        self.table: np.ndarray = np.full((self.size + 1) // 2, 255, dtype=np.uint8)

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
                self.generate_pruning_table()
                print("Saving Table to file", self._get_filename())
                self.save_table()
                print("Table saved")
            else:
                print("Table successfully loaded from file", self._get_filename())

    def save_table(self) -> None:
        arr: bytes = self.table.tobytes()
        with open(self._get_filename(), "wb") as file:
            file.write(arr)

    def load_table(self) -> None:
        with open(self._get_filename(), "rb") as file:
            arr: bytes = file.read((self.size + 1) // 2)
        self.table = np.frombuffer(arr, dtype=np.uint8)

    def read(self, index: int) -> int:
        if index % 2 == 0:
            return self.table[index // 2] // 16
        else:
            return self.table[index // 2] % 16


    def generate_pruning_table(self) -> None:
        self.filled: int = 0
        self.step_rel: float = .1 if self.state_type== PruningTable.CS else .001
        self.step_abs: int = int(self.step_rel * self.size)
        self.step: float = 1
        if self.max_slices == 0:
            return
        print("Generating Pruning Table")
        start_time = time()
        if self.state_type == PruningTable.CS:
            self._gpt_cs()
        elif self.state_type == PruningTable.SQSQ:
            self._gpt_sqsq()
        print("Generation took", f"{time() - start_time:.2f}", "seconds")

    def _gpt_cs(self) -> None:
        print("Cube Shape")
        print("Maximum Slice Depth:", self.max_slices)
        print("Table Size:", self.size)
        self.slice_depth: int = 0
        opened: list[int] = [Square1().get_int()]
        while opened:
            print("Check and write states for slice depth", self.slice_depth)
            closed: list[int] = []
            while opened:
                sq1: int = opened.pop()
                if self._write(StateCS(Square1(sq1)).get_index(), self.slice_depth) and self.slice_depth < self.max_slices:
                    closed.append(sq1)

            if closed and (self.filled < self.size):
                self.slice_depth += 1
                print("Generate states for slice depth", self.slice_depth)
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
        print("Maximum slice depth", self.slice_depth)

    def _gpt_sqsq(self) -> None:
        print("Square Square")
        print("Maximum Slice Depth:", self.max_slices)
        print("Table Size:", self.size)
        self.slice_depth: int = 0
        opened: np.ndarray = np.array([[Square1().get_int()]], dtype=np.uint64)

        while opened.size:
            print("Check and write states for slice depth", self.slice_depth)
            closed: list[int] = []
            with get_context("spawn").Pool(6) as pool:
                for states in pool.imap_unordered(_gs_sqsq, opened, chunksize=10):
                    for state in states:
                        if self._write(state.get_index(), self.slice_depth):
                            for index in state.get_symmetric_indecies():
                                self._write(index, self.slice_depth)
                            if self.slice_depth < self.max_slices:
                                closed.append(state.square1.get_int())
                    if self.filled == self.size:
                        break

            opened = np.empty(0)
            if closed and (self.filled < self.size):
                self.slice_depth += 1
                print("Generate states for slice depth", self.slice_depth)
                closed_arr: np.ndarray = np.array(closed, dtype=np.uint64)
                closed = []
                opened = np.empty((len(closed_arr), 16), dtype=np.uint64)

                with get_context("spawn").Pool(6) as pool:
                    index: int = 0
                    step = 0.1
                    pr = step
                    for result in pool.imap_unordered(_gnc_sqsq, closed_arr, chunksize=200):
                        opened[index] = result
                        index += 1
                        while pr <= float(index) / len(closed_arr):
                            print(f"{pr:.0%}", "of states generated")
                            pr += step
        print("Maximum slice depth", self.slice_depth)


    def _get_filename(self) -> str:
        if self.state_type == PruningTable.CS:
            return "pruning_table_cs.bin"
        elif self.state_type == PruningTable.SQSQ:
            return "pruning_table_sqsq.bin"
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

    def _increase_fill(self) -> None:
        self.filled += 1
        while self.filled >= self.step * self.step_abs:
            if self.state_type == PruningTable.CS:
                print(f"{self.step * self.step_rel:.0%}", "filled")
            else:
                print(f"{self.step * self.step_rel:.1%}", "filled")
            self.step += 1

# generates states for a square 1
def _gs_sqsq(sq1s: np.ndarray) -> list[StateSqSq]:
    states: list[StateSqSq] = []
    for sq1 in sq1s:
        states.append(StateSqSq(Square1(sq1)))
    return states

# gets next cubes for square square
def _gnc_sqsq(sq1: int) -> np.ndarray:
    sq1s: np.ndarray = np.empty(16, dtype=np.uint64)
    square1: Square1 = Square1(sq1)
    turns: list[tuple[int, int]] = square1.get_unique_turns_sq_sq()
    for i in range(len(turns)):
        square1.turn_layers(turns[i])
        square1.turn_slice()
        sq1s[i] = square1.get_int()
        square1 = Square1(sq1)
    return sq1s