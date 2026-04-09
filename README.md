# Algorithmic Benchmarking Suite: C vs. Java vs. Python

![Status: Completed](https://img.shields.io/badge/Status-Completed-success)
![Course: CSE 1320](https://img.shields.io/badge/Course-CSE%201320%20Honors-blue)
![Institution: UTA](https://img.shields.io/badge/Institution-University%20of%20Texas%20at%20Arlington-orange)

## Abstract
This study presents a comprehensive benchmarking of three fundamental computer science algorithms—**Quick Sort**, **Linear Search**, and **Binary Search**—across three distinct programming language architectures: **C** (compiled), **Java** (JIT-compiled), and **Python** (interpreted). By utilizing both hardware-dependent metrics (execution time) and hardware-independent metrics (comparison counts) across datasets ranging from $N=10$ to $N=5000$, we quantify the performance disparities inherent in each language's execution model. Our findings indicate that while hardware-independent metrics remain theoretically consistent for deterministic inputs, raw execution time varies by orders of magnitude. C exhibits the highest efficiency, while Python demonstrates significant overhead, particularly in large-scale sorting tasks. Java bridges the gap, showing high throughput after initial JVM warm-up.

## I. Methodology & Experimental Setup

### A. Performance Metrics
To ensure a rigorous and objective comparison, the benchmarking methodology relies on two distinct metrics:
1.  **Hardware-Dependent Metric (Execution Time):** Measured in wall-clock time using high-resolution timers (`clock()` in C, `System.nanoTime()` in Java, and `time.perf_counter()` in Python) to isolate the raw computational speed and language overhead.
2.  **Hardware-Independent Metric (Comparison Count):** A metric that tracks the absolute number of fundamental operations performed, ensuring theoretical algorithmic complexity remains constant across all implementations for deterministic inputs.

### B. Algorithms & Data Distributions
The performance of each language is evaluated across both sorting and searching paradigms:
*   **Quick Sort:** Evaluated across random, ascending, and descending distributions to capture Average, Best, and Worst Case scenarios.
*   **Linear Search:** A sequential search algorithm representing $O(N)$ complexity.
*   **Binary Search:** A logarithmic search algorithm representing $O(\log N)$ complexity on sorted data.

Tests were executed across varying input sizes ($N=10$ to $N=5000$) to evaluate performance scaling.

## II. Empirical Results & Analysis

### A. Execution Time Trends
The disparity in execution time is most evident in the Quick Sort algorithm as $N$ increases. As seen in Fig 1, the compiled nature of C provides a massive advantage, while Python's interpreted overhead leads to significantly higher execution times, especially at scale.

![Cross Language Time](results/graphs/cross_time_vs_n_faceted.png)
*Fig 1. Execution time across languages for varied distributions.*

### B. Speedup relative to C
Using C as the baseline for maximum efficiency, Fig 2 highlights how Java's performance approaches C as the dataset size increases, likely due to JIT optimizations and high throughput. Python, conversely, remains consistently several orders of magnitude slower.

![Speedup vs C](results/graphs/cross_speedup_vs_c.png)
*Fig 2. Speedup of Java and Python relative to C.*

### C. Sorting Distribution Effects
Python shows extreme sensitivity to pre-sorted data when using a standard Quick Sort implementation. Fig 3 illustrates the significant performance penalty Python incurs in worst-case scenarios (e.g., ascending/descending data), where execution time scales poorly compared to the more optimized C and Java implementations.

![Distribution Effect Quicksort Python](results/graphs/dist_effect_quicksort_python.png)
*Fig 3. Sensitivity of Python Quick Sort to input distribution.*

> [!TIP]
> **Full Research Report:** For a detailed deep dive into the methodology, experimental setup, and granular data analysis, please see our modular [IEEE Research Paper Index](docs/index.md).

---

## III. Repository Structure & Reproduction

### A. Directory Structure
```text
├── /src
│   ├── /c          # C source files (C11, Makefile)
│   ├── /java       # Java source files (JDK 17+, Maven)
│   └── /python     # Python scripts (3.10+)
├── /data           # Dataset generation scripts
├── /results        # Output CSVs and generated performance graphs
├── /docs           # Formal IEEE research paper drafts
└── README.md
```

### B. Compiling & Running Benchmarks

#### C Implementation
Requires a C11 compiler (GCC, Clang, or MSVC) and `make`.
```bash
cd src/c
make
./benchmark quicksort random 1000 --seed 42
```

#### Java Implementation
Requires JDK 17+ and Apache Maven.
```bash
mvn compile
mvn -q exec:java -Dexec.args="quicksort random 1000 --seed 42"
```

#### Python Implementation
Requires Python 3.10+.
```bash
python src/python/benchmark.py quicksort random 1000 --seed 42
```

### C. Data Collection & Visualization
1. Install plotting dependencies: `pip install -r requirements.txt`
2. Collect timings from all languages:
   ```bash
   python scripts/collect_benchmarks.py
   ```
3. Generate performance graphs:
   ```bash
   python scripts/plot_benchmarks.py
   ```

---
*Author: Ali Alfridawi*
*Research Conducted for CSE 1320 Honors Project, University of Texas at Arlington.*