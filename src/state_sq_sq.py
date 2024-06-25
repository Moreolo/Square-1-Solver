from square1 import Square1

class StateSqSq:
    # c1 < c2 < c3 < c4
    # c1 c2 c3 c4
    #  -  0  0  0
    #
    # c3 c2 c4 c1
    #  -  1  0  3
    #
    # c4 c3 c2 c1
    #  -  1  2  3


    # 1 16 36 16 1

    def __init__(self, square1: Square1) -> None:
        self.square1: Square1 = Square1(square1.pieces[:])
        # finds the orientation case
        # gets the orientation of the corners on the up layer
        orientations: list[bool] = []
        alignment: int = self.square1.pieces[0] % 2
        blacks: int = 0
        for i in range(alignment, 8, 2):
            is_black: bool = self.square1.pieces[i] < 8
            # counts the black corners in the up layer
            if is_black:
                blacks += 1
            orientations.append(is_black)
        # swaps layers if there are fewer black pieces than white pieces
        if blacks < 2:
            self.swap_layers()
            for orientation in orientations:
                orientation = not orientation

        case: int = 0
        up_rot: int = 0
        try:
            up_rot = orientations.index(False)
        except:
            pass
        else:
            if up_rot == 0 and not orientations[-1]:
                up_rot = 3
                case = 2
            elif not orientations[(up_rot + 1) % 4]:
                case = 2
            elif not orientations[(up_rot + 2) % 4]:
                case = 3
            else:
                case = 1

        orientations = []
        alignment = self.square1.pieces[8] % 2
        for i in range(8 + alignment, 16, 2):
            orientations.append(self.square1.pieces[i] < 8)
        try:
            down_rot = orientations.index(True)
        except:
            pass
        else:
            if case > 1:
                if down_rot == 0 and orientations[-1]:
                    down_rot = 3
                elif not orientations[down_rot + 1]:
                    case += 2
        # rotate layers
        self.rotate_layers(up_rot, down_rot)
        permutation_corners_black = 0
        permutation_corners_white = 0
        orientation_corners = 0
        permutation_edges = 0

    def rotate_layers(self, up_rot: int, down_rot: int) -> None:
        self.square1.turn_layers((up_rot * 2, down_rot * 2))

    def swap_layers(self) -> None:
        for piece in self.square1.pieces:
            piece = 18 - piece
            if piece > 15 or piece < 11:
                piece -= 8

            if piece == 0:
                piece = 10
            elif piece == 1:
                piece = 9
            elif piece == 2:
                piece = 8
            elif piece == 3:
                piece = 15
            elif piece == 4:
                piece = 14
            elif piece == 5:
                piece = 13
            elif piece == 6:
                piece = 12
            elif piece == 7:
                piece = 11
            elif piece == 8:
                piece = 2
            elif piece == 9:
                piece = 1
            elif piece == 10:
                piece = 0
            elif piece == 11:
                piece = 7

    def cycle_layers(self) -> None:
        pass