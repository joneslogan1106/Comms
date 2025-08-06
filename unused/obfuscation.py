import random
def cipher(inp: str, cipher: list):
    index = 0
    out = list(inp)
    for i in inp:
        out[index] = chr(cipher.index(ord(i)))
        index += 1
    return ''.join(out)
def uncipher(inp: str, cipher:list):
    index = 0
    out = list(inp)
    for i in inp:
        out[index] = chr(cipher[ord(i)])
        index += 1
    return ''.join(out)
def Gcipher(key: int):
    cipher = []
    for i in range(255):
        cipher.append(i + 1)
    for s in range(25):
        index = 0
        for i in cipher:
            index2 = abs(((index^2) % 256) - s)
            index1 = abs(((index * key) - s) % 256)
            item1 = cipher.pop(index1)
            cipher.insert(index2, item1)
            item2 = cipher.pop(index2 - 1)
            cipher.insert(index1, item2)
            index += 1
    return cipher
ciphed = Gcipher(70)
#ciphed.sort()
f = open("out.dll", "wb")
lines = []
length = 2048
jarmble = b""
for i in range(length):
    jarmble += cipher(i, ciphed)