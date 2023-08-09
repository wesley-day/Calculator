import numpy as np
import matplotlib.pyplot as plt
import calc_lexer as cl
import calc_parser as cp

# TODO
# 3.900000000 ^ 03480 returns 0
# 0123.00 returns 0
# handle undefined tan values
# let value come into next line
# add factorial

ROUND_THRESH = 1.0e-12
NUM_SAMPLES = 1000
domain = (-10, 10)

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
        print(val)

def process_input(line):
    if line == "exit" or line == "quit":
        return False
    if line == "":
        return True
    if line == "configure" or line == "config":
        print("Min x = ", end="")
        min_x = int(input())
        print("Max x = ", end="")
        max_x = int(input())
        if min_x >= max_x:
            print("Min x must be less than max x")
        else:
            set_domain(min_x, max_x)
        return True
    try:
        toks = cl.tokenize(line)
        expr, graph_mode = cp.parse(toks)
        interpret(expr, graph_mode)
    except Exception as e:
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
    except KeyboardInterrupt:
        print()
        return

if __name__ == "__main__":
    main()