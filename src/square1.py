import numpy as np

sqsq_unique_turns_ba: list[tuple[int, int]] = [(1, 0), (5, 0), (3, 0), (7, 0),
                                               (0, 1), (0, 5), (2, 1), (6, 1),
                                               (1, 2), (1, 6), (7, 2), (7, 6),
                                               (0, 3), (0, 7), (2, 7), (6, 7)]
sqsq_unique_turns_ua: list[tuple[int, int]] = [(0, 0), (4, 0), (2, 0), (6, 0),
                                               (1, 1), (5, 1), (3, 1), (7, 1),
                                               (0, 2), (0, 6), (2, 2), (2, 6),
                                               (1, 3), (1, 7), (7, 7), (7, 3)]
sqsq_unique_turns_da: list[tuple[int, int]] = [(0, 0), (4, 0), (2, 0), (6, 0),
                                               (1, 1), (1, 5), (3, 1), (7, 1),
                                               (0, 2), (0, 6), (2, 2), (2, 6),
                                               (1, 3), (1, 7), (7, 7), (3, 7)]

sqsq_all_turns_a: list[tuple[int, int]] = [(1, 0), (5, 0), (3, 0), (7, 0),
                                           (1, 4), (5, 4), (3, 4), (7, 4),
                                           (0, 1), (4, 1), (2, 1), (6, 1),
                                           (0, 5), (4, 5), (2, 5), (6, 5),
                                           (1, 2), (5, 2), (3, 2), (7, 2),
                                           (1, 6), (5, 6), (3, 6), (7, 6),
                                           (0, 3), (4, 3), (2, 3), (6, 3),
                                           (0, 7), (4, 7), (2, 7), (6, 7)]
sqsq_all_turns_m: list[tuple[int, int]] = [(0, 0), (4, 0), (2, 0), (6, 0),
                                           (0, 4), (4, 4), (2, 4), (6, 4),
                                           (1, 1), (5, 1), (3, 1), (7, 1),
                                           (1, 5), (5, 5), (3, 5), (7, 5),
                                           (0, 2), (4, 2), (2, 2), (6, 2),
                                           (0, 6), (4, 6), (2, 6), (6, 6),
                                           (1, 3), (5, 3), (3, 3), (7, 3),
                                           (1, 7), (5, 7), (3, 7), (7, 7)]

