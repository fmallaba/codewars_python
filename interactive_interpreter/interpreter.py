import operator
import re
from types import FunctionType

def tokenize(expression):
    if expression == "":
        return []

    regex = re.compile("\s*(=>|[-+*\/\%=\(\)]|[A-Za-z_][A-Za-z0-9_]*|[0-9]*\.?[0-9]+)\s*")
    tokens = regex.findall(expression)
    return [s for s in tokens if not s.isspace()]

class Interpreter:
    def __init__(self):
        self.vars = {}
        self.functions = {}
        self.prec = {'=': 0, '+':1 , '-':1, '/':2, '*':2, '%':2}
        self.ops = {
            "+": (self.var_vals_dec(operator.add)),
            "-": (self.var_vals_dec(operator.sub)),
            "*": (self.var_vals_dec(operator.mul)),
            "/": (self.var_vals_dec(operator.truediv)),
            "%": (self.var_vals_dec(operator.mod)),
            "=": (self.assign),
        }
        self.vars = dict()
        self.funcs = dict()
        
    def var_vals_dec(self, func):
        def get_val(arg):
            if isinstance(arg, str) and not arg.isdigit():
                if arg not in self.vars:
                    raise RuntimeError(f'ERROR: There is no variable {arg}')
                return int(self.vars[arg])
            return int(arg)
        def wrap(a, b):
            a = get_val(a)
            b = get_val(b)
            return int(func(a, b))
        
        return wrap
        
    def assign(self, var, val):
        if isinstance(var, int) or var.isdigit():
            raise RuntimeError(f'ERROR: Bad variable {var}')
        val = int(val)
        if var in self.funcs:
            raise RuntimeError(f'ERROR: There is function with name {var}')
        self.vars[var] = val
        return val
        
    def _to_rpn(self, tokens):
        output = []
        stack = []
        for item in tokens:
            if item in self.funcs:
                stack.append(item)
            elif item in self.ops:
                while stack and not stack[-1] == '(' \
                    and (stack[-1] in self.funcs \
                    or self.prec[stack[-1]] > self.prec[item] \
                    or (self.prec[item] != 0 and self.prec[stack[-1]] == self.prec[item])):
                    output.append(stack.pop())
                stack.append(item)
            elif item == "(":
                stack.append("(")
            elif item == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                stack.pop()
            else:
                output.append(item)
        while stack:
            output.append(stack.pop())
        return output
    
    def _declare_func(self, tokens):
        if tokens[1] in self.vars:
            raise RuntimeError(f'ERROR: There is variable with name {var}')
        arg_stop = tokens.index('=>')
        args = tokens[2:arg_stop]
        for token in tokens[arg_stop+1:]:
            if token not in self.ops and not token.isdigit() and token not in ('(', ')') and token not in args:
                raise RuntimeError(f'ERROR: Invalid variable name {token}')
        
        f_code = compile(f'def {tokens[1]}({",".join(args)}): return {"".join(tokens[arg_stop+1:])}', "<int>", "exec")
        f_func = FunctionType(f_code.co_consts[0], {}, tokens[1])
        self.funcs[tokens[1]] = (f_func, len(args))

    def _eval(self, tokens):
        stack = []

        for token in tokens:
            if token in self.ops:
                arg2 = stack.pop()
                arg1 = stack.pop()
                result = self.ops[token](arg1, arg2)
                stack.append(result)
            elif token in self.funcs:
                arg_num = self.funcs[token][1]
                args = [int(stack.pop()) for _ in range(arg_num)]
                result = int(self.funcs[token][0](*args))
                stack.append(result)
            else:
                stack.append(token)

        if len(stack) > 1:
            raise RuntimeError('Bad input')
        result = stack.pop()
        if isinstance(result, int):
            return result
        elif result.isdigit():
            return int(result)
        return self.vars[result]

    def input(self, expression):
        tokens = tokenize(expression)
        if len(tokens) == 0:
            return ''
        if '=>' in tokens:
            self._declare_func(tokens)
            return ''
        rpn = self._to_rpn(tokens)
        result = self._eval(rpn)
        return result
