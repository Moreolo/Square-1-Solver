class Square1:
    def __init__(self, pieces: list[int] = [i for i in range(16)]) -> None:
        # starts on U at FL, goes cw
        # continues on D at BR, goes ccw
        self.pieces: list[int] = pieces

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
        for piece in self.pieces:
            if piece < 8:
                piece = (piece - cycle[0]) % 8
            else:
                piece = (piece - cycle[1]) % 8 + 8

    def flip_colors(self) -> None:
        for piece in self.pieces:
            piece = 14 - piece
            if piece == 7 or piece < 0:
                piece += 8

    def flip_layers(self) -> None:
        self.pieces = self.pieces[::-1]

    def mirror_layers(self) -> None:
        # calculates the pieces on the up layer
        up_turns: int = 0
        angle: int = 0
        while angle < 12:
            angle += self.get_angle(up_turns)
            up_turns += 1
        self.pieces[:up_turns] = self.pieces[:up_turns][::-1]
        self.pieces[up_turns:] = self.pieces[up_turns:][::-1]
        for piece in self.pieces:
            piece = (piece + 4) % 8 + 8

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
        turns: list[tuple[int, int]] = []
        if self.pieces[0] % 2 != self.pieces[-1] % 2:
            # same alignment
            for i in range(0, 8, 2):
                for j in range(0, 8, 2):
                    turns.append((i + 1, j))
                    turns.append((i, j + 1))
        else:
            # different alignment
            for i in range(0, 8, 2):
                for j in range(0, 8, 2):
                    turns.append((i ,j))
                    turns.append((i + 1, j + 1))
        return turns

    def get_unique_turns_sq_sq(self) -> list[tuple[int, int]]:
        if self.pieces[0] % 2 != self.pieces[-1] % 2:
            # same alignment
            return [(1, 0), (5, 0), (3, 0), (7, 0),
                    (0, 1), (0, 5), (2, 1), (6, 1),
                    (1, 2), (1, 6), (7, 2), (7, 6),
                    (0, 3), (0, 7), (2, 7), (6, 7)]
        else:
            # different alignment
            top_aligned: bool = self.pieces[0] % 2 == 0
            return [(0, 0), (4, 0), (2, 0), (6, 0),
                    (1, 1), (5, 1) if top_aligned else (1, 5), (3, 1), (7, 1),
                    (0, 2), (0, 6), (2, 2), (2, 6),
                    (1, 3), (1, 7), (7, 7), (7, 3) if top_aligned else (3, 7)]

    def solve_auf(self) -> None:
        self.turn_layers((self.pieces.index(0), self.pieces.index(8) - 8))

    def get_angle(self, index: int) -> int:
        return 2 - (self.pieces[index] % 2)
            