from square1 import Square1

class StateCS:
    size: int = 113 # = 65 * 2 - 5 - 12
    max_slices: int = 7

    def __init__(self, square1: Square1 = Square1()) -> None:
        self.square1: Square1 = square1
        self.cs: int = 0 # 65 = 39 + 21 + 5
        self.parity: int = 0 # 2
        self.name: str = ""

        # calculate cubeshape
        # get shapes of layers
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

                self.name = _num_to_name_4(up_case) + " " + _num_to_name_4(down_case)
                # corrects case number for cubeshape number
                if up_case == 8:
                    if down_case == 1:
                        down_case = 0
                    else:
                        down_case = 1
                elif up_case == 9:
                    up_case = 8
                    down_case = 2

                self.cs = (up_case * (up_case + 1) // 2) + down_case
                # turns layers for parity calculation
                up_turn: int = self._get_shape_turn(True, up_shape)
                down_turn: int = self._get_shape_turn(False, down_shape)
                self.square1.turn_layers((up_turn, down_turn))

            case 1:
                # handle all shapes with 6 + 2 edges
                up_case: int = _get_case_6_edges(up_shape)
                down_case: int = _get_case_2_edges(down_shape)
                # mirrors asymmetric states to base mirror states
                if up_case > 6:
                    self.square1.mirror_layers(9)
                    up_case -= 7
                self.name = _num_to_name_2(down_case) + " " + _num_to_name_6(up_case)
                # converts the two cases to a combined CS case
                self.cs = 39 + 3 * up_case + down_case
                # turns layers for parity calculation
                up_turn: int = self._get_shape_turn(True, up_shape)
                down_turn: int = self._get_shape_turn(False, down_shape)
                self.square1.turn_layers((up_turn, down_turn))
                # symmetric states always tale same amount of slices, no matter parity
                if up_case > 2:
                    return
            case 2:
                # handle all shapes with 8 + 0 edges
                self.cs = 60 + min(up_shape)
                self.name = _num_to_name_8(min(up_shape))
                # state always takes same amount of slices, no matter parity
                return

        # calculate parity
        for i in range(16):
            for j in range(1, i):
                if self.square1.pieces[j] > self.square1.pieces[i]:
                    self.parity += 1
        self.parity %= 2

    # index is in range [0, 113[
    def get_index(self) -> int:
        return self.parity * 65 + self.cs

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

    def _get_shape_turn(self, is_up: bool, shape: list[int]) -> int:
        highest: int = max(shape)
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

def _get_case_4_edges(edge_list: list[int]) -> int:
    # calculate distinct cases
    case: int = max(max(edge_list) - 2, 0)
    gap: int = 1
    for i in range(4):
        if edge_list[i] == 0:
            distance: int = 0
            while edge_list[i - 1 - distance] < 2:
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

def _get_case_6_edges(edge_list: list[int]) -> int:
    # calculate distinct cases
    highest: int = max(edge_list)
    previous: int = edge_list[edge_list.index(highest) - 1]
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

def _get_case_2_edges(edge_list: list[int]) -> int:
    try:
        index: int = edge_list.index(1)
    except:
        return 0
    else:
        if edge_list[index - 1] == 1 or edge_list[index + 1] == 1:
            return 1
        else:
            return 2

def _num_to_name_4(num: int) -> str:
    match num:
        case 0: return "Square"
        case 1: return "Good Fist"
        case 2: return "Kite"
        case 3: return "Barrel"
        case 4: return "Shield"
        case 5: return "Good Pawn"
        case 6: return "Muffin"
        case 7: return "Scallop"
        case 8: return "Bad Fist"
        case 9: return "Bad Pawn"
    return ""

def _num_to_name_2(num: int) -> str:
    match num:
        case 0: return "V"
        case 1: return "L"
        case 2: return "I"
    return ""

def _num_to_name_6(num: int) -> str:
    match num:
        case 0: return "3-1-2"
        case 1: return "2-4"
        case 2: return "1-5"
        case 3: return "2-2-2"
        case 4: return "3-3"
        case 5: return "4-1-1"
        case 6: return "6"
    return ""

def _num_to_name_8(num: int) -> str:
    match num:
        case 0: return "8"
        case 1: return "7-1"
        case 2: return "6-2"
        case 3: return "5-3"
        case 4: return "4-4"
    return ""

