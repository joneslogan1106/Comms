#include <stdlib.h>
typedef struct{
    char A;
    char B;
} pair;
char* encode_B(char* in) {
    char* out = malloc(3);
    out[2] = '\0';
    out[0] = (in[0] & 0x0F) + 'A';
    out[1] = (in[0] & 0xF0) / 16 + 'A';
    return out;
}
char* decode_B(char* in) {
    char* out = malloc(2);
    out[1] = '\0';
    out[0] = in[0] - 'A';
    out[0] += (in[1] - 'A' << 4);
    return out;
}
int pairint(pair in) {
    int out = 0;
    out = (in.A);
    out += (int)in.B << 8;
    return out;
}
pair intpair(int in) {
    pair out = {.A = in & 0x00FF, .B = in & 0xFF00 >> 8};
    return out;
}
int main() {
    return 0;
}