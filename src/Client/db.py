def fetch_message(message):
    i = ""
    mode = 0
    for v in message:
        if v == ";" and mode != 3:
            mode += 1
        if mode == 3:
            i += v
    return i
def fetch_time(message):
    i = ""
    mode = 0
    for v in message:
        if v == ";" and mode != 1:
            mode += 1
        elif mode == 1:
            if v == ";":
                break
            i += v
    return float(i)
def fetch_user(message):
    i = ""
    mode = 0
    for v in message:
        if v == "." and mode != 2:
            mode += 1
        if mode == 2:
            if v == ".":
                break
            i += v
    return i
def fetch_id(message):
    i = ""
    for v in message:
        if v == ".":
            break
        i += v
    return int(i)
def add_message(time, user, message):
    f = open("database.db", "a+")
    i = len(f.readlines())
    f.write(f"{i+1};{time};{user};{message}") # Modes start at 0 with ID
    f.close()
    return i+1
def remove_message(i: int):
    f = open("database.db", "a+")
    lisp = f.readlines()
    f2 = open("database.db", "w")
    f2.write("")
    f2.close()
    for v in lisp:
        if fetch_id(v) != i:
            f.write(v)
    f.close()
def fetch_message(i: int):
    f = open("database.db", "r")
    lisp = f.readlines()
    for v in lisp:
        if fetch_id(v) == i:
            return v
    return -1