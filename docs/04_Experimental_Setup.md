# IV. Experimental Setup

The benchmark was regenerated on a Windows x86_64 machine with the following local toolchain:

- GCC `15.2.0`
- Apache Maven `3.9.14`
- Eclipse Adoptium Java `17.0.18`
- Python `3.11.9`
- OS: Windows 11 (`amd64`)

Repository tooling:

- C sources are built from `src/c/` with `mingw32-make`
- Java sources are compiled from `src/java/` through Maven
- Python benchmarking and plotting scripts run from the repository root

Artifacts produced by the workflow:

- Raw trials: `results/data/benchmark_runs.csv`
- Median summary: `results/data/benchmark_summary.csv`
- Plots: `results/graphs/quicksort_median_time.png`, `linear_search_median_time.png`, `binary_search_median_time.png`, and `comparison_counts.png`
