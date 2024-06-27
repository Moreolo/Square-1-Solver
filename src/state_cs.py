from square1 import Square1

class StateCS:
    def __init__(self, square1: Square1) -> None:
        self.square1 = Square1(square1.pieces[:])
        self.cs: int = 0
        self.parity: int = 0

        # calculate cubeshape
        # get shapes of layers
        up_shape: list[int]
        down_shape: list[int]
        up_shape, up_turn = self._get_shape(0)
        down_shape, down_turn = self._get_shape(8)
        self.square1.turn_layers((up_turn, down_turn))
        # flips cubeshape case
        if len(up_shape) < len(down_shape):
            up_shape, down_shape = down_shape, up_shape
        # gets cubeshape type
        self.cs += 30 * (len(up_shape) - 4)
        match len(up_shape) - 4:
            case 0:
                # turn layers for correct parity calculation
                highest: int = max(up_shape)
                index: int = up_shape.index(highest)
                if up_shape[index - 1] == highest:
                    index -= 1
                
                # handle all shapes with 4 + 4 edges
                up_case: int = _get_case_4_edges(up_shape)
                down_case: int = _get_case_4_edges(down_shape)
                self._set_cs_44_edges(up_case, down_case)
            case 1:
                # handle all shapes with 6 + 2 edges
                up_case: int = _get_case_6_edges(up_shape)
                down_case: int = _get_case_2_edges(down_shape)
                # converts the two cases to a combined CS case
                if up_case > 6:
                    self.parity = 1
                    up_case = _get_base_case_6_edges(up_case)
                self.cs = 39 + 7 * down_case + up_case
            case 2:
                # handle all shapes with 8 + 0 edges
                self.cs = 60 + min(up_shape)
                # state always takes same amount of slices, no matter parity
                return

        # calculate parity
        for i in range(16):
            for j in range(1, i):
                if self.square1.pieces[j] > self.square1.pieces[i]:
                    self.parity += 1
        self.parity %= 2

    # index is in range [0, 125[
    def get_index(self) -> int:
        return self.parity * 70 + self.cs

    def _get_shape(self, turn: int) -> tuple[list[int], int]:
        # gets shape of layer with start at turn
        shape: list[int] = [0]
        angle: int = 0
        while angle < 12:
            if self.square1.pieces[turn] % 2 == 0:
                shape.append(0)
                angle += 2
            else:
                shape[-1] += 1
                angle += 1
            turn += 1
        # gets layer turn
        highest: int = max(shape)
        index: int = shape.index(highest)
        # deals with 2200, 330, 11000 and 10100
        if shape.count(highest) == 2:
            if shape[index + 1] == 0:
                if highest == 1:
                    if shape[index + 2] == 0:
                        index += 1
                else:
                    index += 1
        # calculates turn
        turn = 0
        for i in range(index):
            turn += shape[i] + 1
        # remove excess number
        if shape[0] == 0:
            shape.pop(0)
        elif shape[-1] == 0:
            shape.pop(-1)
        else:
            #deals with overflow
            shape[0] += shape[-1]
            # turn is different
            if shape[0] > highest:
                turn = 8 - shape[-1]
            elif shape[0] == highest and shape[index - 1] != 0:
                turn = 8 - shape[-1]
            shape.pop(-1)
        return shape, turn

    def _set_cs_44_edges(self, up_case: int, down_case: int) -> None:
        # converts the two cases to a combined CS case
        if up_case > 7 or down_case > 7:
            extra: int = max(up_case, down_case) - 8
            if up_case == 5 or down_case == 5:
                extra += 1
            elif not (up_case == 1 or down_case == 1):
                extra = -1
            if extra != -1:
                up_case = 8
                down_case = extra
            else:
                up_case = _get_base_case_4_edges(up_case)
                down_case = _get_base_case_4_edges(down_case)
                if (up_case == 2 or down_case == 2 or
                    up_case == 3 or down_case == 3 or
                    up_case == 7 or down_case == 7):
                    self.parity = 1
                up_case, down_case = _bigger_first(up_case, down_case)
        else:
            up_case, down_case = _bigger_first(up_case, down_case)
        self.cs = (up_case * (up_case + 1) // 2) + down_case


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
    
def _get_base_case_4_edges(case: int) -> int:
    if case == 8:
        return 1
    elif case == 9:
        return 5
    else:
        return case

def _get_case_6_edges(edge_list: list[int]) -> int:
    # calculate distinct cases
    highest: int = max(edge_list)
    previous: int = edge_list[edge_list.index(highest) - 1]
    if highest == 3 and previous == 0:
        previous = 3
    case: int = highest - previous + min(highest - 2, 3)
    # move mirrors to back
    if case < 3:
        return case
    elif case == 3:
        return 7
    elif 3 < case < 6:
        return case - 1
    elif case == 6:
        return 8
    elif case == 7:
        return 5
    elif case == 8:
        return 9
    else:
        return 6

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

def _get_base_case_6_edges(case: int) -> int:
    if case == 7:
        return 2
    elif case == 8:
        return 3
    elif case == 9:
        return 5
    else:
        return case

def _bigger_first(num1: int, num2: int) -> tuple[int, int]:
    if num1 < num2:
        return num2, num1
    else:
        return num1, num2