import threading, random, time
found = False
prime = 0
def random_prime():
    rand = random.getrandbits(2047)
    rand = (rand << 1) | 1
    return rand
def miller_rabin_hell(n: int, k:int = 80):
    """
    Miller rabin but it takes so long by default
    """
    global found
    if n < 2 or n % 2 == 0:
        return False
    if n in (2, 3):
        return True

    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        if found:
            return False
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def miller_rabin_hell_helper():
    while True:
        pprime = random_prime()
        is_prime = miller_rabin_hell(pprime)
        global found
        if is_prime:
            found = True
            global prime
            prime = pprime
            return prime
        elif found:
            return False
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def modinv(a, m):
    """Modular inverse using Extended Euclidean Algorithm"""
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 % m0

def generate_rsa_keys(p: int, q: int):
    if p == q:
        raise ValueError("p and q must be distinct primes")
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    while gcd(e, phi) != 1:
        e += 2
    d = modinv(e, phi)

    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key
def encrypt(message, public_key) -> int:
    e, n = public_key
    m_int = int.from_bytes(message.encode(), byteorder='big')
    c = pow(m_int, e, n)
    return c

def decrypt(ciphertext, private_key) -> str:
    d, n = private_key
    m_int = pow(ciphertext, d, n)
    message = m_int.to_bytes((m_int.bit_length() + 7) // 8, byteorder='big').decode()
    return message
def gen_hash(i: bytes|str, s: int) -> bytes:
    inp = b""
    if type(i) == str:
        inp = i.encode("ascii")
    elif type(i) == bytes:
        try:
            i.decode("ascii")
        except UnicodeDecodeError:
            return -2
        inp = i
    else:
        return -1
    c = 0
    inp = bytearray(inp)
    if len(inp) < 3:
        for _ in range(3 - len(inp)):
            inp.append(45)
    output = bytearray((((inp[0] * inp[1] + inp[2]) // 3) % 95 + 32).to_bytes() * s)
    for k in range(5):
        for byte in inp:
            output[c] = (output[c] + byte) % 127
            output[c] = (output[c] * byte * k) % 127
            output[c] %= 95
            output[c] += 32
            c += 1
            if c == len(output):
                c = 0
    # output.append(((inp[0] * inp[1] + inp[2]) // 3) % 95 + 32)
    return bytes(output)
