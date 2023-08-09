import numpy as np
import matplotlib.pyplot as plt
import calc_lexer as cl
import calc_parser as cp

# TODO

ROUND_THRESH = 1.0e-12
NUM_SAMPLES = 1000
domain = (-10, 10)
ans = None

def set_domain(min_x, max_x):
    global domain
    domain = (min_x, max_x)
    print(domain)

def graph(expr):
    y = expr.evaluate()
    plt.figure(figsize=(6, 6))
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)
    plt.plot(np.linspace(*domain, num=NUM_SAMPLES), y)
    plt.grid(True)
    plt.show()

def interpret(expr, graph_mode):
    if graph_mode:
        graph(expr)
    else:
        val = expr.evaluate()
        if abs(val - round(val)) <= ROUND_THRESH:
            val = round(val)
        return val

def configure():
    print("Edit graph domain (domain), number of samples to take for x (samples),",
          "or rounding threshold (thresh)?\n> ", end="")
    arg = input()
    if arg == "domain":
        print("Min x = ", end="")
        arg = input()
        min_x = int(arg) if arg.isnumeric() else None
        print("Max x = ", end="")
        arg = input()
        max_x = int(arg) if arg.isnumeric() else None
        if not min_x or not max_x or min_x >= max_x:
            print("Invalid input")
        else:
            set_domain(min_x, max_x)
    elif arg == "samples":
        print("New number of samples = ", end="")
        arg = input()
        if not arg.isnumeric():
            print("Invalid input")
        else:
            global NUM_SAMPLES
            NUM_SAMPLES = int(arg)
    elif arg == "thresh":
        print("New rounding threshold = ", end="")
        arg = input()
        if not arg.isnumeric():
            print("Invalid input")
        else:
            global ROUND_THRESH
            ROUND_THRESH = float(arg)


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
        expr, graph_mode = cp.parse(toks)
        ans = interpret(expr, graph_mode)
        print(ans)
    except (ValueError, cp.ParseError) as e:
        print("Error:", e)
        return True
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