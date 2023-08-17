import numpy as np
import calculator as calc
import math
from collections import defaultdict
import ctypes
from pathlib import Path

UINT64_MAX = 18446744073709551615
INT64_MAX = 9223372036854775807
INT64_MIN = -9223372036854775808

cfunctions = ctypes.CDLL(str(Path(__file__).parent) + "/cfunctions.so")
cfunctions.prime.argtypes = [ctypes.c_uint64]
cfunctions.prime.restype = ctypes.c_int
cfunctions.fib.argtypes = [ctypes.c_int]
cfunctions.fib.restype = ctypes.c_uint64

class ParseError(Exception):
    pass

# Helper functions
def convert_to_number(x: str):
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            raise ValueError("Not a number")

def isnumber(x):
    return isinstance(x, float) or isinstance(x, int)

# An expression is either a Value, Function, or Binop

class Value:
    def __init__(self, val):
        self.val = val
        self.neg = 1

    def evaluate(self):
        return self.neg * self.val

    def __str__(self):
        neg = "" if self.neg == 1 else "-"
        return f"{neg}{str(self.val)}"

class Function:
    def sqrt(x):
        if isnumber(x):
            if x < 0:
                raise ValueError("Cannot take square root of value < 0")
            # Ran into problems with np.sqrt for large integer values
            return math.sqrt(x)
        return np.sqrt(x)

    def tan(x):
        if isnumber(x):
            cosx = np.cos(x)
            if abs(cosx - round(cosx)) < calc.ROUND_THRESH and round(cosx) == 0:
                raise ValueError("Undefined")
        return np.tan(x)

    def ln(x):
        if isnumber(x) and x <= 0:
            raise ValueError("Cannot take log of value <= 0")
        return np.log(x)
    
    def lg(x):
        if isnumber(x) and x <= 0:
            raise ValueError("Cannot take log of value <= 0")
        return np.log2(x)
    
    def log(x):
        if isnumber(x) and x <= 0:
            raise ValueError("Cannot take log of value <= 0")
        return np.log10(x)

    def fact(n):
        if not isinstance(n, int) or n < 0:
            raise ValueError("Undefined")
        return math.factorial(int(n))

    def gcf(n, m):
        if not isinstance(n, int) or not isinstance(m, int):
            raise ValueError("No GCF between non-integers")
        return math.gcd(int(n), int(m))

    def lcm(n, m):
        if not isinstance(n, int) or not isinstance(m, int):
            raise ValueError("No LCM between non-intergers")
        return math.lcm(int(n), int(m))

    def C(n, m):
        if not isinstance(n, int) or not isinstance(m, int):
            raise ValueError("Cannot count combinations of non-integers")
        return math.factorial(n) // (math.factorial(m) * math.factorial(n - m))
    
    def P(n, m):
        if not isinstance(n, int) or not isinstance(m, int):
            raise ValueError("Cannot count permutations of non-integers")
        return math.factorial(n) // math.factorial(n - m)
    
    def prime(n):
        if not isinstance(n, int) or n < 2:
            raise ValueError("Primality is defined only for positive integers",
                             "greater than or equal to 2")
        if n > UINT64_MAX:
            raise ValueError("Calculation too large")
        return cfunctions.prime(n)
    
    def fib(n):
        if not isinstance(n, int) or n < 1:
            raise ValueError("fib requires a natural number")
        if n > 94:
            raise ValueError("Calculation too large")
        return cfunctions.fib(n)

    functions = {
        "sqrt": sqrt,
        "exp": np.exp,
        "sin": np.sin,
        "cos": np.cos,
        "tan": tan,
        "ln": ln,
        "lg": lg,
        "log": log,
        "floor": np.floor,
        "ceil": np.ceil,
        "fact": fact,
        "abs": np.abs,
        "round": np.round,
        "gcf": gcf,
        "lcm": lcm,
        "C": C,
        "P": P,
        "prime": prime,
        "fib": fib
    }

    num_params = defaultdict(lambda: 1, {
        "gcf": 2,
        "lcm": 2,
        "C": 2,
        "P": 2
    })

    def __init__(self, fun, exprs):
        self.fun = fun
        self.exprs = exprs
        self.neg = 1

    def evaluate(self):
        return self.neg * Function.functions[self.fun](*[expr.evaluate() for expr in self.exprs])
    
    def __str__(self):
        neg = "" if self.neg == 1 else "-"
        return f"{neg}{self.fun}({self.exprs})"

