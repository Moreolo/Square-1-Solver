class Symmetry:
    def __init__(self, flip_l: bool, flip_c: bool, mirror: bool, up_rot: int, down_rot: int) -> None:
        self.flip_l: bool = flip_l
        self.flip_c: bool = flip_c
        self.mirror: bool = mirror
        self.up_rot: int = up_rot
        self.down_rot: int = down_rot