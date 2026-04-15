# IV. Experimental Setup

The checked-in benchmark snapshot was regenerated on a single Windows workstation. The repository now records the machine and toolchain context in `results/data/benchmark_metadata.json`; the key fields for the current snapshot are summarized below.

| Component | Value |
| --- | --- |
| CPU family | AMD64 Family 25 Model 117 Stepping 2 |
| Logical processors | `16` |
| Operating system | Windows `10.0.26200` on `AMD64` |
| Active power plan | `Balanced` |
| GCC | `15.2.0` |
| Java | OpenJDK `17.0.18` |
| Python | `3.11.9` |

These values matter because the repository is a single-host benchmark artifact. The numbers should be read as measurements from one documented environment rather than as hardware-invariant constants.

## A. Build and Execution Configuration

| Subsystem | Configuration |
| --- | --- |
| C build | `mingw32-make all` from `src/c/` |
| C flags | `-std=c11 -Wall -Wextra -O2` |
| Java build | `mvn -q -DskipTests compile` |
| Java release target | `17` |
| Java runtime flags | none beyond the default launcher |
| Python runtime | CPython `3.11.9` |
| Python runtime flags | none |

Benchmark runner templates recorded in `benchmark_metadata.json`:

- Python: `python src/python/benchmark.py <algorithm> <distribution> <N> --input-file <path> --trials <n> --warmup <n> --search-case <case>`
- C: `src/c/benchmark.exe <algorithm> <distribution> <N> --input-file <path> --trials <n> --warmup <n> --search-case <case>`
- Java: `java -cp target/classes bench.Benchmark <algorithm> <distribution> <N> --input-file <path> --trials <n> --warmup <n> --search-case <case>`

## B. Controlled and Uncontrolled Factors

| Category | Controlled in this repository | Not controlled in this repository |
| --- | --- | --- |
| Workload definition | Shared input files, explicit benchmark matrix, explicit search cases, comparison-count parity | Real-application workload mix |
| Timing scope | Same in-process timing boundary per language | End-to-end wall-clock latency |
| Trial policy | Common warm-up and measured-trial counts, common `50 ms` batching threshold | Adaptive steady-state detection |
| Build configuration | Documented compiler flags and runtime entrypoints | Alternative optimization flags or JVM tuning |
| Host environment | Host, CPU count, power plan, and key tool versions recorded | CPU affinity, core isolation, thermal state, background-load telemetry |

This table is the practical interpretation boundary for the report. The benchmark is controlled enough to support matched-workload algorithm-section claims, but not controlled enough to support hardware-independent or universally generalizable rankings.

## C. Output Artifacts

| Artifact | Purpose |
| --- | --- |
| `results/data/benchmark_runs.csv` | Raw trial rows including warm-up flags and batch-loop counts |
| `results/data/benchmark_summary.csv` | Medians, quartiles, IQR, `95%` bootstrap median CI, min/max, standard deviation, comparisons, and trial counts |
| `results/data/benchmark_metadata.json` | Host, toolchain, build, command, and artifact-hash metadata |
| `results/graphs/quicksort_median_time.png` | Quicksort timing figure with IQR bands |
| `results/graphs/linear_search_median_time.png` | Linear-search timing figure with IQR bands |
| `results/graphs/binary_search_median_time.png` | Binary-search timing figure with IQR bands |
| `results/graphs/comparison_counts.png` | Workload-consistency figure based on comparison counts |
| `results/graphs/timing_overview.png` | Compact multi-panel timing summary |
| `results/graphs/timing_speedup_vs_c.png` | Timing normalized against the C baseline |

The metadata sidecar also records SHA-256 hashes for the raw CSV, summary CSV, and figures so that the checked-in report snapshot can be tied to exact artifact bytes.

## D. Reproduction Workflow

Recommended local workflow:

1. `cd src/c`
2. `mingw32-make all`
3. `cd ../..`
4. `mvn -q -DskipTests compile`
5. `python data/DataSetGenerator.py`
6. `python scripts/collect_benchmarks.py`
7. `python scripts/plot_benchmarks.py`

Validation commands used by the repository:

- `cd src/c && mingw32-make test`
- `mvn test`
- `python -m unittest src/python/test_algorithms.py`
- `python -m unittest test_benchmark_pipeline.py`

The workflow is intentionally local rather than CI-driven. That keeps the published artifacts tied to the documented Windows environment used for measurement and avoids implying cross-platform automation support that the repository does not claim.
