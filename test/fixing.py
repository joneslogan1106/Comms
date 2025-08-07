def unfix_message(i: str):
    o = ""
    b = False
    replace_list = {
        "n":"\n",
        "\\": "\\"
    }
    for v in i:
        if b:
            try:
                o += replace_list[v]
            except KeyError:
                o += v
            b = False
        elif v == "\\":
            b = True
        else:
            o += v
    return o
def fix_string(i: str):
    o = ""
    replace_string_list = {
        "\n": "\\n",
        "\\": "\\\\"
    }
    for v in i:
        try:
            o += replace_string_list[v]
        except KeyError:
            o += v
    return o
print(unfix_message(fix_string("Hello!\nToday we will be using some backslashes aka \\")))
print(fix_string("""Hello!
Today we will be using some backslashes aka \\"""))