class Square1:
    def __init__(self, pieces: (list[int] | int | np.uint64) = [i for i in range(16)]) -> None:
        # starts on U at FL, goes cw
        # continues on D at BR, goes ccw
        if type(pieces) is np.uint64:
            pieces = int(pieces)
        if type(pieces) is int:
            self.pieces: list[int] = []
            for i in range(16):
                self.pieces.insert(0, pieces % 16)
                pieces //= 16
        elif type(pieces) is list:
            self.pieces: list[int] = pieces

    def get_int(self) -> int:
        num: int = 0
        for piece in self.pieces:
            num *= 16
            num += piece
        return num

    def get_copy(self) -> "Square1":
        return Square1(self.pieces[:])

    # turns the slice
    # returns False if slice is not possible
    # returns True if slice is successful
    def turn_slice(self) -> None:
        angle: int = 0
        # gets start index of slice
        start: int = 0
        while angle < 6:
            angle += self.get_angle(start)
            start += 1
        # checks if angle is too big to fit corner
        if angle > 6:
            raise OverflowError

        angle = 0
        # gets end index of slice
        end: int = len(self.pieces)
        while angle < 6:
            angle += self.get_angle(end - 1)
            end -= 1
        # checks if angle is too big to fit corner
        if angle > 6:
            raise OverflowError

        # performs slice
        self.pieces[start:end] = self.pieces[end-1:start-1:-1]

    # turns the layers
    # cycles the pieces of the layers turn times to the left
    def turn_layers(self, turn: tuple[int, int]) -> None:
        if turn[0] == 0 and turn[1] == 0:
            return
        # calculates the pieces on the up layer
        up_turns: int = 0
        angle: int = 0
        while angle < 12:
            angle += self.get_angle(up_turns)
            up_turns += 1
        # performs the layer turns
        self.pieces[:up_turns] = self.pieces[turn[0]:up_turns] + self.pieces[:turn[0]]
        self.pieces[up_turns:] = self.pieces[up_turns:][turn[1]:] + self.pieces[up_turns:][:turn[1]]

    def cycle_colors(self, cycle: tuple[int, int]) -> None:
        if cycle[0] == 0 and cycle[1] == 0:
            return
        for i in range(16):
            if self.pieces[i] < 8:
                self.pieces[i] = (self.pieces[i] - cycle[0] * 2) % 8
            else:
                self.pieces[i] = (self.pieces[i] - cycle[1] * 2) % 8 + 8

    def flip_colors(self) -> None:
        for i in range(16):
            self.pieces[i] = 14 - self.pieces[i]
            if self.pieces[i] == 7 or self.pieces[i] < 0:
                self.pieces[i] += 8

    def flip_layers(self) -> None:
        self.pieces = self.pieces[::-1]

    def mirror_layers(self, up_turns: int = -1) -> None:
        # calculates the pieces on the up layer if not defined
        if up_turns == -1:
            up_turns = 0
            angle: int = 0
            while angle < 12:
                angle += self.get_angle(up_turns)
                up_turns += 1
        # mirrors cube
        self.pieces[:up_turns] = self.pieces[:up_turns][::-1]
        self.pieces[up_turns:] = self.pieces[up_turns:][::-1]
        for i in range(16):
            if self.pieces[i] < 8:
                self.pieces[i] = (self.pieces[i] + 4) % 8 + 8
            else:
                self.pieces[i] = (self.pieces[i] + 4) % 8

    def get_unique_turns(self) -> list[tuple[int, int]]:
        turn: int = 0
        angle: int = 0
        # gets the potential angles on the up layer
        pot_angles: list[int] = []
        pot_turns: list[int] = []
        while angle < 6:
            pot_angles.append(angle)
            pot_turns.append(turn)
            angle += self.get_angle(turn)
            turn += 1
        # gets the valid angles
        up_ats: list[tuple[int, int, int]] = []
        while angle < 12:
            try:
                pot_angle: int = angle - 6
                index = pot_angles.index(pot_angle)
            except:
                pass
            else:
                up_ats.append((pot_angle, pot_turns[index], turn))
            angle += self.get_angle(turn)
            turn += 1

        up_turns_no: int = turn
        turn = 0
        angle = 0
        # gets the potential angles on the down layer
        pot_angles = []
        pot_turns = []
        while angle < 6:
            pot_angles.append(angle)
            pot_turns.append(turn)
            angle += self.get_angle(up_turns_no + turn)
            turn += 1
        # gets the valid angles and gets unique turn combinations
        turns: list[tuple[int, int]] = []
        while angle < 12:
            try:
                pot_angle: int = angle - 6
                index = pot_angles.index(pot_angle)
            except:
                pass
            else:
                for up_at in up_ats:
                    if up_at[0] + pot_angle < 7:
                        turns.append((up_at[1], pot_turns[index]))
                    else:
                        turns.append((up_at[2], turn))
                    if up_at[0] < pot_angle:
                        turns.append((up_at[1], turn))
                    else:
                        turns.append((up_at[2], pot_turns[index]))
            angle += self.get_angle(up_turns_no + turn)
            turn += 1
        return turns

    def get_all_turns_sq_sq(self) -> list[tuple[int, int]]:
        if self.pieces[0] % 2 != self.pieces[-1] % 2:
            return sqsq_all_turns_a
        else:
            return sqsq_all_turns_m

    def get_unique_turns_sq_sq(self) -> list[tuple[int, int]]:
        if self.pieces[0] % 2 != self.pieces[-1] % 2:
            # same alignment
            return sqsq_unique_turns_ba
        elif self.pieces[0] % 2 == 0:
            # up aligned
            return sqsq_unique_turns_ua
        else:
            # down aligned
            return sqsq_unique_turns_da

    def get_angle(self, index: int) -> int:
        return 2 - (self.pieces[index] % 2)

    def get_human_readable(self, turn: tuple[int, int]) -> tuple[int, int]:
        up_angle: int = 0
        turns: int = 0
        while turns < turn[0]:
            up_angle += self.get_angle(turns)
            turns += 1
        down_angle: int = up_angle
        while down_angle < 12:
            down_angle += self.get_angle(turns)
            turns += 1
        down_angle = 0
        turns_offset: int = turns
        turns = 0
        while turns < turn[1]:
            down_angle += self.get_angle(turns + turns_offset)
            turns += 1

        up_angle *= -1
        if up_angle < -5:
            up_angle += 12
        if down_angle > 6:
            down_angle -= 12
        return up_angle, down_angle

    # starts right before the last slice
    # solves bar flip and layer flip
    # returns list of human readables starting at the layer turn before the slice
    def solve_last_slice(self, human_readable: tuple[int, int], bar_solved: bool) -> list[tuple[int, int]]:
        hrs: list[tuple[int, int]] = []
        if bar_solved:
            if abs(human_readable[0]) >= abs(human_readable[1]):
                hrs.append(_add_human_readables(human_readable, (6, 0)))
                self.turn_layers((4, 0))
            else:
                hrs.append(_add_human_readables(human_readable, (0, 6)))
                self.turn_layers((0, 4))
            self.turn_slice()
            if self.pieces[0] < 8:
                hrs.append((0, 6))
                self.turn_layers((0, 4))
            else:
                hrs.append((6, 0))
                self.turn_layers((4, 0))
            self.turn_slice()
        else:
            if self.pieces[0] < 8:
                hrs.append(human_readable)
            else:
                hrs.append(_add_human_readables(human_readable, (6, 6)))
                self.turn_layers((4, 4))
            self.turn_slice()
        abf_turn: tuple[int, int] = (self.pieces.index(0), self.pieces.index(8) - 8)
        hrs.append(self.get_human_readable(abf_turn))
        self.turn_layers(abf_turn)
        return hrs

def _add_human_readables(hr1: tuple[int, int], hr2: tuple[int, int]) -> tuple[int, int]:
    up_angle = hr1[0] + hr2[0]
    down_angle = hr1[1] + hr2[1]
    if up_angle < 5:
        up_angle += 12
    elif up_angle > 6:
        up_angle -= 12
    if down_angle < 5:
        down_angle += 12
    elif down_angle > 6:
        down_angle -= 12
    return up_angle, down_angle