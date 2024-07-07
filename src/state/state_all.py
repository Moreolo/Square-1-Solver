from square1 import Square1

fnm: list[tuple[bool, bool]] = [(False, False), (True, False)]
nfm: list[tuple[bool, bool]] = [(False, False), (False, True)]
fom: list[tuple[bool, bool]] = [(False, False), (False, True), (True, False), (True, True)]
fam: list[tuple[bool, bool]] = [(False, False), (True, True)]
nan: list[tuple[bool, bool]] = [(False, False)]

r_4_2: list[int] = [0, 2, 4, 6]
r_2_4: list[int] = [0, 4]
r_3_3: list[int] = [0, 3, 6]
r_2_5: list[int] = [0, 5]
r_6_1: list[int] = [0, 1, 2, 3, 4, 5]
r_1_0: list[int] = [0]

class StateAll:
    size: int = 3302208000 # = 65 * 35 * 3! 3! 8!
    max_slices: int = 12

    def __init__(self, square1: Square1 = Square1()) -> None:
        self.square1 = square1
        self.cs = 0 # 65 = 39 + 21 + 5
        self.co = 0 # 35 = 7C3
        self.cp_black = 0 # 6 = 3!
        self.cp_white = 0 # 6 = 3!
        self.ep = 0 # 40320 = 8!

        self.caclculate_cs()
        self.calculate_p()

    def get_index(self) -> int:
        index: int = self.ep
        index = index * 65 + self.cs
        index = index * 35 + self.co
        index = index * 6 + self.cp_black
        index = index * 6 + self.cp_white
        return index

    def get_symmetric_indecies(self) -> list[int]:
        # copies square1 to not modify base cube
        square1: Square1 = self.square1.get_copy()
        # cycles through all possible symmetries for the cs case
        flip_mirrors, up_turns, down_turns = self._get_symmetry_actions()
        indecies: list[int] = []
        for flip_mirror in flip_mirrors:
            # does the axis symmetry actions
            mirrored: bool = False
            if flip_mirror[1]:
                self.square1.mirror_layers()
                mirrored = True
            if flip_mirror[0]:
                self.square1.flip_layers()
            # copies cube another time
            mod: Square1 = square1.get_copy()
            for up_turn in up_turns:
                for down_turn in down_turns:
                    if not flip_mirrors[0] and not flip_mirrors[1] and up_turn == 0 and down_turn == 0:
                        continue
                    # rotates the layers of action
                    if mirrored:
                        self.square1.turn_layers((self.up_re + up_turn, self.down_re + down_turn))
                    else:
                        self.square1.turn_layers((up_turn, down_turn))
                    # recalculates permutation and adds index to list
                    self.calculate_p()
                    indecies.append(self.get_index())
                    # resets square1
                    self.square1 = mod.get_copy()
            self.square1 = square1.get_copy()
        return indecies

    # calculates cubeshape case
    def caclculate_cs(self) -> None:
        # gets shapes of layers
        up_shape: list[int] = self._get_shape(True)
        down_shape: list[int] = self._get_shape(False)
        # flips shape with more edges to up
        if len(up_shape) > 4:
            self.square1.flip_layers()
            up_shape, down_shape = down_shape, up_shape
        match 4 - len(up_shape):
            case 0:
                # handle all shapes with 4 + 4 edges
                up_case: int = _get_case_4_edges(up_shape)
                down_case: int = _get_case_4_edges(down_shape)

                # mirrors if one case is asymmetrical
                # except for:
                # 8 + 1, 8 + 5
                # 9 + 5
                # 1 + 8, 5 + 8
                # 5 + 9
                if ((up_case > 7 or down_case > 7) and (not
                        (up_case == 1 or up_case == 5 or
                        down_case == 1 or down_case == 5) or
                        (up_case == 9 and down_case == 1 or
                        up_case == 1 and down_case == 9))):
                    # mirrors case
                    self.square1.mirror_layers(8)
                    up_case = _mirror_case_4_edges(up_case)
                    down_case = _mirror_case_4_edges(down_case)

                if up_case < down_case:
                    # flips case
                    self.square1.flip_layers()
                    up_shape, down_shape = down_shape, up_shape
                    up_case, down_case = down_case, up_case

                # corrects case number for cubeshape number
                if up_case == 8:
                    if down_case == 1:
                        down_case = 0
                    else:
                        down_case = 1
                elif up_case == 9:
                    up_case = 8
                    down_case = 2

                # sets values for symmetry finder
                self.up_case: int = up_case
                self.down_case: int = down_case
                if up_case != 4:
                    self.up_re: int = max(up_shape)
                else:
                    self.up_re: int = 5
                if down_case == 0 and up_case != 8:
                    self.down_re: int = 1
                elif down_case == 3:
                    self.down_re: int = 2
                elif down_case != 4:
                    self.down_re: int = 8 - max(down_shape)
                else:
                    self.down_re: int = 8 - 5

                self.cs = _sum_to(up_case) + down_case
            case 1:
                # handle all shapes with 6 + 2 edges
                up_case: int = _get_case_6_edges(up_shape)
                down_case: int = _get_case_2_edges(down_shape)
                # mirrors asymmetric states to base mirror states
                if up_case > 6:
                    self.square1.mirror_layers(9)
                    up_case -= 7

                # sets values for symmetry finder
                self.up_case: int = up_case
                self.down_case: int = -1
                if up_case != 4:
                    self.up_re: int = max(up_shape)
                else:
                    self.up_re: int = 7
                if down_case == 0:
                    self.down_re: int = 7 - 2
                elif down_case == 1:
                    self.down_re: int = 7 - 3
                else:
                    self.down_re: int = 7 - 4

                # converts the two cases to a combined CS case
                self.cs = 39 + 3 * up_case + down_case
            case 2:
                # sets values for symmetry finder
                self.up_case: int = min(up_shape)
                self.down_case: int = -2
                self.up_re: int = max(up_shape)
                self.down_re: int = 0

                # sets cs case
                self.cs = 60 + self.up_case
        # places shape in same position everytime
        self._correct_shape_turn(up_shape, down_shape)

    def calculate_p(self) -> None:
        # flips black to first corner
        if self.square1.pieces[0] > 7:
            self.square1.flip_colors()

        # gets white gaps in co and cp offset
        corner_gaps: list[int] = []
        gap: int = 0
        black_offset: int = -1
        white_offset: int = -1
        for piece in self.square1.pieces:
            if not piece & 1:
                if piece > 7:
                    gap += 1
                    if white_offset == -1:
                        white_offset = piece // 2 - 4
                else:
                    corner_gaps.append(gap)
                    gap = 0
                    if black_offset == -1:
                        black_offset = piece // 2
        # calculates unique co case
        n1: int = 4 - corner_gaps[1]
        n2: int = n1 - corner_gaps[2]
        n3: int = n2 - corner_gaps[3]
        self.co = _sum_sum_to(n1) + _sum_to(n2) + n3

        # calculates permutations
        self.square1.cycle_colors((black_offset, white_offset))
        self.cp_black = 0
        self.cp_white = 0
        self.ep = 0
        blacks: list[int] = []
        whites: list[int] = []
        edges: list[int] = []
        black_index: int = -1
        white_index: int = -1
        edge_index: int = 0
        black_factor: int = 1
        white_factor: int = 1
        edge_factor: int = 1
        for piece in self.square1.pieces:
            higher: int = 0
            if piece & 1:
                # calculates ep
                if edge_index > 0:
                    edge_factor *= edge_index
                    for check in edges:
                        if check > piece:
                            higher += 1
                    self.ep += higher * edge_factor
                edges.append(piece)
                edge_index += 1
            elif piece > 7:
                # calculates cp white
                if white_index > 0:
                    white_factor *= white_index
                    for check in whites:
                        if check > piece:
                            higher += 1
                    self.cp_white += higher * white_factor
                if white_index > -1:
                    whites.append(piece)
                white_index += 1
            else:
                # calculates cp black
                if black_index > 0:
                    black_factor *= black_index
                    for check in blacks:
                        if check > piece:
                            higher += 1
                    self.cp_black += higher * black_factor
                if black_index > -1:
                    blacks.append(piece)
                black_index += 1


    def _get_shape(self, is_up: bool) -> list[int]:
        # gets shape of layer with start at turn
        shape: list[int] = [0]
        turn: int = 0
        angle: int = 0
        while angle < 12:
            if self.square1.pieces[turn if is_up else 15 - turn] % 2 == 0:
                shape.append(0)
                angle += 2
            else:
                shape[-1] += 1
                angle += 1
            turn += 1
        # remove excess number
        if shape[0] == 0:
            shape.pop(0)
        elif shape[-1] == 0:
            shape.pop(-1)
        else:
            #deals with overflow
            shape[0] += shape[-1]
            shape.pop(-1)
        return shape

    def _correct_shape_turn(self, up_shape: list[int], down_shape: list[int]) -> None:
        self.square1.turn_layers((self._get_shape_turn(True, up_shape), self._get_shape_turn(False, down_shape)))

    def _get_shape_turn(self, is_up: bool, shape: list[int]) -> int:
        highest: int = max(shape)
        if highest == 0:
            return 0
        piece_count: int = 12 - len(shape)

        edge_count: int = 0
        turn: int = 0
        while edge_count < highest:
            if self.square1.pieces[turn if is_up else 15 - turn] % 2 == 0:
                edge_count = 0
            else:
                edge_count += 1
            turn = (turn + 1) % piece_count

        if shape.count(highest) == 2:
            if self.square1.pieces[(turn + 1) if is_up else 15 - (turn + 1)] % 2 != 0:
                turn = (turn + 1 + highest) % piece_count
            elif highest == 1:
                if self.square1.pieces[(turn + 2) if is_up else 15 - (turn + 2)] % 2 != 0:
                    turn = (turn + 3) % piece_count

        return turn if is_up else (piece_count - turn) % piece_count

    def _get_symmetry_actions(self) -> tuple[list[tuple[bool, bool]], list[int], list[int]]:
        flip_mirrors: list[tuple[bool, bool]]
        up_turns: list[int]
        down_turns: list[int]
        if self.down_case == -2:
            flip_mirrors = nfm
            if self.up_case == 4:
                up_turns = r_2_5
            else:
                up_turns = r_1_0
            down_turns = r_6_1
        elif self.down_case == -1:
            if self.up_case > 2:
                flip_mirrors = nfm
            else:
                flip_mirrors = nan
            if self.up_case == 3:
                up_turns = r_3_3
            else:
                up_turns = r_1_0
            down_turns = r_1_0
        else:
            if self.up_case == 8:
                if self.down_case == 1:
                    flip_mirrors = nan
                else:
                    flip_mirrors = fam
            elif self.up_case == self.down_case:
                if self.up_case == 1 or self.up_case == 5:
                    flip_mirrors = fnm
                else:
                    flip_mirrors = fom
            elif self.up_case == 1 or self.down_case == 1 or self.up_case == 5 or self.down_case == 5:
                flip_mirrors = nan
            else:
                flip_mirrors = nfm
            if self.up_case == 0:
                up_turns = r_4_2
            elif self.up_case == 3:
                up_turns = r_2_4
            else:
                up_turns = r_1_0
            if self.down_case == 0 and self.up_case != 8:
                down_turns = r_4_2
            elif self.down_case == 3:
                down_turns = r_2_4
            else:
                down_turns = r_1_0
        return flip_mirrors, up_turns, down_turns


