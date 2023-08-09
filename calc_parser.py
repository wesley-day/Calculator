import numpy as np
import calculator as calc

class ParseError(Exception):
    pass

# An expression is either a Value, Function, or Binop

class Value:
    def __init__(self, val):
        self.val = val

    def evaluate(self):
        return self.val

class Function:
    functions = {
        "sqrt": np.sqrt,
        "exp": np.exp,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan
    }

    def __init__(self, fun, expr):
        self.fun = fun
        self.expr = expr

    def evaluate(self):
        return Function.functions[self.fun](self.expr.evaluate())

class Binop:
    operations = {
        "POW": (lambda x, y: x ** y),
        "MULT": (lambda x, y: x * y),
        "DIV": (lambda x, y: x / y),
        "ADD": (lambda x, y: x + y),
        "SUB": (lambda x, y: x - y)
    }

    def __init__(self, op, expr1, expr2):
        self.op = op
        self.expr1 = expr1
        self.expr2 = expr2

    def evaluate(self):
        return Binop.operations[self.op](self.expr1.evaluate(), self.expr2.evaluate())

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
    toks2, expr2, graph_mode2 = parse_additive(toks1[1:]) # this might not work as intended
    return toks2, Binop(op, expr1, expr2), graph_mode1 or graph_mode2

# Makes implied multiplication explicit (e.g. (2)(2) -> (2) * (2))
def preprocess(toks):
    new_toks = []
    for i, (token, value) in enumerate(toks):
        currIsVal = token in {"RPAREN", "CONST", "VAR", "NUM"}
        nextIsVal = i < len(toks) - 1 and toks[i + 1][0] in {"LPAREN", "FUN", "CONST", "VAR", "NUM"}

        # Should not cause problems if input is something like '2 1'
        # because whitespace is removed.
        if currIsVal and nextIsVal:
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