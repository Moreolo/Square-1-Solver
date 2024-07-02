from functools import total_ordering
import heapq

from square1 import Square1
from state_cs import StateCS
from state_sq_sq import StateSqSq
from pruning_table import PruningTable as Table

@total_ordering
class AstarCSState:
    def __init__(self, f: int, g: int, turn: tuple[int, int], sq1: int, parent: "(AstarCSState | None)" = None) -> None:
        self.f = f
        self.g = g
        self.turn = turn
        self.sq1 = sq1
        self.parent = parent

    def __eq__(self, other: object) -> bool:
        if hasattr(other, "f"):
            return self.f == other.f # type: ignore
        else:
            return NotImplemented

    def __lt__(self, other: object) -> bool:
        if hasattr(other, "f"):
            return self.f < other.f # type: ignore
        else:
            return NotImplemented

class SolverAstar:
    def __init__(self) -> None:
        self.table_cs: Table = Table(state_type=Table.CS)
        self.table_sqsq: Table = Table(state_type=Table.SQSQ)

    def solve(self, square1: Square1, bar_solved: bool) -> list[tuple[int, int]]:
        human_readables: list[tuple[int, int]] = []
        # finds cs solution with lowest sqsq slice count after
        state = self._get_cs_solution_state(square1.get_int())
        # returns error if no solution was found
        if state is None:
            raise LookupError
        # writes turns to list
        turns: list[tuple[int, int]] = []
        while state.parent is not None:
            turns.append(state.turn)
            state = state.parent
        # reverses turns
        turns = turns[::-1]
        for turn in turns:
            # appends the turn to the solution
            human_readables.append(square1.get_human_readable(turn))
            # turns layers and slices
            square1.turn_layers(turn)
            square1.turn_slice()
            # flips bar
            bar_solved = not bar_solved

        # solves sqsq
        slices: int = self._get_slices_sqsq(square1.get_copy())
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

    def _get_cs_solution_state(self, sq1: int) -> (AstarCSState | None):
        depth: int = 0
        # inits solution and f to None
        solution: (AstarCSState | None) = AstarCSState(StateCS.max_slices + StateSqSq.max_slices + 1, 0, (0, 0), 0)
        # inits open list
        opened: list[AstarCSState] = []
        heapq.heappush(opened, AstarCSState(0, 0, (0, 0), sq1))
        while opened:
            # gets lowest f in open
            state = heapq.heappop(opened)
            # gets all possible turns
            turns: list[tuple[int, int]] = Square1(state.sq1).get_unique_turns()
            # removes (0, 0) if not the start
            if state.parent is not None:
                turns.pop(0)
            for turn in turns:
                # does the turn on a copied cube
                copy: Square1 = Square1(state.sq1)
                copy.turn_layers(turn)
                copy.turn_slice()
                # gets slices to solve cs
                slices: int = self._get_slices_cs(copy.get_copy())
                if slices == 0:
                    # state is possible solution
                    # calculates g and h of entire solution
                    g: int = state.g + 1
                    h: int = self._get_slices_sqsq(copy.get_copy())
                    if g + h < solution.f:
                        # sets new solution if f is better
                        solution = AstarCSState(g + h, g, turn, copy.get_int(), state)
                        print("Found solution with", solution.f, "slices")
                        print("Cube Shape:", g, "slices")
                        print("Square Square:", h, "slices")
                    if g >= solution.f or g >= 8:
                        # returns if solution can't be improved
                        return solution
                    else:
                        if g > depth:
                            depth = g
                            print("-- Searching", g, "slices deep")
                else:
                    # appends state to open
                    g: int = state.g + 1
                    heapq.heappush(opened, AstarCSState(g + slices, g, turn, copy.get_int(), state))
        return solution

    def _get_slices_cs(self, square1: Square1) -> int:
        # calculates the sqsq state of the cube and gets slice count from table with index from state
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