def _get_case_4_edges(shape: list[int]) -> int:
    # calculate distinct cases
    case: int = max(max(shape) - 2, 0)
    gap: int = 1
    for i in range(4):
        if shape[i] == 0:
            distance: int = 0
            while shape[i - 1 - distance] < 2:
                distance += 1
            case += gap + distance
            if gap == 1:
                gap = 3
            else:
                gap = 0
    # move mirrors to back
    if case < 3:
        return case
    elif case == 3:
        return 8
    elif 3 < case < 8:
        return case - 1
    elif case == 8:
        return 9
    else:
        return 7

def _mirror_case_4_edges(case: int) -> int:
    match case:
        case 1: return 8
        case 5: return 9
        case 8: return 1
        case 9: return 5
    return case

def _get_case_6_edges(shape: list[int]) -> int:
    # calculate distinct cases
    highest: int = max(shape)
    previous: int = shape[shape.index(highest) - 1]
    if highest == 3 and previous == 0:
        previous = 3
    case: int = highest - previous + min(highest - 2, 3)
    # move mirrors to back and base mirrors to front
    match case:
        case 0: return 3
        case 1: return 4
        case 2: return 0
        case 3: return 7
        case 4: return 1
        case 5: return 5
        case 6: return 8
        case 7: return 2
        case 8: return 9
        case 9: return 6
    return 3

def _get_case_2_edges(shape: list[int]) -> int:
    try:
        index: int = shape.index(1)
    except:
        return 0
    else:
        if shape[index - 1] == 1 or shape[index + 1] == 1:
            return 1
        else:
            return 2

def _sum_sum_to(val: int) -> int:
    if val < 1:
        return 0
    else:
        return val * val + _sum_sum_to(val - 2)

def _sum_to(val: int) -> int:
    return (val * (val + 1)) // 2