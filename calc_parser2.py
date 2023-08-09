import numpy as np
import calculator as calc

class ParseError(Exception):
    pass

# An expression is either a Value, Function, or Binop

class Value:
    def __init__(self, val):
        self.val = val
        self.neg = 1

    def evaluate(self):
        return self.neg * self.val

class Function:
    def sqrt(x):
        if x < 0:
            raise ValueError("Cannot take square root of value < 0")
        return np.sqrt(x)
    
    # still doesn't work
    def tan(x):
        return Binop.div(np.sin(x), np.cos(x))

    def ln(x):
        if x <= 0:
            raise ValueError("Cannot take log of value <= 0")
        return np.log(x)
    
    def lg(x):
        if x <= 0:
            raise ValueError("Cannot take log of value <= 0")
        return np.log2(x)
    
    def log(x):
        if x <= 0:
            raise ValueError("Cannot take log of value <= 0")
        return np.log10(x)

    functions = {
        "sqrt": sqrt,
        "exp": np.exp,
        "sin": np.sin,
        "cos": np.cos,
        "tan": tan,
        "ln": ln,
        "lg": lg,
        "log": log
    }

    def __init__(self, fun, expr):
        self.fun = fun
        self.expr = expr
        self.neg = 1

    def evaluate(self):
        return self.neg * Function.functions[self.fun](self.expr.evaluate())

class Binop:
    def div(x, y):
        if y == 0:
            raise ValueError("Cannot divide by 0")
        return x / y

    operations = {
        "POW": (lambda x, y: x ** y),
        "MULT": (lambda x, y: x * y),
        "DIV": div,
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

constants = {
    "pi": np.pi,
    "e": np.e
}

def match_tok(target, toks):
    tok = toks[0][0]
    if target != tok:
        raise ParseError(f"Target {target} did not match {tok}")
    return toks[1:]
     
# Every expression must start with LPAREN, FUN, VAR, or NUM.
def parse_primary(toks):
    tok = toks[0]
    if tok[0] == "LPAREN":
        toks_left, expr, graph_mode = parse_additive(toks[1:])
        toks_left = match_tok("RPAREN", toks_left)
        return toks_left, expr, graph_mode
    if tok[0] == "FUN":
        toks_left = match_tok("LPAREN", toks[1:])
        toks_left, expr, graph_mode = parse_additive(toks_left)
        toks_left = match_tok("RPAREN", toks_left)
        return toks_left, Function(tok[1], expr), graph_mode
    if tok[0] == "CONST":
        return toks[1:], Value(constants[tok[1]]), False
    if tok[0] == "VAR":
        return toks[1:], Value(np.linspace(*calc.domain, num=calc.NUM_SAMPLES)), True
    if tok[0] == "NUM":
        return toks[1:], Value(tok[1]), False
    if tok[0] == "SUB":
        toks_left, expr, graph_mode = parse_primary(toks[1:])
        expr.neg = -1
        return toks_left, expr, graph_mode 
    raise ParseError("Invalid input")

def parse_exponential(toks):
    toks1, expr1, graph_mode1 = parse_primary(toks)
    if not toks1 or toks1[0][0] != "POW":
        return toks1, expr1, graph_mode1
    toks2, expr2, graph_mode2 = parse_exponential(toks1[1:])
    return toks2, Binop("POW", expr1, expr2), graph_mode1 or graph_mode2

def parse_multiplicitive(toks):
    toks1, expr1, graph_mode1 = parse_exponential(toks)
    if not toks1 or toks1[0][0] != "MULT" and toks1[0][0] != "DIV":
        return toks1, expr1, graph_mode1
    op = "MULT" if toks1[0][0] == "MULT" else "DIV"
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
        # Should not cause problems if input is something like '2 1'
        # because whitespace is removed.
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
        raise ParseError("Unparsed tokens:", toks_left)
    return expr, graph_mode