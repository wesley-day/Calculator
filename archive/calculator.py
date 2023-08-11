import numpy as np
import plotly.graph_objects as go
import calc_lexer as cl
import calc_parser as cp

# TODO
# complex numbers

ROUND_THRESH = 1.0e-12
COMMAS = False
ans = None

def interpret(expr, graph_mode):
    val = expr.evaluate()
    if abs(val - round(val)) <= ROUND_THRESH:
        val = round(val)
    print(f"{val:,}" if COMMAS else val)
    return val

def configure():
    print("Edit rounding threshold (thresh) or toggle commas (commas)?\n> ", end="")
    arg = input()
    if arg == "thresh":
        print("New rounding threshold = ", end="")
        arg = input()
        try:
            global ROUND_THRESH
            ROUND_THRESH = float(arg)
        except:
            print("Invalid input")
    elif arg == "commas":
        global COMMAS
        COMMAS = not COMMAS
        print("Commas now", "on" if COMMAS else "off")


def process_input(line):
    if line == "exit" or line == "quit":
        return False
    if line == "":
        return True
    if line == "configure" or line == "config":
        configure()
        return True
    try:
        global ans
        toks = cl.tokenize(line, ans)
        if not toks:
            return True
        expr = cp.parse(toks)
        ans = interpret(expr)
    except (ValueError, cp.ParseError, OverflowError) as e:
        if isinstance(e, OverflowError):
            e = "Calculation too large"
        print("Error:", e)
    return True

def main():
    try:
        print("calc> ", end="")
        line = input()
        while process_input(line):
            print("calc> ", end="")
            line = input()
    except (KeyboardInterrupt, EOFError):
        print()
        return

if __name__ == "__main__":
    main()