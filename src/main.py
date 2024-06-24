from square1 import Square1

sq1 = Square1()

print(sq1.pieces)
sq1.turn_slice()
print(sq1.pieces)
sq1.turn_layers((1, 2))
print(sq1.pieces)
print(sq1.get_unique_turns())