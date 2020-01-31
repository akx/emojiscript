import sys
import io
import unicodedata
import json
import re
import enum

input = io.StringIO(sys.stdin.read())


output = sys.stdout


def tokenize(stream):
    in_comment = 0
    val_buf = []

    def dump_val():
        if val_buf:
            yield ("v", val_buf[:])
        val_buf[:] = []

    while True:
        c = input.read(1)
        if not c:
            break
        if c.isspace():
            continue
        if c == "(":
            in_comment += 1
            continue
        if c == ")":
            assert in_comment
            in_comment -= 1
            continue
        if in_comment:
            continue
        if c == "\\":
            val_buf.append(input.read(1))
            continue
        if unicodedata.category(c) == "So":
            yield from dump_val()
            yield ("t", c)
        else:
            val_buf.append(c)
    yield from dump_val()


def c2js(c):
    return f"_{ord(c):x}"


def asjs(vb):
    val = "".join(vb)
    if not val.isdigit():
        return json.dumps(val)
    return val


def w(s):
    output.write("  " * len(stack) + str(s))


tokens = list(tokenize(sys.stdin))


def need_tok():
    assert tokens[0][0] == "t", "needed a token"
    return tokens.pop(0)[1]


def need_val():
    assert tokens[0][0] == "v", "needed a value"
    return tokens.pop(0)[1]


def take():
    return tokens.pop(0)


stack = []
while tokens:
    tok = need_tok()
    if tok == "👉":  # assign
        idfr = need_tok()
        w(f"let {c2js(idfr)} = {asjs(need_val())};\n")
    elif tok == "🔁":  # while
        w(f"while({c2js(need_tok())}){{\n")
        stack.append("}\n")
    elif tok == "👇":  # dec
        w(f"{c2js(need_tok())}--;\n")
    elif tok == "☝️":  # inc
        w(f"{c2js(need_tok())}++;\n")
    elif tok == "📣":  # print
        t, v = take()
        if t == "t":
            w(f"console.log({c2js(v)});\n")
        else:
            w(f"console.log({asjs(v)});\n")
    elif tok == "🎉":  # end
        if not stack:
            w("process.exit(0);\n")
            break
        w(stack.pop(-1))
    else:
        raise RuntimeError(tok)
