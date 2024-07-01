from square1 import Square1

sq1 = Square1()
print(sq1.pieces)
num = sq1.get_int()
print(num)
sq1 = Square1(num)
print(sq1.pieces)
print(sq1.get_int())
sq1.turn_layers((3, 3))
print(sq1.get_int())