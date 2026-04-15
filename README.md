# Cross-Language Algorithm Benchmarking: C vs. Java vs. Python

This repository benchmarks three small algorithm kernels across C, Java, and Python:

- quicksort
- linear search
- binary search

The final review of the harness found that the methodology is defensible for a narrow question: how do these implementations behave when the timed region is limited to the in-process algorithm section and the same algorithmic work is enforced through shared datasets and comparison-count parity?

It is not an end-to-end application benchmark, a universal language ranking, or a proof of steady-state JVM performance.

## What This Repository Can Claim

- All published benchmark cases use the same deterministic on-disk inputs across languages.
- Comparison counts match across C, Java, and Python for every published configuration, which is strong evidence that the algorithmic workload is aligned.
- Warm-up rows, repeated measured trials, and raw trial capture make the results materially more defensible than ad hoc single-run benchmarks.
- Very small workloads are batched until at least `50 ms` of total timed work is collected, which reduces timer-noise distortion on micro-scale measurements.

## What It Does Not Claim

- It does not measure process startup, file I/O, argument parsing, or binary-search presorting.
- It does not control CPU affinity, core isolation, background load, or power-management state beyond documenting the host used.
- It does not establish steady-state JVM behavior or perform inferential statistics such as confidence intervals.
- It does not generalize beyond this Windows 11 machine, toolchain set, and workload family.

## Methodology Contract

| Dimension | Current contract |
| --- | --- |
| Workload control | Shared datasets in `data/benchmark_inputs/` plus cross-language comparison-count parity |
| Quicksort inputs | `random`, `ascending`, `descending` |
| Search inputs | `ascending` only |
| Search cases | `first_hit`, `middle_hit`, `last_hit`, `miss` |
| Timed region | In-process algorithm body only |
| Excluded costs | Process startup, input loading, argument parsing, binary-search presorting |
| Trial policy | `5` warm-up trials, `20` measured trials |
| Small-workload policy | Batch repeated executions until at least `50 ms` total timed work |
| Primary statistic | Median seconds per run |
| Published artifacts | Raw CSV, summary CSV, and report-ready graphs |

Comparison counts are the control variable for equal algorithmic work. They do not erase differences in runtime services such as JIT compilation, memory management, interpreter dispatch, cache behavior, or standard-library setup.

## Methodology Review Verdict

The harness is well structured for an exploratory benchmark. Its strongest features are deterministic shared inputs, strict collector validation, explicit search scenarios, preserved raw trials, and scope-limited claims.

The main caveat is not correctness but scope. Stronger benchmarking systems such as `pyperf`, JMH, or the infrastructure behind public cross-language suites typically add process isolation, richer warm-up strategies, deeper environment control, and more formal statistical analysis. This repository should therefore be presented as a transparent, reproducible benchmark harness with narrow claims, not as a definitive statement about language performance in general.

## Key Findings

- Comparison counts align across all three languages for every published configuration.
- At `N=5000` on random quicksort input, median in-process times are about `0.000098 s` in C, `0.000152 s` in Java, and `0.012475 s` in Python.
- Those medians correspond to about `1.55x` for Java vs. C and `126.9x` for Python vs. C in this setup.
- Linear search behaves exactly as the search case predicts: `first_hit` stays near one comparison, while `last_hit` and `miss` both reach `5000` comparisons at `N=5000`.
- Binary search remains logarithmic in comparison count: at `N=5000`, published cases range from `23` to `26` comparisons.

## Reproduce

This repository is validated through the documented local workflow below. It intentionally does not depend on GitHub Actions or another CI pipeline.

1. Build the C target:
   - `cd src/c`
   - `mingw32-make all`
2. Return to the repository root and compile Java:
   - `cd ../..`
   - `mvn -q -DskipTests compile`
3. Run correctness and pipeline tests:
   - `cd src/c`
   - `mingw32-make test`
   - `cd ../..`
   - `mvn test`
   - `python -m unittest src/python/test_algorithms.py`
   - `python -m unittest test_benchmark_pipeline.py`
4. Regenerate shared inputs:
   - `python data/DataSetGenerator.py`
5. Collect raw trials:
   - `python scripts/collect_benchmarks.py`
   - The collector fails by default if any language or scenario is missing or inconsistent.
6. Generate summary CSVs and figures:
   - `python scripts/plot_benchmarks.py`

## Results

![Quicksort timing](results/graphs/quicksort_median_time.png)

![Linear search timing](results/graphs/linear_search_median_time.png)

![Binary search timing](results/graphs/binary_search_median_time.png)

Additional report-style summary views are generated in `results/graphs/`:

- `comparison_counts.png`
- `timing_overview.png`
- `timing_speedup_vs_c.png`

## Documentation

The supporting report lives in [docs/index.md](docs/index.md). The discussion section now includes a direct comparison to established benchmarking guidance and public evaluations so the methodology can be read in context rather than in isolation.
