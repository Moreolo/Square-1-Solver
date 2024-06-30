from square1 import Square1

class StateSqSq:
    size: int = 3628800 # = 5 * 3! 3! 8! / 2
    max_slices: int = 9

    def __init__(self, square1: Square1) -> None:
        self.square1: Square1 = square1
        self.co: int = 0 # 6
        self.cp_black: int = 0 # 6 = 3!
        self.cp_white: int = 0 # 6 = 3!
        self.ep: int = 0 # 20160 = 8! / 2

        self.up_alignment: int = self.square1.pieces[0] % 2
        self.down_alignment: int = self.square1.pieces[8] % 2

        self.calculate_orientation()
        self.calculate_permutation()

    # index is in range [0, 3628800[
    def get_index(self) -> int:
        index: int = self.ep
        index = index * 5 + self.co
        index = index * 6 + self.cp_black
        index = index * 6 + self.cp_white
        return index

    # calculates the corner orientation case
    def calculate_orientation(self) -> None:
        # counts corner colors in the up layer
        black: bool = self._get_corner(0) < 8
        count: int = 1
        for i in range(1, 4):
            if self._get_corner(i) < 8 == black:
                count += 1
        # decides on co depending on count
        # flips if up layer has fewer black corners than white corners
        if count == 1:
            self.co = 1
            if black:
                self._flip_layers()
        elif count == 2:
            # checks if layer is opp case
            self.co = 2
            up_is_opp: bool = False
            if self._get_corner(2) < 8 == black:
                self.co += 1
                up_is_opp = True
            if self._get_corner(4) < 8 == self._get_corner(6) < 8:
                self.co += 1
            # flips opp case to down
            if self.co == 3 and up_is_opp:
                self._flip_layers()
        elif count == 3:
            self.co = 1
            if not black:
                self._flip_layers()
        else:
            self.co = 0
            if not black:
                self._flip_layers()

        # gets base rotation
        up_rot: int = 0
        down_rot: int = 0
        for i in range(4):
            if self._get_corner(i) > 7:
                up_rot = i
            if self._get_corner(4 + i) < 8:
                down_rot = i
        # corrects rotation
        if self.co == 2:
            if self._get_corner(0) > 7:
                up_rot = 0
            if self._get_corner(4) < 8:
                down_rot = 0
        elif self.co == 3:
            if self._get_corner(0) > 7:
                up_rot = 0
        # rotates layers
        self._turn_layers(up_rot, down_rot)
        # get combination of flip colors, flip layers, mirror layers
        # get possible rotations

    def calculate_permutation(self) -> None:
        # cycles lowest black corner and lowest white corner to front
        black_offset: int = -1
        white_offset: int = -1
        index: int = 0
        while black_offset == -1 or white_offset == -1:
            corner: int = self._get_corner(index) // 2
            if self._get_corner(index) < 4:
                if black_offset == -1:
                    black_offset = corner
            else:
                if white_offset == -1:
                    white_offset = corner - 4
        self.square1.cycle_colors((black_offset, white_offset))

        # calculates permutations
        blacks: list[int] = []
        whites: list[int] = []
        for i in range(8):
            if corner < 8:
                blacks.append(self._get_corner(i))
            else:
                whites.append(self._get_corner(i))
        factor: int = 1
        for i in range(2, 4):
            factor *= (i - 1)
            blacks_higher: int = 0
            whites_higher: int = 0
            for j in range(1, i):
                if blacks[j] > blacks[i]:
                    blacks_higher += 1
                if whites[j] > whites[i]:
                    whites_higher += 1
                self.cp_black += blacks_higher * factor
                self.cp_white += whites_higher * factor
        

    def _get_corner(self, corner_num: int) -> int:
        if corner_num < 4:
            return self.square1.pieces[self.up_alignment + corner_num * 2]
        else:
            return self.square1.pieces[self.down_alignment + corner_num * 2]

    def _get_edge(self, edge_num: int) -> int:
        if edge_num < 4:
            return self.square1.pieces[1 - self.up_alignment + edge_num * 2]
        else:
            return self.square1.pieces[1 - self.down_alignment + edge_num * 2]

    def _flip_layers(self) -> None:
        self.square1.flip_layers()
        self.up_alignment, self.down_alignment = 1 - self.down_alignment, 1 - self.up_alignment

    def _turn_layers(self, up_rot: int, down_rot: int) -> None:
        self.square1.turn_layers((self.up_alignment + up_rot * 2, self.down_alignment + down_rot * 2))
        self.up_alignment = 0
        self.down_alignment = 0