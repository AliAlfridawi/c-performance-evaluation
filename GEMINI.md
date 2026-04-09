# GEMINI.md - Algorithmic Benchmarking Suite

This project is a comparative performance study of algorithms (Quick Sort, Linear Search, Binary Search) implemented in C, Java, and Python. It evaluates both raw execution time and hardware-independent metrics like comparison counts.

## Project Overview

- **Objective:** Benchmark algorithmic efficiency across different language architectures (Compiled vs. JIT/Bytecode vs. Interpreted).
- **Algorithms:** Quick Sort, Linear Search, Binary Search.
- **Metrics:** Execution time (CPU clock/nanoseconds) and Iteration/Comparison counts.
- **Technologies:**
    - **C:** C11, GCC/Clang, Makefile.
    - **Java:** JDK 17+, Apache Maven.
    - **Python:** Python 3.10+, `pandas`, `matplotlib`.

## Project Structure

- `src/c/`: C implementation, header files, and `Makefile`.
- `src/java/`: Java implementation (package `bench`) and `pom.xml` in root.
- `src/python/`: Python implementation and unit tests.
- `scripts/`: Python automation for benchmark collection and visualization.
- `data/`: Dataset generation scripts and documentation.
- `results/`: CSV data and generated performance graphs.
- `docs/`: Research documentation and papers.

## Building and Running

### Prerequisites
- C11 compatible compiler (GCC, Clang, or MSVC).
- JDK 17 or higher.
- Apache Maven.
- Python 3.10+ with `pip`.

### Setup
Install Python dependencies for plotting:
```powershell
pip install -r requirements.txt
```

### C (src/c)
Build the benchmark and test executables:
```powershell
cd src/c
make
```
Run a manual benchmark:
```powershell
./benchmark quicksort random 1000 --seed 42
```

### Java
Compile and package:
```powershell
mvn compile
```
Run the benchmark CLI:
```powershell
mvn -q exec:java -Dexec.args="quicksort random 1000 --seed 42"
```

### Python (src/python)
Run the benchmark script:
```powershell
python src/python/benchmark.py quicksort random 1000 --seed 42
```

### Automation Scripts
Collect data from all languages into `results/data/benchmark_runs.csv`:
```powershell
python scripts/collect_benchmarks.py
```
Generate performance graphs in `results/graphs/`:
```powershell
python scripts/plot_benchmarks.py
```

## Testing

- **C:** `cd src/c && make test` (Runs `test_algorithms.c`)
- **Java:** `mvn test` (Runs JUnit 5 tests in `src/test/java`)
- **Python:** `python -m unittest discover -s src/python -v`

## Development Conventions

- **Consistency:** Each language implementation must return both execution time and comparison counts in a consistent CSV-style output: `language,algorithm,distribution,N,comparisons,seconds`.
- **Reproducibility:** Use the `--seed` flag to ensure (as much as possible per language PRNG) reproducible random distributions.
- **Accuracy:** Iteration counts must be hardware-independent and theoretically consistent across implementations for deterministic inputs (ascending/descending).
