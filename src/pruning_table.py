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
        print("Generating Pruning Table")
        self._print_state()
        if self.max_slices == 0:
            return
        open: list[tuple[(StateCS | StateSqSq), int]] = [(self._create_state(), 0)]
        self._write(open[0][0].get_index(), 0)
        slice_depth: int = 0
        while len(open) > 0:
            state, slices = open.pop(0)
            slices += 1
            if slices > slice_depth:
                slice_depth = slices
                print("Slice Depth:", slice_depth)
            # Gets the unique turns for the State and Cube
            turns: list[tuple[int, int]]
            if self.state_type == PruningTable.SQSQ:
                turns = state.square1.get_unique_turns_sq_sq()
            else:
                turns = state.square1.get_unique_turns()
            for turn in turns:
                # Turns and slices on a copied Cube
                next_cube: Square1 = state.square1.get_copy()
                next_cube.turn_layers(turn)
                next_cube.turn_slice()
                # Reduces Cube to State and gets index
                next_state = self._create_state(next_cube)
                index: int = next_state.get_index()
                # Tries to write
                # Appends to open if successful and still in slice limit
                if self._write(index, slices) and slices < self.max_slices:
                    open.append((next_state, slices))

    def print_table(self) -> None:
        for slice_count in self.table:
            print(slice_count // 16, slice_count % 16)

    def _print_state(self) -> None:
        if self.state_type == PruningTable.CS:
            print("Cube Shape")
        elif self.state_type == PruningTable.SQSQ:
            print("Square Square")
        print("Maximum Slice Depth:", self.max_slices)
        print("Table Size:", self.size)

    def _get_filename(self) -> str:
        if self.state_type == PruningTable.CS:
            return "pruning_table_cs.bin"
        elif self.state_type == PruningTable.SQSQ:
            return "pruning_table_sqsq.bin"
        else:
            return "pruning_table_none.bin"

    def _create_state(self, square1: Square1 = Square1()):
        if self.state_type == PruningTable.CS:
            return StateCS(square1)
        else:
            return StateSqSq(square1)

    def _write(self, index: int, value: int) -> bool:
        table_val: int = self.table[index // 2]
        left: int = table_val // 16
        right: int = table_val % 16
        if index % 2 == 0:
            if left == 15:
                self.table[index // 2] = value * 16 + right
                self._increase_fill()
                return True
        else:
            if right == 15:
                self.table[index // 2] = left * 16 + value
                self._increase_fill()
                return True
        return False

    def _increase_fill(self) -> None:
        self.filled += 1
        while self.print <= float(self.filled) / self.size:
            print(f"{self.print:.1%}", "filled")
            self.print += self.step