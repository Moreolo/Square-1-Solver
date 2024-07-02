from square1 import Square1
from symmetry import Symmetry

co_0: list[Symmetry] = []
for up_rot in range(4):
    for down_rot in range(4):
        co_0.append(Symmetry(False, False, False, up_rot, down_rot))
        co_0.append(Symmetry(True, True, False, up_rot, down_rot))
        co_0.append(Symmetry(True, False, True, up_rot, down_rot))
        co_0.append(Symmetry(False, True, True, up_rot, down_rot))
co_0.pop(0)

co_1: list[Symmetry] = []
co_1.append(Symmetry(True, True, False, 3, 3))
co_1.append(Symmetry(True, False, True, 0, 0))
co_1.append(Symmetry(False, True, True, 3, 3))

co_2: list[Symmetry] = []
co_2.append(Symmetry(True, False, False, 2, 2))
co_2.append(Symmetry(False, True, False, 2, 2))
co_2.append(Symmetry(False, False, True, 2, 2))
co_2.append(Symmetry(True, True, False, 0, 0))
co_2.append(Symmetry(True, False, True, 0, 0))
co_2.append(Symmetry(False, True, True, 0, 0))
co_2.append(Symmetry(True, True, True, 2, 2))

co_3: list[Symmetry] = []
for down_rot in range(0, 4, 2):
    co_3.append(Symmetry(False, False, False, 0, 0 + down_rot))
    co_3.append(Symmetry(False, True, False, 2, 1 + down_rot))
    co_3.append(Symmetry(False, False, True, 2, 0 + down_rot))
    co_3.append(Symmetry(False, True, True, 0, 1 + down_rot))
co_3.pop(0)

co_4: list[Symmetry] = []
for up_rot in range(0, 4, 2):
    for down_rot in range(0, 4, 2):
        co_4.append(Symmetry(False, False, False, 0 + up_rot, 0 + down_rot))
        co_4.append(Symmetry(True, False, False, 0 + up_rot, 0 + down_rot))
        co_4.append(Symmetry(False, True, False, 1 + up_rot, 1 + down_rot))
        co_4.append(Symmetry(False, False, True, 0 + up_rot, 0 + down_rot))
        co_4.append(Symmetry(True, True, False, 1 + up_rot, 1 + down_rot))
        co_4.append(Symmetry(True, False, True, 0 + up_rot, 0 + down_rot))
        co_4.append(Symmetry(False, True, True, 1 + up_rot, 1 + down_rot))
        co_4.append(Symmetry(True, True, True, 1 + up_rot, 1 + down_rot))
co_4.pop(0)


class StateSqSq:
    size: int = 3628800 # = 5 * 3! 3! 8! / 2
    max_slices: int = 9

    def __init__(self, square1: Square1 = Square1()) -> None:
        self.square1: Square1 = square1
        self.co: int # 5
        self.cp_black: int # 6 = 3!
        self.cp_white: int # 6 = 3!
        self.ep: int # 20160 = 8! / 2

        self.up_alignment: int = self.square1.pieces[0] % 2
        self.down_alignment: int = self.square1.pieces[8] % 2
        self.calculate_orientation()
        self.calculate_permutation()

    # index is in range [0, 3 628 800[
    def get_index(self) -> int:
        index: int = self.ep
        index = index * 5 + self.co
        index = index * 6 + self.cp_black
        index = index * 6 + self.cp_white
        return index

    def get_symmetric_indecies(self) -> list[int]:
        # copies square1 to not modify base cube
        square1: Square1 = self.square1.get_copy()
        # cycles through all possible symmetries for the co case
        actions: list[Symmetry] = self._get_symmetry_actions()
        indecies: list[int] = []
        for action in actions:
            # does the flips of the action
            if action.flip_l:
                self._flip_layers()
            if action.flip_c:
                self._flip_colors()
            if action.mirror:
                self._mirror_layers()
            # rotates the layers of the action
            self._rotate_layers(action.up_rot, action.down_rot)
            # recalculates permutation and adds index to list
            self.calculate_permutation()
            indecies.append(self.get_index())
            # resets square1
            self.square1 = square1.get_copy()
        return indecies

    # calculates the corner orientation case
    def calculate_orientation(self) -> None:
        self.co = 0
        # counts corner colors in the up layer
        black: bool = self._get_corner(0) < 8
        count: int = 1
        for i in range(1, 4):
            if (self._get_corner(i) < 8) == black:
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
            if (self._get_corner(2) < 8) == black:
                self.co += 1
                up_is_opp = True
            if (self._get_corner(4) < 8) == (self._get_corner(6) < 8):
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
            if up_rot == 3 and self._get_corner(0) > 7:
                up_rot = 0
            if down_rot == 3 and self._get_corner(4) < 8:
                down_rot = 0
        elif self.co == 3:
            if up_rot == 3 and self._get_corner(0) > 7:
                up_rot = 0
        # rotates layers
        self._rotate_layers(up_rot, down_rot)

    def calculate_permutation(self) -> None:
        self.cp_black = 0
        self.cp_white = 0
        self.ep = 0
        # cycles lowest black corner and lowest white corner to front
        black_offset: int = -1
        white_offset: int = -1
        index: int = 0
        while black_offset == -1 or white_offset == -1:
            corner: int = self._get_corner(index) // 2
            if corner < 4:
                if black_offset == -1:
                    black_offset = corner
            else:
                if white_offset == -1:
                    white_offset = corner - 4
            index += 1
        self.square1.cycle_colors((black_offset, white_offset))

        # calculates permutations
        blacks: list[int] = []
        whites: list[int] = []
        for i in range(8):
            corner: int = self._get_corner(i)
            if corner < 8:
                blacks.append(corner)
            else:
                whites.append(corner)
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
        factor = 1
        for i in range(1, 8):
            factor *= i
            edges_higher: int = 0
            for j in range(i):
                if self._get_edge(j) > self._get_edge(i):
                    edges_higher += 1
            self.ep += edges_higher * factor
        # devides by 2 because parity is always even
        self.ep //= 2

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

    def _rotate_layers(self, up_rot: int, down_rot: int) -> None:
        self.square1.turn_layers((self.up_alignment + up_rot * 2, self.down_alignment + down_rot * 2))
        self.up_alignment = 0
        self.down_alignment = 0

    def _flip_colors(self) -> None:
        self.square1.flip_colors()

    def _mirror_layers(self) -> None:
        self.square1.mirror_layers(8)
        self.up_alignment = 1 - self.up_alignment
        self.down_alignment = 1 - self.down_alignment

    def _get_symmetry_actions(self) -> list[Symmetry]:
        match self.co:
            case 0:
                return co_0
            case 1:
                return co_1
            case 2:
                return co_2
            case 3:
                return co_3
            case 4:
                return co_4
        return []