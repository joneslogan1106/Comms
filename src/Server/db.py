id = 1
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
    global id
    f.write(f"\n{id+1};{time};{user};{message}") # Modes start at 0 with ID
    f.close()
    id += 1
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
def validate_message(i: str):
    mode = 0
    type_checks = [int, float, str, str]
    for v in i.split(";"):
        try:
            type_checks[mode](v)
        except ValueError:
            return False
        mode += 1
    return True
if __name__ == "__main__":
    print(validate_message("1;1234567890.123;user.name;Hello, world!"))
    print(validate_message("ef;123456hi7890.12a;21;no"))