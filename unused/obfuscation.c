#include <stdio.h>
#include <strings.h>
#include <stdlib.h>
#include <math.h>
int* Gcipher(unsigned long in) {
    int* cipher = (int*)malloc(256 * sizeof(int) + 1);
    cipher[255] = 0;
    for (int i = 0; i < 256; i++) {
        cipher[i] = i - 128;
    }
    for (unsigned char i = 0; i < 25; i++) {
        for (int v = 0; v < 256; v++) {
            int index1 = abs((int)pow(v, 2) % 256 - i);
            int index2 = abs(v * in - i % 256);
            int item1 = cipher[index1];
            int item2 = cipher[index2];
            cipher[index1] = item2;
            cipher[index2] = item1;
        }
    }
    return cipher;
}
int main() {
    int* ciphed = Gcipher(25);
    printf("[");
    for (int i = 0; i < 255; i++) {
        printf("%d, ", ciphed[i]);
    }
    printf("%d]\n", ciphed[25]);
}