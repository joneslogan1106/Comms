import ctypes
c16 = ctypes.CDLL("./16.dll")
# use "from c16.py import ctypes, c16" to import
c16.decode_B.restype = ctypes.c_char_p
c16.encode_B.restype = ctypes.c_char_p
if __name__ == "__main__":
    #print(c16.decode_B(c16.encode_B("L")).decode('utf-8'))
    print(c16.encode_B("A"))