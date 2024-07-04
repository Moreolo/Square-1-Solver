from square1 import Square1
# from solver import SolverStandard as Solver
from solver.solver_astar import SolverAstar as Solver

solver: Solver = Solver()
print("Scramble: (1,0)/ (3,0)/ (5,-4)/ (-2,-5)/ (-4,-1)/ (3,0)/ (-2,0)/ (0,-3)/ (0,-2)/ (3,0)/ (-1,0)/ (-3,-4)/ (-4,0)/ (0,-2)")
square1, bar_solved = Square1([2, 7, 13, 15, 5, 1, 14, 0, 11, 12, 3, 9, 10, 6, 8, 4]), False
# print("Scramble: (0,2)/ (-2,-2)/ (-3,0)/ (-1,-1)/ (3,0)/ (0,-3)/ (0,-5)/ (-3,-3)/ (2,-5)/ (0,-4)/ (2,-2)/ (6,0)")
# square1, bar_solved = Square1([0, 8, 2, 6, 10, 12, 7, 1, 11, 13, 3, 5, 9, 15, 14, 4]), False
# square1, bar_solved = Square1([0, 1, 2, 3, 4, 7, 6, 5, 8, 9, 10, 11, 12, 13, 14, 15]), False
solution = solver.solve(square1, bar_solved)
print("Solution:", solution[0], end='')
for i in range(1, len(solution)):
    print('/', solution[i], end='')
print()