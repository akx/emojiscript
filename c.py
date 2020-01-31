import sys
import io
import unicodedata
import json

input = io.StringIO(sys.stdin.read())


output = sys.stdout


def get_tok():
    while True:
        c = input.read(1)
        if not c.isspace():
            break
    if not c:
        return None
    assert unicodedata.category(c) == "So"
    return c


def need_tok():
    c = get_tok()
    assert c
    return c


def need_val():
    val = []
    while True:
        c = input.read(1)
        assert c, "eof"
        if c == "🛑":
            break
        val.append(c)
    return val


def c2js(c):
    return f"_{ord(c):x}"


stack = []
while True:
    tok = get_tok()
    if not tok:
        break
    if tok == "👉":  # assign
        idfr = need_tok()
        val = "".join(need_val())
        if not val.isdigit():
            val = json.dumps(val)
        output.write(f"let {c2js(idfr)} = {val};\n")
    elif tok == "🔁":  # while
        idfr = need_tok()
        output.write(f"while({c2js(idfr)}){{\n")
        stack.append("}\n")
    elif tok == "👇":  # dec
        idfr = need_tok()
        output.write(f"{c2js(idfr)}--;\n")
    elif tok == "📣":  # print
        idfr = need_tok()
        output.write(f"console.log({c2js(idfr)});\n")
    elif tok == "🎉":  # end
        if not stack:
            output.write("process.exit(0);\n")
            break
        output.write(stack.pop(-1))
    else:
        raise RuntimeError(tok)
