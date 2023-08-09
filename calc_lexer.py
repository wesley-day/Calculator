import re

whitespace_re = re.compile(r"\s+")
tok_patterns = [
    ("LPAREN", re.compile(r"^\(")),
    ("RPAREN", re.compile(r"^\)")),
    ("POW", re.compile(r"^\^")),
    ("MULT", re.compile(r"^\*")),
    ("DIV", re.compile(r"^/")),
    ("ADD", re.compile(r"^\+")),
    ("SUB", re.compile(r"^-")),
    ("FACT", re.compile(r"^!")),
    ("ANS", re.compile(r"^ans")),
    ("FUN", re.compile(r"^(sqrt|exp|sin|cos|tan|ln|lg|log|floor|ceil)")),
    ("CONST", re.compile(r"^(pi|e)")),
    ("VAR", re.compile(r"^x")),
    ("NUM", re.compile(r"^(\d+\.\d+|\.\d+|\d+)")),
]

def tokenize(line, ans):
    line = re.sub(whitespace_re, "", line)
    toks = []
    while line:
        for tok, pattern in tok_patterns:
            _match = re.match(pattern, line)
            if _match:
                if tok == "ANS":
                    if ans == None:
                        raise ValueError("Invalid input (ans is not yet defined)")
                    toks.append(("NUM", ans))
                elif tok == "NUM":
                    toks.append((tok, float(_match.group())))
                elif tok == "FUN" or tok == "CONST" or tok == "VAR":
                    toks.append((tok, _match.group()))
                else:
                    toks.append((tok, None))
                line = re.sub(pattern, "", line, count=1)
                break
        else:
            raise ValueError("Invalid input")
    
    return toks