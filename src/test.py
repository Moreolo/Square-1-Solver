from square1 import Square1
from state_cs import StateCS

square11 = Square1([0, 1, 3, 2, 4, 5, 6, 7, 8, 10, 9, 11, 12, 13, 14, 15])
square12 = Square1([0, 3, 1, 2, 4, 5, 6, 7, 8, 10, 9, 11, 12, 13, 14, 15])
state1 = StateCS(square11.get_copy())
state2 = StateCS(square12.get_copy())
print(state1.get_index(), state2.get_index())
square11.turn_layers((0, 7))
square11.turn_slice()
square12.turn_layers((0, 7))
square12.turn_slice()
state1 = StateCS(square11.get_copy())
state2 = StateCS(square12.get_copy())
print(state1.get_index(), state2.get_index())