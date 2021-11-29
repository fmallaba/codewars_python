import copy

class SudokuSolver:
    """
    Solves sudoku if valid puzzle passed.
    Puzzle with multiple solutions considered as invalid.
    """
    def __init__(self, puzzle):
        self.__puzzle = puzzle
        self.__unknowns = []
        self.__solution = None
        
    def __getAllPossible(self, row, col):
        """
        Returns all possible values for a particular cell
        """
        filt = lambda cur, inp: [n for n in cur if n not in inp]
        res = filt(range(1, 9+1), self.__puzzle[row])
        res = filt(res, [l[col] for l in self.__puzzle])
        rBegin = row - row%3
        cBegin = col - col%3
        return filt(res, [self.__puzzle[i][j] for i in range(rBegin, rBegin+3) for j in range(cBegin, cBegin+3)])
    
    def __validateGrid(self):
        """
        Validates if puzzle's grid is valid. Raises exception if grid is invalid.
        """
        if len(self.__puzzle) != 9 or not all(len(l) == 9 for l in self.__puzzle):
            raise RuntimeError("Invalid grid")
        if 9*9-(zeros := sum([l.count(0) for l in self.__puzzle])) < 17 or zeros == 0:
            raise RuntimeError("Invalid grid")
        if not all([type(n) == int for l in self.__puzzle for n in l if n != 0]):
            raise RuntimeError("Invalid grid")
        self.__validatePuzzle()
        
    def __validatePuzzle(self):
        """
        Validates if puzzle is valid. Raises exception if puzzle is invalid.
        """
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
        """
        Tries to solve puzzle using recursive backtracking algorithm.
        """
        row, col = 0,0
        possibles = None
        # List of values that are going to be set in the current iteration
        reset = [] 

        # Iterate over all unknown cells and pick the cell with the least number of possible values.
        # If number of possibles is equal to 1 fill it and continue
        for i,j in self.__unknowns:
            ps = self.__getAllPossible(i, j)
            if len(ps) == 0:
                # It means the puzzle is became invalid
                for i,j in reset:
                    self.__puzzle[i][j] = 0
                return
            elif len(ps) == 1:
                # Only one possible value, so just put it and continue
                self.__puzzle[i][j] = ps[0]
                reset.append((i,j))
            elif possibles is None or len(ps) < len(possibles):
                possibles = ps
                row = i
                col = j
                
        if possibles is None:
            # It means we found solution. Store it if it is the first one otherwise raise an exception
            if self.__solution is not None:
                raise RuntimeError("Multiple solutions")
            self.__solution = copy.deepcopy(self.__puzzle)
            return
        
        # Update possilbes because it might be changed after 1 possible-cells filled
        possibles = self.__getAllPossible(row, col)
        if len(possibles) == 0:
            for i,j in reset:
                self.__puzzle[i][j] = 0
            return
        
        reset.append((row,col))

        # Update uknowns for the next iteration
        self.__unknowns = [c for c in self.__unknowns if c not in reset]
        
        # Try to set possible values one by one and solve puzzle recursively
        for p in possibles:
            self.__puzzle[row][col] = p
            self.__solve()
            
        # Reset values and unknowns
        for i,j in reset:
            self.__puzzle[i][j] = 0
        self.__unknowns.extend(reset)
    
    def solve(self):
        self.__validateGrid()

        # Create list of all unknown cells
        self.__unknowns = [(i,j) for i,l in enumerate(self.__puzzle) for j,n in enumerate(l) if n == 0]

        self.__solve()
        if self.__solution is not None:
            return self.__solution
        raise RuntimeError("No solution")

def sudoku_solver(puzzle):
    solver = SudokuSolver(puzzle)
    return solver.solve()
