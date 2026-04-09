# Windows: use MinGW-w64 or MSYS2: mingw32-make
# MSVC: compile manually (see README)

CC ?= gcc
CFLAGS = -std=c11 -Wall -Wextra -O2

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
	rm -f test_algorithms benchmark *.o
