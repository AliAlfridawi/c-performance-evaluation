# IV. Experimental Setup

The benchmark was regenerated on a single Windows workstation. The host details that were captured for this review are:

| Component | Value |
| --- | --- |
| CPU | AMD Ryzen 7 8840HS w/ Radeon 780M Graphics |
| Logical processors | `16` |
| Operating system | Windows 11, `amd64` |
| Active power plan | `Balanced` |
| GCC | `15.2.0` |
| Apache Maven | `3.9.14` |
| Java | Eclipse Adoptium OpenJDK `17.0.18` |
| Python | `3.11.9` |

The active power plan and the single-host nature of the run matter. This repository does not pin CPU affinity, isolate cores, disable frequency scaling, or record background-load telemetry. The numbers should therefore be read as measurements from one documented desktop environment rather than as hardware-invariant constants.

## A. Build and Execution Workflow

Repository tooling:

- C sources are built from `src/c/` with `mingw32-make`
- Java sources are compiled from `src/java/` through Maven
- Python benchmarking and plotting scripts run from the repository root

This repository uses a documented local workflow rather than a continuous-integration pipeline. That keeps the benchmark process aligned with the Windows environment used for the published artifact and avoids implying cross-platform automation support that the project does not claim.

Recommended reproduction workflow:

1. `cd src/c`
2. `mingw32-make all`
3. `cd ../..`
4. `mvn -q -DskipTests compile`
5. `python data/DataSetGenerator.py`
6. `python scripts/collect_benchmarks.py`
7. `python scripts/plot_benchmarks.py`

Validation commands used by this repository:

- `cd src/c && mingw32-make test`
- `mvn test`
- `python -m unittest src/python/test_algorithms.py`
- `python -m unittest test_benchmark_pipeline.py`

## B. Output Artifacts

Artifacts produced by the workflow:

| Artifact | Purpose |
| --- | --- |
| `results/data/benchmark_runs.csv` | Raw trial rows including warm-up flags and batch-loop counts |
| `results/data/benchmark_summary.csv` | Median/min/max/std summary per language and benchmark case |
| `results/graphs/quicksort_median_time.png` | Quicksort timing figure |
| `results/graphs/linear_search_median_time.png` | Linear search timing figure |
| `results/graphs/binary_search_median_time.png` | Binary search timing figure |
| `results/graphs/comparison_counts.png` | Workload-consistency figure based on comparison counts |
| `results/graphs/timing_overview.png` | Compact report-style overview of all timing surfaces |
| `results/graphs/timing_speedup_vs_c.png` | Timing normalized against the C baseline |

## C. Reproducibility Notes

The repository is reasonably reproducible for a small research artifact because it preserves datasets, raw measurements, and plotting code together. It is not fully environment-normalized in the way that dedicated benchmarking frameworks or isolated lab machines would be. A future regeneration intended for stronger publication claims should also capture CPU governor behavior, memory capacity, background-load state, and benchmark-command metadata alongside the CSV outputs.
