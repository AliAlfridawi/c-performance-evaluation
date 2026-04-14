# Cross-Language Algorithm Benchmarking: C vs. Java vs. Python

This repository is a reproducible benchmarking project for three baseline algorithms implemented in C, Java, and Python:

- Quick sort
- Linear search
- Binary search

The focus is not just "which language is fastest," but whether the benchmark protocol is defensible. The current version fixes the earlier methodological gaps by using shared on-disk datasets, explicit search cases, warm-up trials, repeated measurements, and raw trial data.

## What This Project Demonstrates

- Cross-language algorithm implementations with matching comparison-count semantics
- A benchmark harness that separates raw trial capture from summary plotting
- Shared deterministic inputs consumed by all three language runners
- A small research-style workflow: collect data, summarize medians, document limitations

## Benchmark Design

- Shared inputs live in `data/benchmark_inputs/` and are listed in `data/benchmark_inputs/manifest.csv`.
- Inputs use unique integers so search hit cases are unambiguous across languages.
- Quick sort is tested on `random`, `ascending`, and `descending` inputs.
- Linear search and binary search are tested on `ascending` inputs with `first_hit`, `middle_hit`, `last_hit`, and `miss` cases.
- Each configuration runs `5` warm-up trials and `20` measured trials.
- Very small workloads are batched until at least `50 ms` of total timed work is collected, then normalized back to per-run timing.
- `elapsed_ns` measures only the in-process algorithm section; process startup, input loading, and binary-search presorting are excluded.
- Raw rows are written to `results/data/benchmark_runs.csv`; summary statistics including median, min/max, and standard deviation are written to `results/data/benchmark_summary.csv`.

## Key Findings

- Comparison counts align across all three languages for every published configuration, which confirms the shared-input protocol is working as intended.
- Under this harness on one Windows 11 machine, quick sort at `N=5000` on random input has median in-process times of about `0.000098 s` in C, `0.000152 s` in Java, and `0.012475 s` in Python.
- Those medians correspond to observed ratios of about `1.55x` for Java vs. C and `126.9x` for Python vs. C in this setup; they should not be read as steady-state language rankings.
- Linear search behaves exactly as the search case predicts: `first_hit` stays near one comparison, while `last_hit` and `miss` reach `5000` comparisons at `N=5000`.
- Binary search stays near logarithmic behavior: at `N=5000`, the comparison count ranges from `23` to `26` depending on the search case.

## Reproduce

1. Build the native and JVM targets:
   - `cd src/c && mingw32-make all`
   - `mvn -q -DskipTests compile`
2. Run correctness tests:
   - `cd src/c && mingw32-make test`
   - `mvn test`
   - `cd src/python && python -m unittest test_algorithms.py`
   - `python -m unittest test_benchmark_pipeline.py`
3. Regenerate shared inputs:
   - `python data/DataSetGenerator.py`
4. Collect raw trials:
   - `python scripts/collect_benchmarks.py`
   - The collector now fails by default if any language/case is missing or inconsistent. Use `--allow-partial` only for local debugging.
5. Generate summary CSVs and plots:
   - `python scripts/plot_benchmarks.py`
   - This writes the original benchmark figures plus the publication-style summary views `timing_overview.png` and `timing_speedup_vs_c.png`.

## Results

![Quick sort timing](results/graphs/quicksort_median_time.png)

![Linear search timing](results/graphs/linear_search_median_time.png)

![Binary search timing](results/graphs/binary_search_median_time.png)

Additional report-ready summary views are also generated in `results/graphs/`:

- `timing_overview.png` for a compact multi-panel timing atlas
- `timing_speedup_vs_c.png` for normalized timing relative to the C baseline

## Limitations

- Results come from one Windows 11 machine and should not be treated as a universal language ranking.
- Each benchmark configuration is launched as a separate process, but `elapsed_ns` measures only the in-process algorithm section after setup. Startup, input loading, and binary-search presorting are excluded.
- Java still shows visible run-to-run spread in several configurations, so the reported medians are practical observations under this harness rather than steady-state JVM claims.
- The project tracks execution time and comparison counts, not memory usage, cache effects, or CPU affinity controls.

The supporting report lives in [docs/index.md](docs/index.md).
