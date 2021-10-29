class WI:
    def __init__(self, code, inp = ''):
        self.__code = ''.join(c for c in code if c in (' ', '\t', '\n'))
        self.__inp = inp
        self.__out = ""
        self.__pc = 0
        self.__inPos = 0
        self.__stack = []
        self.__heap = {}
        self.__labels = {}
        self.__exitProgram = False
        self.__exitSubRoutine = False
        self.__subN = 0
        self.__commands = {
            ' ': self.__stackCmd,
            '\t ': self.__arithmeticCmd,
            '\t\t': self.__heapCmd,
            '\t\n': self.__ioCmd,
            '\n': self.__flowCmd
        }
        self.__stackCommands = {
            ' ': self.__push,
            '\t ': self.__duplicateN,
            '\t\n': self.__discardN,
            '\n ': self.__duplicate,
            '\n\t': self.__swap,
            '\n\n': self.__discard
        }
        self.__arithmeticCommands = {
            '  ': self.__add,
            ' \t': self.__sub,
            ' \n': self.__mul,
            '\t ': self.__div,
            '\t\t': self.__mod,
        }
        self.__heapCommands = {
            ' ': self.__store,
            '\t': self.__load
        }
        self.__ioCommands = {
            '  ': self.__chOut,
            ' \t': self.__nOut,
            '\t ': self.__chIn,
            '\t\t': self.__nIn
        }
        self.__flowCommands = {
            '  ': self.__mark,
            ' \t': self.__call,
            ' \n': self.__jump,
            '\t ': self.__jump2,
            '\t\t': self.__jump3,
            '\t\n': self.__exitSub,
            '\n\n': self.__exit,
        }
        
    def __mark(self):
        label = self.__parseLabel()
        if self.__running:
            return
        if label in self.__labels.keys():
            raise RuntimeError(f"Label {label} already exists")
        self.__labels[label] = self.__pc
        
    def __call(self):
        label = self.__parseLabel()
        if not self.__running:
            return
        if label not in self.__labels.keys():
              raise RuntimeError(f"Label {label} wasn't found")
        pos = self.__pc
        self.__pc = self.__labels[label]
        self.__subN += 1
        while self.__pc < len(self.__code) and not self.__exitProgram and not self.__exitSubRoutine:
            success = False
            for k in self.__commands.keys():
                if self.__code[self.__pc:].startswith(k):
                    success = True
                    self.__pc += len(k)
                    self.__commands[k]()
                    break
            if not success:
                raise RuntimeError("Bad command")
        self.__subN -= 1
        if self.__exitProgram:
            return
        if not self.__exitSubRoutine:
            raise RuntimeError("Exit subroutine is missing")
        self.__exitSubRoutine = False
        self.__pc = pos
        
    def __jump(self):
        label = self.__parseLabel()
        if not self.__running:
            return
        if label not in self.__labels.keys():
            raise RuntimeError(f"Label {label} doesn't exist")
        self.__pc = self.__labels[label]
        
    def __jump2(self):
        label = self.__parseLabel()
        if not self.__running:
            return
        v = self.__stack.pop()
        if v == 0:
            if label not in self.__labels.keys():
                raise RuntimeError(f"Label {label} doesn't exist 2")
            self.__pc = self.__labels[label]
        
    def __jump3(self):
        label = self.__parseLabel()
        if not self.__running:
            return
        v = self.__stack.pop()
        if v < 0:
            if label not in self.__labels.keys():
                raise RuntimeError(f"Label {label} doesn't exist 3")
            self.__pc = self.__labels[label]
        
    def __exitSub(self):
        if not self.__running:
            return
        if self.__subN == 0:
            raise RuntimeError("Return outside of subroutine")
        self.__exitSubRoutine = True
        
    def __exit(self):
        if not self.__running:
            return
        self.__exitProgram = True
        
    def __chOut(self):
        if not self.__running:
            return
        if len(self.__stack) < 1:
            raise RuntimeError("Stack is empty")
        self.__out += chr(self.__stack.pop())
        
    def __nOut(self):
        if not self.__running:
            return
        if len(self.__stack) < 1:
            raise RuntimeError("Stack is empty")
        self.__out += str(self.__stack.pop())
        
    def __chIn(self):
        if not self.__running:
            return
        if self.__inPos + 1 > len(self.__inp):
            raise RuntimeError("Input ended")
        a = self.__inp[self.__inPos]
        self.__inPos += 1
        if len(self.__stack) < 1:
            raise RuntimeError("Stack is empty")
        b = self.__stack.pop()
        self.__heap[b] = ord(a)
        
    def __nIn(self):
        if not self.__running:
            return
        base = 10
        if self.__inp[self.__inPos].startswith("0x"):
            base = 16
        elif self.__inp[self.__inPos].startswith("0b"):
            base = 2
        elif self.__inp[self.__inPos].startswith("0"):
            base = 8
        ind = self.__inp[self.__inPos:].find('\n')
        if ind == -1:
            raise RuntimeError("Number must be ended with new line")
        ind += self.__inPos
        a = int(self.__inp[self.__inPos:ind], base)
        self.__inPos = ind + 1
        if len(self.__stack) < 1:
            raise RuntimeError("Stack is empty")
        b = self.__stack.pop()
        self.__heap[b] = a
        
    def __store(self):
        if not self.__running:
            return
        if len(self.__stack) < 2:
            raise RuntimeError("Stack is less than 2")
        a = self.__stack.pop()
        b = self.__stack.pop()
        self.__heap[b] = a
        
    def __load(self):
        if not self.__running:
            return
        if len(self.__stack) < 1:
            raise RuntimeError("Stack is empty")
        a = self.__stack.pop()
        if a not in self.__heap.keys():
            raise RuntimeError(f"'{a}' no such address in heap")
        self.__stack.append(self.__heap[a])
        
    def __mod(self, a, b):
        if not self.__running:
            return
        if a == 0:
            raise RuntimeError("Modulo by 0")
        self.__stack.append(int(b%a))
        
    def __div(self, a, b):
        if not self.__running:
            return
        if a == 0:
            raise RuntimeError("Division by 0")
        self.__stack.append(int(b//a))
        
    def __mul(self, a, b):
        if not self.__running:
            return
        self.__stack.append(a*b)
        
    def __sub(self, a, b):
        if not self.__running:
            return
        self.__stack.append(b-a)
        
    def __add(self, a, b):
        if not self.__running:
            return
        self.__stack.append(a+b)
        
    def __push(self):
        n = self.__parseNumber()
        if not self.__running:
            return
        self.__stack.append(n)
        
    def __duplicateN(self):
        n = self.__parseNumber()
        if not self.__running:
            return
        if n < 0:
            raise RuntimeError("N must be > 0")
        if len(self.__stack) < n + 1:
            raise RuntimeError("Not enough values in stack")
        self.__stack.append(self.__stack[-n-1])
        
    def __discardN(self):
        n = self.__parseNumber()
        if not self.__running:
            return
        if n < 0 or n >= len(self.__stack):
            del self.__stack[:-1]
        else:
            del self.__stack[-n-1:-1]
        
    def __duplicate(self):
        if not self.__running:
            return
        if len(self.__stack) < 1:
            raise RuntimeError("Empty stack")
        self.__stack.append(self.__stack[-1])
        
    def __swap(self):
        if not self.__running:
            return
        if len(self.__stack) < 2:
            raise RuntimeError("Stack is less than 2")
        self.__stack[-1], self.__stack[-2] = self.__stack[-2], self.__stack[-1]
        
    def __discard(self):
        if not self.__running:
            return
        if len(self.__stack) < 1:
            raise RuntimeError("Empty stack")
        self.__stack.pop()
        
    def __parseLabel(self):
        ind = self.__code[self.__pc:].find('\n')
        if ind == -1:
            raise RuntimeError("Bad label")
        ind += self.__pc + 1
        label = self.__code[self.__pc:ind]
        self.__pc = ind
        return label
        
    def __parseNumber(self):
        if self.__code[self.__pc] not in ('\t', ' '):
            raise RuntimeError("Bad sign")
        sign = -1 if self.__code[self.__pc] == '\t' else 1
        self.__pc += 1
        val = 0
        while self.__code[self.__pc] != '\n' and self.__pc < len(self.__code):
            val = val*2 + (0 if self.__code[self.__pc] == ' ' else 1)
            self.__pc += 1
        if self.__code[self.__pc] != '\n':
            raise RuntimeError("Terminal is missing")
        self.__pc += 1
        return val * sign
        
    def __stackCmd(self):
        for k in self.__stackCommands.keys():
            if self.__code[self.__pc:].startswith(k):
                self.__pc += len(k)
                self.__stackCommands[k]()
                return
        raise RuntimeError("Stack command not found")
        
    def __arithmeticCmd(self):
        for k in self.__arithmeticCommands.keys():
            if self.__code[self.__pc:].startswith(k):
                self.__pc += len(k)
                a, b = 0, 0
                if self.__running:
                    if len(self.__stack) < 2:
                        raise RuntimeError("Less than 2")
                    a = self.__stack.pop()
                    b = self.__stack.pop()
                self.__arithmeticCommands[k](a, b)
                return
        raise RuntimeError("Arithmetic command not found")
        
    def __heapCmd(self):
        for k in self.__heapCommands.keys():
            if self.__code[self.__pc:].startswith(k):
                self.__pc += len(k)
                self.__heapCommands[k]()
                return
        raise RuntimeError("Heap command not found")
        
    def __ioCmd(self):
        for k in self.__ioCommands.keys():
            if self.__code[self.__pc:].startswith(k):
                self.__pc += len(k)
                self.__ioCommands[k]()
                return
        raise RuntimeError("IO command not found")
        
    def __flowCmd(self):
        for k in self.__flowCommands.keys():
            if self.__code[self.__pc:].startswith(k):
                self.__pc += len(k)
                self.__flowCommands[k]()
                return
        raise RuntimeError("Flow command not found")
    
    def run(self):
        self.__running = False
        while self.__pc < len(self.__code):
            success = False
            for k in self.__commands.keys():
                if self.__code[self.__pc:].startswith(k):
                    success = True
                    self.__pc += len(k)
                    self.__commands[k]()
                    break
            if not success:
                raise RuntimeError("Bad command")
        self.__running = True
        self.__pc = 0
        while self.__pc < len(self.__code) and not self.__exitProgram:
            success = False
            for k in self.__commands.keys():
                if self.__code[self.__pc:].startswith(k):
                    success = True
                    self.__pc += len(k)
                    self.__commands[k]()
                    break
            if not success:
                raise RuntimeError("Bad command")
        if not self.__exitProgram:
            raise RuntimeError("Exit is missing")
        return self.__out

def whitespace(code, inp = ''):
    wi = WI(code, inp)
    return wi.run()
