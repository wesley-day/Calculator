import numpy as np
import matplotlib.pyplot as plt
import calc_lexer as cl
import calc_parser as cp

# TODO
# add factorial

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
        print(expr)
        val = expr.evaluate()
        if abs(val - round(val)) <= ROUND_THRESH:
            val = round(val)
        return val

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