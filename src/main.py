from square1 import Square1
from solver import Solver

solver: Solver = Solver()
# scramble: (1,0)/ (3,0)/ (5,-4)/ (-2,-5)/ (-4,-1)/ (3,0)/ (-2,0)/ (0,-3)/ (0,-2)/ (3,0)/ (-1,0)/ (-3,-4)/ (-4,0)/ (0,-2)
# square1, bar_solved = Square1([14, 13, 7, 8, 0, 12, 2, 1, 11, 9, 3, 6, 15, 4, 10, 5]), False
square1, bar_solved = Square1([2, 7, 13, 15, 5, 1, 14, 0, 11, 12, 3, 9, 10, 6, 8, 4]), False
print("Scramble: (1,0)/ (3,0)/ (5,-4)/ (-2,-5)/ (-4,-1)/ (3,0)/ (-2,0)/ (0,-3)/ (0,-2)/ (3,0)/ (-1,0)/ (-3,-4)/ (-4,0)/ (0,-2)")
print(solver.solve(square1, bar_solved))