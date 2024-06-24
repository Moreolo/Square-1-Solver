
class Square1:
    def __init__(self) -> None:
        # cececece cececece
        # ceceecec ececcece
        # starts on U at FL, goes cw
        # continues on D at BR, goes ccw
        self.pieces: list[int] = [i for i in range(16)]

    # turns the slice
    # returns False if slice is not possible
    # returns True if slice is successful
    def turn_slice(self) -> bool:
        angle: int = 0
        # gets start index of slice
        start: int = 0
        while angle < 6:
            angle += self.get_angle(start)
            start += 1
        # checks if angle is too big to fit corner
        if angle > 6:
            return False

        angle = 0
        # gets end index of slice
        end: int = len(self.pieces)
        while angle < 6:
            angle += self.get_angle(end - 1)
            end -= 1
        # checks if angle is too big to fit corner
        if angle > 6:
            return False
      
        # performs slice
        self.pieces[start:end] = self.pieces[end-1:start-1:-1]
        return True

    # turns the layers
    # cycles the pieces of the layers turn times to the left
    def turn_layers(self, turn: tuple[int, int]) -> None:
        # calculates the pieces on the up layer
        up_turns: int = 0
        angle: int = 0
        while angle < 12:
            angle += self.get_angle(up_turns)
            up_turns += 1
        # performs the layer turns
        self.pieces[:up_turns] = self.pieces[turn[0]:up_turns] + self.pieces[:turn[0]]
        self.pieces[up_turns:] = self.pieces[up_turns:][turn[1]:] + self.pieces[up_turns:][:turn[1]]

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
            print(pot_angles, pot_turns)
        # gets the valid angles
        up_ats: list[tuple[int, int, int]] = []
        while angle < 12:
            try:
                pot_angle: int = angle - 6
                index = pot_angles.index(pot_angle)
            except:
                print(pot_angle)
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
        # gets the valid angles
        down_ats: list[tuple[int, int, int]]= []
        while angle < 12:
            try:
                pot_angle: int = angle - 6
                index = pot_angles.index(pot_angle)
            except:
                pass
            else:
                down_ats.append((pot_angle, pot_turns[index], turn))
            angle += self.get_angle(up_turns_no + turn)
            turn += 1
        
        print(up_ats)
        print(down_ats)
        # gets unique turn combinations
        turns: list[tuple[int, int]] = []
        for up_at in up_ats:
            for down_at in down_ats:
                if up_at[0] + down_at[0] < 7:
                    turns.append((up_at[1], down_at[1]))
                else:
                    turns.append((up_at[2], down_at[2]))
                if up_at[0] < down_at[0]:
                    turns.append((up_at[1], down_at[2]))
                else:
                    turns.append((up_at[2], down_at[1]))
        return turns

    def get_angle(self, index: int) -> int:
        if self.pieces[index] % 2 == 0:
            return 2
        return 1
            