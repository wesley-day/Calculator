import numpy as np

domain = (-10, 10)

def set_domain(min_x, max_x):
    global domain
    domain = (min_x, max_x)

class ParseError(Exception):
    pass

class Binop:
    operations = {
        "EXP": (lambda x, y: x ** y),
        "MULT": (lambda x, y: x * y),
        "DIV": (lambda x, y: x / y),
        "ADD": (lambda x, y: x + y),
        "SUB": (lambda x, y: x - y)
    }

    # An expression is either a value or a Binop
    def __init__(self, op, expr1, expr2):
        self.op = op
        self.expr1 = expr1
        self.expr2 = expr2

    def evaluate(self):
        val1 = self.expr1.evaluate() if isinstance(self.expr1, Binop) else self.expr1
        val2 = self.expr2.evaluate() if isinstance(self.expr2, Binop) else self.expr2
        return Binop.operations[self.op](val1, val2)


constants = {
    "pi" : np.pi,
    "e" : np.e
}

def match_tok(target, toks):
    tok = toks[0][0]
    if target != tok:
        raise ParseError("Target token did not match")
    return toks[1:]
     
# Every expression must start with LPAREN, VAR, or NUM.
# Constants should have already been converted into NUMs.
def parse_primary(toks):
    tok = toks[0]
    if tok[0] == "LPAREN":
        toks_left, expr, graph_mode = parse_additive(toks[1:])
        toks_left = match_tok("RPAREN", toks_left)
        return toks_left, expr, graph_mode
    if tok[0] == "CONST":
        return toks[1:], constants[tok[1]], False
    if tok[0] == "VAR":
        return toks[1:], np.linspace(*domain), True
    if tok[0] == "NUM":
        return toks[1:], tok[1], False

def parse_exponential(toks):
    toks1, expr1, graph_mode1 = parse_primary(toks)
    if not toks1 or toks1[0][0] != "EXP":
        return toks1, expr1, graph_mode1
    toks2, expr2, graph_mode2 = parse_exponential(toks1[1:])
    return toks2, Binop("EXP", expr1, expr2), graph_mode1 or graph_mode2

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

# Should only be called by the main method.
# Functions within the parsing process should call _parse.
def parse(toks):
    # Making implied multiplication explicit (e.g. 5x + 2 -> 5 * x + 2)
    # and replacing constants with their values (e.g. pi -> 3.14159...)
    new_toks = []
    for i, (token, value) in enumerate(toks):
        # this doesn't work
        if (token == "NUM" or token == "CONST") \
                and i < len(toks) - 1 and toks[i + 1][1] in constants.keys():
            new_toks.append((token, value))
            new_toks.append(("MULT", None))
        else:
            if token in constants.keys():
                token, value = "NUM", constants[token]
            new_toks.append((token, value))

    toks_left, expr, graph_mode = parse_additive(new_toks)
    if toks_left:
        raise ParseError("Unparsed tokens:", toks_left)
    return expr, graph_mode