class Binop:
    def div(x, y):
        if y == 0:
            raise ValueError("Undefined")
        return x / y

    def mod(x, y):
        if y == 0:
            raise ValueError("Undefined")
        return x % y

    operations = {
        "POW": (lambda x, y: x ** y),
        "MULT": (lambda x, y: x * y),
        "DIV": div,
        "MOD": mod,
        "ADD": (lambda x, y: x + y),
        "SUB": (lambda x, y: x - y)
    }

    def __init__(self, op, expr1, expr2):
        self.op = op
        self.expr1 = expr1
        self.expr2 = expr2
        self.neg = 1

    def evaluate(self):
        return self.neg * Binop.operations[self.op](self.expr1.evaluate(), self.expr2.evaluate())
    
    def __str__(self):
        neg = "" if self.neg == 1 else "-"
        return f"{neg}{self.op}({self.expr1}, {self.expr2})"

constants = {
    "pi": np.pi,
    "e": np.e,
    "G": 6.67408e-11, # m^3 kg^-1 s^-2
    "c": 299_792_458 # m/s
}

def match_tok(target, toks):
    tok = toks[0][0]
    if target != tok:
        raise ParseError(f"Invalid syntax")
    return toks[1:]
     
def parse_primary(toks):
    tok = toks[0]
    if tok[0] == "LPAREN":
        toks_left, expr, graph_mode = parse_additive(toks[1:])
        toks_left = match_tok("RPAREN", toks_left)
        return toks_left, expr, graph_mode
    if tok[0] == "FUN":
        toks_left = match_tok("LPAREN", toks[1:])
        exprs = []
        graph_mode = False
        for i in range(Function.num_params[tok[1]]):
            if i > 0:
                toks_left = match_tok("COMMA", toks_left)
            toks_left, expr, gm = parse_additive(toks_left)
            exprs.append(expr)
            graph_mode |= gm
        toks_left = match_tok("RPAREN", toks_left)
        return toks_left, Function(tok[1], exprs), graph_mode
    if tok[0] == "CONST":
        return toks[1:], Value(constants[tok[1]]), False
    if tok[0] == "VAR":
        return toks[1:], Value(np.linspace(*calc.DOMAIN, num=calc.NUM_SAMPLES)), True
    if tok[0] == "NUM":
        return toks[1:], Value(convert_to_number(tok[1])), False
    if tok[0] == "SUB":
        toks_left, expr, graph_mode = parse_primary(toks[1:])
        expr.neg = -1
        return toks_left, expr, graph_mode
    raise ParseError("Invalid syntax")

def parse_factorial(toks):
    toks, expr, graph_mode = parse_primary(toks)
    if not toks or toks[0][0] != "FACT":
        return toks, expr, graph_mode
    return toks[1:], Function("fact", [expr]), graph_mode

def parse_exponential(toks):
    toks1, expr1, graph_mode1 = parse_factorial(toks)
    if not toks1 or toks1[0][0] != "POW":
        return toks1, expr1, graph_mode1
    toks2, expr2, graph_mode2 = parse_exponential(toks1[1:])
    return toks2, Binop("POW", expr1, expr2), graph_mode1 or graph_mode2

def parse_multiplicitive(toks):
    toks1, expr1, graph_mode1 = parse_exponential(toks)
    if not toks1 or toks1[0][0] != "MULT" and toks1[0][0] != "DIV" and toks1[0][0] != "MOD":
        return toks1, expr1, graph_mode1
    op = "MULT" if toks1[0][0] == "MULT" else "DIV" if toks1[0][0] == "DIV" else "MOD"
    toks2, expr2, graph_mode2 = parse_multiplicitive(toks1[1:])
    return toks2, Binop(op, expr1, expr2), graph_mode1 or graph_mode2

def parse_additive(toks):
    toks1, expr1, graph_mode1 = parse_multiplicitive(toks)
    if not toks1 or toks1[0][0] != "ADD" and toks1[0][0] != "SUB":
        return toks1, expr1, graph_mode1
    op = "ADD" if toks1[0][0] == "ADD" else "SUB"
    toks2, expr2, graph_mode2 = parse_additive(toks1[1:])
    return toks2, Binop(op, expr1, expr2), graph_mode1 or graph_mode2

# Makes implied multiplication explicit (e.g. (2)(2) -> (2) * (2) and 5pi -> 5 * pi).
def preprocess(toks):
    new_toks = []
    for i, (token, value) in enumerate(toks):
        if token in {"RPAREN", "FACT", "CONST", "VAR", "NUM"} and \
                (i < len(toks) - 1 and toks[i + 1][0] in {"LPAREN", "FUN", "CONST", "VAR", "NUM"}):
            new_toks.append((token, value))
            new_toks.append(("MULT", None))
        else:
            new_toks.append((token, value))
        
    return new_toks
    
def parse(toks):
    toks = preprocess(toks)
    toks_left, expr, graph_mode = parse_additive(toks)
    if toks_left:
        raise ParseError("Invalid syntax")
    return expr, graph_mode