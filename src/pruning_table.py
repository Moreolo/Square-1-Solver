from multiprocessing import Lock, Pool

import numpy as np

from square1 import Square1
from state_sq_sq import StateSqSq
from state_cs import StateCS

class PruningTable:
    CS: int = 0
    SQSQ: int = 1

    def __init__(self, state_type: int = CS) -> None:
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
        self.filled: int = 0
        self.step: float = .1 if self.state_type == PruningTable.CS else .001
        self.print: float = self.step

    def write_file(self) -> None:
        arr: bytes = bytes(self.table)
        with open(self._get_filename(), "wb") as file:
            file.write(arr)

    def read_file(self) -> None:
        with open(self._get_filename(), "rb") as file:
            arr: bytes = file.read((self.size + 1) // 2)
        self.table = np.array(arr, dtype=np.uint8)

    def read(self, index: int) -> int:
        if index % 2 == 0:
            return self.table[index // 2] // 16
        else:
            return self.table[index // 2] % 16


    def generate_pruning_table(self) -> None:
        if self.max_slices == 0:
            return
        print("Generating Pruning Table")
        if self.state_type == PruningTable.CS:
            self._gpt_cs()
        elif self.state_type == PruningTable.SQSQ:
            self._gpt_sqsq()

    def _gpt_cs(self) -> None:
        print("Cube Shape")
        print("Maximum Slice Depth:", self.max_slices)
        print("Table Size:", self.size)
        self.slice_depth: int = 0
        opened: list[int] = [Square1().get_int()]

        while len(opened) > 0:
            print("Check and write states for slice depth", self.slice_depth)
            closed: list[int] = []
            while len(opened) > 0:
                sq1: int = opened.pop()
                if self._write(StateCS(Square1(sq1)).get_index(), self.slice_depth) and self.slice_depth < self.max_slices:
                    closed.append(sq1)
            if len(closed) > 0:
                self.slice_depth += 1
                print("Generate states for slice depth", self.slice_depth)
                while len(closed) > 0:
                    sq1: int = closed.pop()
                    for flip_l in range(2):
                        for mirror in range(2):
                            base: Square1 = Square1(sq1)
                            if flip_l:
                                base.flip_layers()
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
        
        while len(opened) > 0:
            print("Check and write states for slice depth", self.slice_depth)
            closed: list[int] = []
            for arr in opened:
                result = self._cwi_sqsq(arr)
                for sq1 in result:
                    closed.append(sq1)
            opened = np.empty(0)
            if len(closed) > 0:
                self.slice_depth += 1
                print("Generate states for slice depth", self.slice_depth)
                closed_arr: np.ndarray = np.array(closed, dtype=np.uint64)
                closed = []
                opened = np.empty((len(closed_arr), 128), dtype=np.uint64)

                with Pool(6) as pool:
                    index: int = 0
                    for result in pool.imap_unordered(self._gnc_sqsq, closed_arr, chunksize=10):
                        opened[index] = result
                        index += 1
        print("Maximum slice depth", self.slice_depth)

    def _cwi_sqsq(self, sq1s: np.ndarray) -> list[int]:
        closed: list[int] = []
        for sq1 in sq1s:
            state: StateSqSq = StateSqSq(Square1(sq1))
            if self._write(state.get_index(), self.slice_depth):
                for index in state.get_symmetric_indecies():
                    self._write(index, self.slice_depth)
                if self.slice_depth < self.max_slices:
                    closed.append(sq1)
        return closed

    def _gnc_sqsq(self, sq1: int) -> np.ndarray:
        sq1s: np.ndarray = np.empty(128, dtype=np.uint64)
        square1: Square1 = Square1(sq1)
        turns: list[tuple[int, int]] = square1.get_all_turns_sq_sq()
        for flip_c in range(2):
            for mirror in range(2):
                for i in range(len(turns)):
                    if flip_c:
                        square1.flip_colors()
                    if mirror:
                        square1.mirror_layers(8)
                    square1.turn_layers(turns[i])
                    square1.turn_slice()
                    sq1s[i * 4 + mirror * 2 + flip_c] = square1.get_int()
                    square1 = Square1(sq1)
        return sq1s


    def print_table(self) -> None:
        for slice_count in self.table:
            print(slice_count // 16, slice_count % 16)

    def _get_filename(self) -> str:
        if self.state_type == PruningTable.CS:
            return "pruning_table_cs.bin"
        elif self.state_type == PruningTable.SQSQ:
            return "pruning_table_sqsq.bin"
        else:
            return "pruning_table_none.bin"

    def _write(self, index: int, value: int) -> bool:
        table_value: int = self.table[index // 2]
        if index % 2 == 0:
            left: int = table_value // 16
            if left == 15:
                right: int = table_value % 16
                self.table[index // 2] = value * 16 + right
                self._increase_fill()
                return True
        else:
            right: int = table_value % 16
            if right == 15:
                left: int = table_value // 16
                self.table[index // 2] = left * 16 + value
                self._increase_fill()
                return True
        return False

    def _increase_fill(self) -> None:
        self.filled += 1
        while self.print <= float(self.filled) / self.size:
            print(f"{self.print:.1%}", "filled")
            self.print += self.step