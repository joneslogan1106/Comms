#!/bin/bash
# Compile C code as shared library for Linux
cd Server
gcc -c 16.c -o 16.o -fPIC
gcc -shared 16.o -o lib16.so
rm 16.o
echo "Compiled lib16.so successfully for Linux"