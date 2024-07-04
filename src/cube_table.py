import os

import numpy as np

class CubeTable:
    def __init__(self, name: str, size: int = 2000) -> None:
        self.name = name
        self.size: int = size * 125000 # size in MB * 1 MB / 8
        self.tab: int = 0
        self.index: int = 0
        self.table: np.ndarray = np.empty(self.size, dtype=np.uint64)
        pass

    def __bool__(self) -> bool:
        return self.tab > 0 or self.index > 0

    def __len__(self) -> int:
        return self.tab * self.size + self.index

    def read(self) -> np.ndarray:
        if self.index != 0:
            index: int = self.index
            self.index = 0
            return self.table[:index]
        else:
            if not self._read_file():
                raise LookupError
            return self.table

    def write(self, value: int) -> None:
        self.table[self.index] = value
        self.index += 1
        if self.index == self.size:
            self._write_file()
            self.index = 0

    def clear(self) -> None:
        while self.tab > 0:
            self.tab -= 1
            os.remove(self._get_tab_name())
        self.index = 0

    def _read_file(self) -> bool:
        if self.tab > 0:
            print("Reading file", self._get_tab_name())
            self.tab -= 1
            with open(self._get_tab_name(), "rb") as file:
                arr: bytes = file.read()
            self.table = np.frombuffer(arr, dtype=np.uint64)
            os.remove(self._get_tab_name())
            return True
        return False

    def _write_file(self) -> None:
        print("Writing file", self._get_tab_name())
        arr: bytes = self.table.tobytes()
        with open(self._get_tab_name(), "wb") as file:
            file.write(arr)
        self.tab += 1

    def _get_tab_name(self) -> str:
        return "temp/" + self.name + "_" + str(self.tab) + ".bin"