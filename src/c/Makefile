# Windows: use MinGW-w64 or MSYS2: mingw32-make
# MSVC: compile manually (see README)

CC ?= gcc
CFLAGS = -std=c11 -Wall -Wextra -O2

ifeq ($(OS),Windows_NT)
RM_CMD = del /Q /F
else
RM_CMD = rm -f
endif

.PHONY: all clean test bench

all: test_algorithms benchmark

test_algorithms: test_algorithms.o algorithms.o
	$(CC) $(CFLAGS) -o $@ test_algorithms.o algorithms.o

benchmark: benchmark.o algorithms.o
	$(CC) $(CFLAGS) -o $@ benchmark.o algorithms.o

test_algorithms.o: test_algorithms.c algorithms.h
benchmark.o: benchmark.c algorithms.h
algorithms.o: algorithms.c algorithms.h

test: test_algorithms
	./test_algorithms

clean:
	$(RM_CMD) test_algorithms test_algorithms.exe benchmark benchmark.exe *.o
