import copy

class SudokuSolver:
    def __init__(self, puzzle):
        self.__puzzle = puzzle
        self.__zeros = []
        self.__solution = None
        
    def __getAllPossible(self, row, col):
        filt = lambda cur, inp: [n for n in cur if n not in inp]
        res = filt(range(1, 9+1), self.__puzzle[row])
        res = filt(res, [l[col] for l in self.__puzzle])
        rBegin = row - row%3
        cBegin = col - col%3
        return filt(res, [self.__puzzle[i][j] for i in range(rBegin, rBegin+3) for j in range(cBegin, cBegin+3)])
    
    def __validateGrid(self):
        if len(self.__puzzle) != 9 or not all(len(l) == 9 for l in self.__puzzle):
            raise RuntimeError("Invalid grid")
        if 9*9-(zeros := sum([l.count(0) for l in self.__puzzle])) < 17 or zeros == 0:
            raise RuntimeError("Invalid grid")
        if not all([type(n) == int for l in self.__puzzle for n in l if n != 0]):
            raise RuntimeError("Invalid grid")
        self.__validatePuzzle()
        
    def __validatePuzzle(self):
        filt = lambda inp: all([inp.count(n) == 1 for n in inp if n != 0])
        for l in self.__puzzle:
            if not filt(l):
                raise RuntimeError("Invalid grid")
        for col in range(9):
            if not filt([l[col] for l in self.__puzzle]):
                raise RuntimeError("Invalid grid")
        for row in range(0, 9, 3):
            for col in range(0, 9, 3):
                if not filt([self.__puzzle[i][j] for i in range(row, row+3) for j in range(col, col+3)]):
                    raise RuntimeError("Invalid grid")
        
    def __solve(self):
        row, col = 0,0
        possibles = None
        reset = []
        for i,j in self.__zeros:
            ps = self.__getAllPossible(i, j)
            if len(ps) == 0:
                for i,j in reset:
                    self.__puzzle[i][j] = 0
                return
            elif len(ps) == 1:
                self.__puzzle[i][j] = ps[0]
                reset.append((i,j))
            elif possibles is None or len(ps) < len(possibles):
                possibles = ps
                row = i
                col = j
                
        if possibles is None:
            if self.__solution is not None:
                raise RuntimeError("Multiple solutions")
            self.__solution = copy.deepcopy(self.__puzzle)
            return
        
        possibles = self.__getAllPossible(row, col)
        if len(possibles) == 0:
            for i,j in reset:
                self.__puzzle[i][j] = 0
            return
        
        reset.append((row,col))
        self.__zeros = [c for c in self.__zeros if c not in reset]
        
        for p in possibles:
            self.__puzzle[row][col] = p
            self.__solve()
            
        for i,j in reset:
            self.__puzzle[i][j] = 0
        self.__zeros.extend(reset)
    
    def solve(self):
        self.__validateGrid()
        self.__zeros = [(i,j) for i,l in enumerate(self.__puzzle) for j,n in enumerate(l) if n == 0]
        self.__solve()
        if self.__solution is not None:
            return self.__solution
        raise RuntimeError("No solution")

def sudoku_solver(puzzle):
    solver = SudokuSolver(puzzle)
    return solver.solve()
