import numpy as np

from square1 import Square1
from state_sq_sq import StateSqSq
from state_cs import StateCS

class PruningTable:
    NONE: int = 0
    CS: int = 1
    SQSQ: int = 2

    def __init__(self, state: str = "cs") -> None:
        self.state_type = PruningTable.NONE
        self.size = 0
        if state[0] == "s":
            self.state_type = PruningTable.SQSQ
            self.size = StateSqSq.size
        elif state[0] == "c":
            self.state_type = PruningTable.CS
            self.size = StateCS.size

        self.table: np.ndarray = np.full((self.size + 1) // 2, 255, dtype=np.uint8)
        self.filled: int = 0
        self.step: float = .1
        self.print: float = self.step

    def write_file(self) -> None:
        arr: bytes = bytes(self.table)
        with open("pruning_table.bin", "wb") as file:
            file.write(arr)

    def read_file(self) -> None:
        with open("pruning_table.bin", "rb") as file:
            arr: bytes = file.read((self.size + 1) // 2)
        self.table = np.array(arr, dtype=np.uint8)

    def read(self, index) -> int:
        if index % 2 == 0:
            return self.table[index // 2] // 16
        else:
            return self.table[index // 2] % 16

    def generate_pruning_table(self) -> None:
        square1 = Square1()


    def _write(self, index: int, value: int) -> None:
        table_val: int = self.table[index // 2]
        left: int = table_val // 16
        right: int = table_val % 16
        if index % 2 == 0:
            if left == 15:
                self.table[index // 2] = value * 16 + right
                self._increase_fill()
        else:
            if right == 15:
                self.table[index // 2] = left * 16 + value
                self._increase_fill()

    def _increase_fill(self) -> None:
        self.filled += 1
        while self.print <= float(self.filled) / self.size:
            print(f"{self.print:.0%}", "filled")
            self.print += self.step