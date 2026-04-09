# Algorithmic Benchmarking Suite: C vs. Python vs. Java

![Status: In Development](https://img.shields.io/badge/Status-In%20Development-yellow)
![Course: CSE 1320](https://img.shields.io/badge/Course-CSE%201320%20Honors-blue)
![Institution: UTA](https://img.shields.io/badge/Institution-University%20of%20Texas%20at%20Arlington-orange)

## Project Overview
This repository contains the source code, datasets, and empirical analysis for a comparative study on algorithmic efficiency across different programming language architectures. The primary objective is to benchmark the performance of a compiled language (C), a bytecode/JIT-compiled language (Java), and an interpreted language (Python) when executing fundamental computer science algorithms.

This research was conducted as an Honors Project for CSE 1320 at the University of Texas at Arlington.

## Algorithms Analyzed
The performance of each language is evaluated across both sorting and searching paradigms:
* **Sorting:** Quick Sort
* **Searching:** Linear Search, Binary Search

## Methodology
To ensure a rigorous and objective comparison, the benchmarking methodology relies on two distinct metrics across dynamically scaled datasets:

1. **Hardware-Dependent Metric (Execution Time):** Measuring CPU execution time to isolate the raw computational speed and language overhead.
2. **Hardware-Independent Metric (Iteration Count):** Tracking the absolute number of fundamental operations to ensure theoretical algorithmic complexity remains constant across all implementations.

Tests will be executed across varying input sizes (N) and data distributions (e.g., randomized, pre-sorted, and reverse-sorted arrays) to evaluate Best Case, Worst Case, and Average Case scenarios.

## Planned Repository Structure
\`\`\`text
├── /src
│   ├── /c          # C source files and executables
│   ├── /java       # Java source files and classes
│   └── /python     # Python scripts
├── /data           # Generated datasets (varying N sizes)
├── /results        # Output CSVs, benchmark logs, and plotted graphs
├── /docs           # Research paper drafts and supplementary materials
└── README.md
\`\`\`

## How to Run

### Python ([src/python/](src/python/))

From the repository root (or from `src/python`):

```text
python -m unittest discover -s src/python -v
```

Benchmark (prints one CSV row: `language,algorithm,distribution,N,comparisons,seconds`):

```text
python src/python/benchmark.py quicksort random 1000 --seed 42
```

### C ([src/c/](src/c/))

Requires a C11 compiler (GCC, Clang, or MSVC). On Windows, MinGW-w64 or MSYS2 is typical.

Using `make` (Git Bash, MSYS2, or WSL):

```text
cd src/c
make test
make
./benchmark quicksort random 1000 --seed 42
```

Manual GCC example:

```text
cd src/c
gcc -std=c11 -Wall -Wextra -O2 -o test_algorithms.exe test_algorithms.c algorithms.c
test_algorithms.exe
gcc -std=c11 -Wall -Wextra -O2 -o benchmark.exe benchmark.c algorithms.c
benchmark.exe linear_search ascending 5000
```

Wall-clock time uses `clock()`; comparison counts are returned via `algorithms_get_comparison_count()`.

### Java ([src/java/](src/java/) + [pom.xml](pom.xml))

Requires JDK 17+ and Apache Maven. From the repository root:

```text
mvn test
```

Run the benchmark CLI (classpath built by Maven):

```text
mvn -q exec:java -Dexec.args="quicksort descending 2000"
```

Wall-clock time uses `System.nanoTime()`; comparison counts come from `Algorithms.getComparisonCount()`.

---
*Author: Ali Alfridawi*