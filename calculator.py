import numpy as np
import plotly.graph_objects as go
import calc_lexer as cl
import calc_parser as cp

# TODO
# 6/2(1+2) should equal 9 not 1
    # parser is right associative, making it left associative might be difficult
# complex numbers
# add ability to create functions on the fly e.g. f(x) = 10x,
#   will need to remove graphing or change how it is called

ROUND_THRESH = 1.0e-12
NUM_SAMPLES = 1000
DOMAIN = (-10, 10)
COMMAS = True
ans = None

def graph(expr):
    y = expr.evaluate()
    x = np.linspace(*DOMAIN, num=NUM_SAMPLES)
    trace = go.Scatter(x=x, y=y)
    
    layout = go.Layout(
        showlegend=False,
        xaxis_showline=True,
        yaxis_showline=True,
        xaxis_zeroline=True,
        yaxis_zeroline=True,
        xaxis_zerolinewidth=1,
        yaxis_zerolinewidth=1,
        xaxis_zerolinecolor='black',
        yaxis_zerolinecolor='black',
        xaxis_showgrid=True,
        yaxis_showgrid=True,
    )
    
    fig = go.Figure(data=[trace], layout=layout)
    fig.show()

def interpret(expr, graph_mode):
    if graph_mode:
        graph(expr)
    else:
        val = expr.evaluate()
        if abs(val - round(val)) <= ROUND_THRESH:
            val = round(val)
        print(f"{val:,}" if COMMAS else val)
        return val

def configure():
    print("Edit graph DOMAIN (domain), number of samples to take for x (samples),")
    print("rounding threshold (thresh), or toggle commas (commas)?\n> ", end="")
    arg = input()
    if arg == "domain":
        print("Min x = ", end="")
        arg = input()
        min_x = int(arg) if arg.isnumeric() else None
        print("Max x = ", end="")
        arg = input()
        max_x = int(arg) if arg.isnumeric() else None
        if min_x is None or max_x is None or min_x >= max_x:
            print("Invalid input")
        else:
            global DOMAIN
            DOMAIN = (min_x, max_x)
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
        expr, graph_mode = cp.parse(toks)
        ans = interpret(expr, graph_mode)
    except (ValueError, TypeError, cp.ParseError, OverflowError) as e:
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