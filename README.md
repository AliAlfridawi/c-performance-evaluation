# Cross-Language Algorithm Benchmarking: C vs. Java vs. Python

This repository benchmarks three small algorithm kernels across C, Java, and Python:

- quicksort
- linear search
- binary search

The repository answers a narrow question: when the algorithmic workload is aligned across languages with shared deterministic inputs and comparison-count parity, what in-process timing differences remain on this Windows host?

It is not an end-to-end application benchmark, a universal language ranking, or a steady-state JVM study.

## Research Question

How do C, Java, and Python differ in median in-process execution time for matched algorithmic work when process startup, input loading, argument parsing, and binary-search presorting are excluded from the timed region?

## Main Artifacts

| Artifact | Purpose |
| --- | --- |
| `results/data/benchmark_runs.csv` | Raw warm-up and measured trial rows |
| `results/data/benchmark_summary.csv` | Per-group medians, quartiles, IQR, min/max, standard deviation, and 95% bootstrap median CIs |
| `results/data/benchmark_metadata.json` | Machine-readable host, toolchain, build, command, and artifact metadata |
| `results/graphs/*.png` | Report-ready timing and comparison figures |
| `docs/index.md` | Full supporting report |

## Method Contract

| Dimension | Current contract |
| --- | --- |
| Workloads | `quicksort`, `linear_search`, `binary_search` |
| Languages | C, Java, Python |
| Quicksort inputs | `random`, `ascending`, `descending` |
| Search inputs | `ascending` |
| Search cases | `first_hit`, `middle_hit`, `last_hit`, `miss` |
| Timed region | In-process algorithm section only |
| Excluded costs | Process startup, file loading, argument parsing, binary-search presorting |
| Warm-up policy | `5` warm-up trials per configuration |
| Measured policy | `20` measured trials per configuration |
| Small-workload policy | Batch repeated executions until at least `50 ms` total timed work |
| Primary statistic | Median seconds per run |
| Uncertainty summaries | Q1/Q3, IQR, min/max, standard deviation, and 95% bootstrap CI for the median |
| Workload control | Shared on-disk inputs plus cross-language comparison-count parity |

Comparison parity is the internal workload-control variable. It shows that the algorithmic work is aligned for each published case. It does not equalize memory layout, interpreter dispatch, JIT optimization, cache locality, or other runtime services.

## Representative Results

All values below come from `results/data/benchmark_summary.csv`.

| Case | C median | Java median | Python median | Java / C | Python / C |
| --- | --- | --- | --- | --- | --- |
| Quicksort, `random`, `N=5000` | `0.0000983 s` | `0.0001523 s` | `0.0124753 s` | `1.55x` | `126.9x` |
| Linear search, `miss`, `N=5000` | `0.00000225 s` | `0.00000248 s` | `0.0005631 s` | `1.10x` | `250.5x` |
| Binary search, `miss`, `N=5000` | `0.0000000490 s` | `0.0000000663 s` | `0.00000386 s` | `1.35x` | `78.7x` |

## Interpretation Boundary

- These are measurements from one documented Windows workstation under a balanced power plan.
- The repository reports a narrow algorithm-section metric, not user-visible end-to-end latency.
- The summary CSV now includes uncertainty columns, but the project still does not make formal inferential claims about universal language ordering.

## Reproduce

1. Build the C benchmark:
   `cd src/c`
   `mingw32-make all`
2. Return to the repository root and compile Java:
   `cd ../..`
   `mvn -q -DskipTests compile`
3. Run validation:
   `cd src/c`
   `mingw32-make test`
   `cd ../..`
   `mvn test`
   `python -m unittest src/python/test_algorithms.py`
   `python -m unittest test_benchmark_pipeline.py`
4. Regenerate shared inputs:
   `python data/DataSetGenerator.py`
5. Collect raw trials:
   `python scripts/collect_benchmarks.py`
6. Rebuild summaries, metadata, and figures:
   `python scripts/plot_benchmarks.py`

## Documentation

The full report is in [docs/index.md](docs/index.md). It now includes an explicit research question, a controlled-versus-uncontrolled setup table, a validity-threats table, and direct links between headline claims and repository artifacts.
