from square1 import Square1

class StateSqSq:
    size: int = 4354560 # = 6 * 3! 3! 8! / 2
    max_slices: int = 9

    def __init__(self, square1: Square1) -> None:
        self.square1: Square1 = square1
        self.co: int = 0 # 6
        self.cp_black: int = 0 # 6 = 3!
        self.cp_white: int = 0 # 6 = 3!
        self.ep: int = 0 # 20160 = 8! / 2
        self.calculate_orientation()
        self.calculate_permutation()

    # index is in range [0, 4 354 560[
    def get_index(self) -> int:
        index: int = self.ep
        index = index * 6 + self.co
        index = index * 6 + self.cp_black
        index = index * 6 + self.cp_white
        return index

    # calculates the co case
    def calculate_orientation(self) -> None:
        # gets the orientation of the corners on the up layer
        orientations: list[bool] = []
        up_alignment: int = self.square1.pieces[0] % 2
        blacks: int = 0
        for i in range(up_alignment, 8, 2):
            is_black: bool = self.square1.pieces[i] < 8
            # counts the black corners in the up layer
            if is_black:
                blacks += 1
            orientations.append(is_black)
        # swaps layers if there are fewer black pieces than white pieces
        if blacks < 2:
            for piece in self.square1.pieces:
                piece = 14 - piece
                if piece == 7 or piece < 0:
                    piece += 8
            for orientation in orientations:
                orientation = not orientation

        # gets the co case of the up layer
        # and gets the rotation of the up layer
        up_rot: int = 0
        try:
            up_rot = orientations.index(False)
        except:
            pass
        else:
            if up_rot == 0 and not orientations[-1]:
                up_rot = 3
                self.co = 2
            elif not orientations[(up_rot + 1) % 4]:
                self.co = 2
            elif not orientations[(up_rot + 2) % 4]:
                self.co = 3
            else:
                self.co = 1

        # gets the orientation of the corners on the down layer
        orientations = []
        down_alignment: int = self.square1.pieces[8] % 2
        for i in range(8 + down_alignment, 16, 2):
            orientations.append(self.square1.pieces[i] < 8)
        # gets the co case for both layers
        # and gets the rotation of the down layer
        down_rot: int = 0
        try:
            down_rot = orientations.index(True)
        except:
            pass
        else:
            if self.co > 1:
                if down_rot == 0 and orientations[-1]:
                    down_rot = 3
                elif not orientations[down_rot + 1]:
                    self.co += 2
        # rotates the layers for EP
        self.square1.turn_layers((up_rot * 2 + up_alignment, down_rot * 2 + down_alignment))

    # calculates the piece permutation
    def calculate_permutation(self) -> None:
        # gets a reduced representation of the black and white corners and all edges
        black_corners: list[int] = []
        white_corners: list[int] = []
        edges: list[int] = []
        for piece in self.square1.pieces:
            if piece % 2 == 0:
                if piece < 8:
                    black_corners.append(piece // 2)
                else:
                    white_corners.append(piece // 2 - 4)
            else:
                edges.append((piece - 1) // 2)
        # cycles black and white pieces, so first occuring colored corner is the lowest
        # calculates permutation in the same iterations
        black_offset: int = black_corners[0]
        white_offset: int = white_corners[0]
        factor: int = 1
        for i in range(4):
            # cycle
            black_corners[i] = (black_corners[i] - black_offset) % 4
            white_corners[i] = (white_corners[i] - white_offset) % 4
            # permutation calculation
            if i > 1:
                factor *= (i - 1)
                higher_black: int = 0
                higher_white: int = 0
                for j in range(1, i):
                    if black_corners[j] > black_corners[i]:
                        higher_black += 1
                    if white_corners[j] > white_corners[i]:
                        higher_white += 1
                self.cp_black += higher_black * factor
                self.cp_white += higher_white * factor
        factor = 1
        for i in range(len(edges)):
            # cycle
            if edges[i] < 4:
                edges[i] = (edges[i] - black_offset) % 4
            else:
                edges[i] = (edges[i] - white_offset) % 4 + 4
            # permutation calculation
            if i > 0:
                factor *= i
                higher: int = 0
                for j in range(i):
                    if edges[j] > edges[i]:
                        higher += 1
                self.ep += higher * factor
        # divides by 2 because parity is even
        self.ep //= 2
        # cycles pieces for more state generation
        self.square1.cycle_colors((black_offset, white_offset))