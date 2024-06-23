
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
        n: int = 0
        # gets start index of slice
        start: int = 0
        while n < 5:
            if self.is_corner(start):
                # adds 2 to n if corner
                n += 2
            else:
                # adds 1 to n if edge
                n += 1
            # increases start index
            start += 1
        # checks if n is too big to fit corner
        if n != 6:
            if self.is_corner(start):
                return False
            else:
                n += 1
            start += 1

        n = 0
        # gets end index of slice
        end: int = len(self.pieces)
        while n < 5:
            if self.is_corner(end - 1):
                # adds 2 to n if corner
                n += 2
            else:
                # adds 1 to n if edge
                n += 1
            # increases start index
            end -= 1
        # checks if n is too big to fit corner
        if n != 6:
            if self.is_corner(end - 1):
                return False
            else:
                n += 1
            end -= 1
      
        # performs slice
        self.pieces[start:end] = self.pieces[end-1:start-1:-1]
        return True

    # turns the layers
    # cycles the pieces of the layers turn times to the right
    def turn_layers(self, turn: tuple[int, int]) -> None:
        up_turns: int = 0
        angle: int = 0
        while angle < 12:
            if self.is_corner(up_turns):
                angle += 2
            else:
                angle += 1
            up_turns += 1
        self.pieces[:up_turns] = self.pieces[up_turns-turn[0]:up_turns] + self.pieces[:up_turns-turn[0]]
        self.pieces[up_turns:] = self.pieces[16-turn[1]:16] + self.pieces[up_turns:16-turn[1]]

    def generate_turns(self) -> None:
        pass

    def is_corner(self, index) -> bool:
        return self.pieces[index] % 2 == 0
            