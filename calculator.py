import numpy as np
import matplotlib.pyplot as plt
import calc_lexer as cl
import calc_parser as cp

def graph(expr):
    y = expr.evaluate() if isinstance(expr, cp.Binop) else expr
    plt.figure(figsize=(6, 6))
    plt.axhline(0, color='black', linewidth=2)  # Horizontal line at y=0
    plt.axvline(0, color='black', linewidth=2)  # Vertical line at x=0
    plt.plot(np.linspace(*cp.domain), y)
    plt.axhline(0, color='black', linewidth=2)
    plt.axvline(0, color='black', linewidth=2)
    plt.grid(True)
    plt.show()

def interpret(expr, graph_mode):
    if graph_mode:
        graph(expr)
    else:
        val = expr.evaluate() if isinstance(expr, cp.Binop) else expr
        print(int(val)) if val.is_integer() else print(val)

def main():
    print("===============Calculator===============")
    while True:
        print(">", end="")
        line = input()
        if line == "exit" or line == "quit":
            break
        if line == "":
            continue
        if line == "configure" or line == "config":
            print("Min x = ", end="")
            min_x = input()
            print("Max x = ", end="")
            max_x = input()
            if min_x >= max_x:
                print("Min x must be less than max x")
            else:
                cp.set_domain(min_x, max_x)
            continue

        toks = cl.tokenize(line)
        expr, graph_mode = cp.parse(toks)
        interpret(expr, graph_mode)

if __name__ == "__main__":
    main()