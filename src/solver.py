from square1 import Square1
from state_cs import StateCS
from state_sq_sq import StateSqSq
from pruning_table import PruningTable as Table

class Solver:
    def __init__(self) -> None:
        self.table_cs = Table(state_type=Table.CS)
        self.table_sqsq = Table(state_type=Table.SQSQ)
        self.table_cs.read_file()
        self.table_sqsq.read_file()

    def solve(self, square1: Square1, bar_solved: bool) -> list[tuple[int, int]]:
        human_readables: list[tuple[int, int]] = []
        slices: int = self._get_slices_cs(square1.get_copy())
        print("CSP solvable in", slices)
        while slices > 0:
            turn: tuple[int, int] = self._get_next_turn_cs(square1, slices)
            human_readables.append(square1.get_human_readable(turn))
            square1.turn_layers(turn)
            square1.turn_slice()
            bar_solved = not bar_solved
            slices -= 1
        slices: int = self._get_slices_sqsq(square1.get_copy())
        print("Square Square solvable in", slices)
        while slices > 1:
            turn: tuple[int, int] = self._get_next_turn_sqsq(square1, slices)
            human_readables.append(square1.get_human_readable(turn))
            square1.turn_layers(turn)
            square1.turn_slice()
            bar_solved = not bar_solved
            slices -= 1
        turn: tuple[int, int] = self._get_next_turn_sqsq(square1, slices)
        human_readable = square1.get_human_readable(turn)
        square1.turn_layers(turn)
        last_human_readables: list[tuple[int, int]] = square1.solve_last_slice(human_readable, bar_solved)
        for last_human_readable in last_human_readables:
            human_readables.append(last_human_readable)
        return human_readables

    def _get_next_turn_cs(self, square1: Square1, slices: int) -> tuple[int, int]:
        for turn in square1.get_unique_turns():
            copy: Square1 = square1.get_copy()
            copy.turn_layers(turn)
            copy.turn_slice()
            if self._get_slices_cs(copy) < slices - 1:
                raise ValueError
            elif self._get_slices_cs(copy) == slices - 1:
                return turn
        raise ValueError

    def _get_slices_cs(self, square1: Square1) -> int:
        return self.table_cs.read(StateCS(square1).get_index())
    
    def _get_next_turn_sqsq(self, square1: Square1, slices: int) -> tuple[int, int]:
        for turn in square1.get_unique_turns_sq_sq():
            copy: Square1 = square1.get_copy()
            copy.turn_layers(turn)
            copy.turn_slice()
            if self._get_slices_sqsq(copy) < slices - 1:
                raise ValueError
            elif self._get_slices_sqsq(copy) == slices - 1:
                return turn
        raise ValueError

    def _get_slices_sqsq(self, square1: Square1) -> int:
        return self.table_sqsq.read(StateSqSq(square1).get_index())