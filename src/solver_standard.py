from square1 import Square1
from state_cs import StateCS
from state_sq_sq import StateSqSq
from pruning_table import PruningTable as Table

class SolverStandard:
    def __init__(self) -> None:
        self.table_cs = Table(state_type=Table.CS)
        self.table_sqsq = Table(state_type=Table.SQSQ)

    def solve(self, square1: Square1, bar_solved: bool) -> list[tuple[int, int]]:
        human_readables: list[tuple[int, int]] = []
        # calculates the slices required to solve csp
        slices: int = self._get_slices_cs(square1.get_copy())
        print("CSP solvable in", slices)
        while slices > 0:
            # gets the next turn with less required slices
            turn: tuple[int, int] = self._get_next_turn_cs(square1, slices)
            # appends the turn to the solution
            human_readables.append(square1.get_human_readable(turn))
            # turns layers and slices
            square1.turn_layers(turn)
            square1.turn_slice()
            # flips bar
            bar_solved = not bar_solved
            # cube now requires one slice less
            slices -= 1
        # calculates the slices required to solve sqsq
        slices: int = self._get_slices_sqsq(square1.get_copy())
        print("Square Square solvable in", slices)
        while slices > 0:
            # gets the next turn with less required slices
            turn: tuple[int, int] = self._get_next_turn_sqsq(square1, slices)
            # appends the turn to the solution
            human_readables.append(square1.get_human_readable(turn))
            # turns layers
            square1.turn_layers(turn)
            # slices if not at last slice
            if slices > 1:
                square1.turn_slice()
                # flips bar
                bar_solved = not bar_solved
                # cube now requires one slice less
                slices -= 1
            else:
                break
        # solves the last slice and gets the last turns of the solution
        last_human_readables: list[tuple[int, int]] = square1.solve_last_slice(human_readables.pop(), bar_solved)
        # appends last turns to solution
        for last_human_readable in last_human_readables:
            human_readables.append(last_human_readable)
        return human_readables

    def _get_next_turn_cs(self, square1: Square1, slices: int) -> tuple[int, int]:
        # gets all possible turns
        for turn in square1.get_unique_turns():
            # does the turn on a copied cube
            copy: Square1 = square1.get_copy()
            copy.turn_layers(turn)
            copy.turn_slice()
            # returns turn if slice count is less than current slice count
            if self._get_slices_cs(copy) < slices:
                return turn
        # raises error if lookup failed
        raise LookupError

    def _get_slices_cs(self, square1: Square1) -> int:
        # calculates the csp state of the cube and gets slice count from table with index from state
        return self.table_cs.read(StateCS(square1).get_index())
    
    def _get_next_turn_sqsq(self, square1: Square1, slices: int) -> tuple[int, int]:
        # gets all possible turns
        for turn in square1.get_unique_turns_sq_sq():
            # does the turn on a copied cube
            copy: Square1 = square1.get_copy()
            copy.turn_layers(turn)
            copy.turn_slice()
            # returns turn if slice count is less than current slice count
            if self._get_slices_sqsq(copy) < slices:
                return turn
        # raises error if lookup failed
        raise LookupError

    def _get_slices_sqsq(self, square1: Square1) -> int:
        # calculates the sqsq state of the cube and gets slice count from table with index from state
        return self.table_sqsq.read(StateSqSq(square1).get_index())