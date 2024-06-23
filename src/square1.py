
class Square1:
    def __init__(self) -> None:
        # cececece cececece
        # ececcece ceceecec
        # starts on U at BR, goes cw
        # continues on D at FL, goes ccw
        self.pieces: list[int] = [i for i in range(16)]

    # returns False if Slice is not possible
    # returns True if Slice is successful
    def slice(self) -> bool:
        n: int = 0
        # gets start index of slice
        start: int = 0
        while n < 5:
            if self.pieces[start] % 2 == 0:
                # adds 2 to n if corner
                n += 2
            else:
                # adds 1 to n if edge
                n += 1
            # increases start index
            start += 1
        # checks if n is too big to fit corner
        if n != 6:
            if self.pieces[start] % 2 == 0:
                return False
            else:
                n += 1
            start += 1

        n = 0
        # gets end index of slice
        end: int = len(self.pieces)
        while n < 5:
            if self.pieces[end - 1] % 2 == 0:
                # adds 2 to n if corner
                n += 2
            else:
                # adds 1 to n if edge
                n += 1
            # increases start index
            end -= 1
        # checks if n is too big to fit corner
        if n != 6:
            if self.pieces[end - 1] % 2 == 0:
                return False
            else:
                n += 1
            end -= 1
      
        # performs slice
        self.pieces[start:end] = self.pieces[end-1:start-1:-1]
        return True