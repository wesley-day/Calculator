import numpy as np
import matplotlib.pyplot as plt
import calc_lexer as cl
import calc_parser as cp

# TODO
# add factorial

ROUND_THRESH = 1.0e-12

def graph(expr):
    y = expr.evaluate()
    plt.figure(figsize=(6, 6))
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)
    plt.plot(np.linspace(*cp.domain), y)
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

def main():
    # print("===============Calculator===============")
    try:
        while True:
            print("calc>", end="")
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
            try:
                toks = cl.tokenize(line)
                expr, graph_mode = cp.parse(toks)
            except (ValueError, cp.ParseError) as e:
                print(e)
                continue
            interpret(expr, graph_mode)
    except KeyboardInterrupt:
        print()
        return

if __name__ == "__main__":
    main()