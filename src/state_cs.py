from square1 import Square1

class StateCS:
    def __init__(self, square1: Square1) -> None:
        self.cs: int = 0
        self.parity: int = 0

        up_shape: list[int] = self.get_shape(square1.pieces, 0)
        down_shape: list[int] = self.get_shape(square1.pieces, 8)

        # flips cubeshape case
        if len(up_shape) < len(down_shape):
            up_shape, down_shape = down_shape, up_shape
        # gets cubeshape type
        self.cs += 30 * (len(up_shape) - 4)
        match len(up_shape) - 4:
            case 0:
                # handle all shapes with 4 + 4 edges
                up_case: int = get_case_4_edges(up_shape)
                down_case: int = get_case_4_edges(down_shape)
                self.set_cs_4_edges(up_case, down_case)
            case 1:
                pass
            case 2:
                pass

        # cube shape
        # 4000  scallop 9 = 1 + 0 + 3 + 1 + 0 + 2 + 2 --
        # 3100  paw     8 = 1 + 1 + 3 + 2 + 1
        # 3001          6 = 1 + 0 + 3 + 1 + 1
        # 3010  muffin  7 = 1 + 0 + 3 + 2 + 1 ++
        # 2200  shield  5 = 1 + 0 + 3 + 1 ++
        # 2020  barrel  4 = 1 + 0 + 3 + 0 --
        # 2110  fist    3 = 1 + 2
        # 2011          1 = 1 + 0
        # 2101  kite    2 = 1 + 1 --
        # 1111  square  0 ++
        # for Lücke: (Lücke + Abstand zu größer 1) + max(höchstes - 2, 0)
        # Lücke Nr. 0   1   2   3
        # Wert      0   1   3   0
        # 20000 pair
        # 11000 L
        # 10100 I
        # 600   9 = 6 - 0 + 3
        # 510   8 = 5 - 0 + 3
        # 501   7 = 5 - 1 + 3
        # 420   6 = 4 - 0 + 2
        # 402   4 = 4 - 2 + 2
        # 411   5 = 4 - 1 + 2
        # 330   1 = 3 - 3 + 1
        # 321   3 = 3 - 1 + 1
        # 312   2 = 3 - 2 + 1
        # 222   0 = 2 - 2 + 0
        # höchstes - davor + min(höchstes - 2, 3)

        # 80
        # 71
        # 62
        # 53
        # 44
        # kleinstes

        # parity

        # 0 1 2 3
        # - 0 0 0

        # 0 2 1 3
        # - 0 1 0

        # 0 3 1 2
        # - 0 1 1

    def get_shape(self, pieces: list[int], turn: int) -> list[int]:
        # gets shape of layer with start at turn
        shape: list[int] = [0]
        angle: int = 0
        while angle < 12:
            if pieces[turn] % 2 == 0:
                shape.append(0)
                angle += 2
            else:
                shape[-1] += 1
                angle += 1
            turn += 1
        if shape[0] == 0:
            shape.pop(0)
        elif shape[-1] == 0:
            shape.pop(-1)
        else:
            shape[0] += shape[-1]
            shape.pop(-1)
        return shape

    def set_cs_4_edges(self, up_case: int, down_case: int) -> None:
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
                up_case = base_shape(up_case)
                down_case = base_shape(down_case)
                if (up_case == 2 or down_case == 2 or
                    up_case == 3 or down_case == 3 or
                    up_case == 7 or down_case == 7):
                    self.parity = 1
                up_case, down_case = bigger_first(up_case, down_case)
        else:
            up_case, down_case = bigger_first(up_case, down_case)
        self.cs = (up_case * (up_case + 1) // 2) + down_case


def get_case_4_edges(edge_list: list[int]) -> int:
    # calculate distinct cases
    shape: int = max(max(edge_list) - 2, 0)
    gap: int = 1
    for i in range(4):
        if edge_list[i] == 0:
            distance: int = 0
            while edge_list[i - 1 - distance] < 2:
                distance += 1
            shape += gap + distance
            if gap == 1:
                gap = 3
            else:
                gap = 0
    # move mirrors to back
    if shape < 3:
        return shape
    elif shape == 3:
        return 8
    elif 3 < shape < 8:
        return shape - 1
    elif shape == 8:
        return 9
    else:
        return 7
    
def base_shape(shape: int) -> int:
    if shape == 8:
        return 1
    elif shape == 9:
        return 5
    else:
        return shape

def bigger_first(num1: int, num2: int) -> tuple[int, int]:
    if num1 < num2:
        return num2, num1
    else:
        return num1, num2