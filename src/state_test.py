from square1 import Square1
from state.state_all import StateAll

square1: Square1 = Square1()
square1.turn_slice()
square1.turn_layers((6, 0))
square1.turn_slice()
square1.turn_layers((7, 0))
square1.turn_slice()
square1.turn_layers((2, 0))
square1.turn_slice()
# square1.turn_layers((2, 0))
# square1.turn_slice()
# square1.turn_layers((2, 0))
# square1.turn_slice()
# square1.turn_layers((7, 0))
# square1.turn_slice()

state: StateAll = StateAll(square1.get_copy())

print(square1.pieces)
print(state.square1.pieces)
print(state._get_symmetry_actions())
print(state.up_re)
print(state.down_re)