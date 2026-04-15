# III. Methodology

## A. Benchmark Contract

| Dimension | Contract |
| --- | --- |
| Algorithms | `quicksort`, `linear_search`, `binary_search` |
| Languages | C, Java, Python |
| Quicksort inputs | `random`, `ascending`, `descending` |
| Search inputs | `ascending` |
| Search cases | `first_hit`, `middle_hit`, `last_hit`, `miss` |
| Timed region | In-process algorithm section only |
| Excluded costs | Process startup, argument parsing, file loading, binary-search presorting |
| Warm-up policy | `5` warm-up trials per configuration |
| Measured trials | `20` measured trials per configuration |
| Micro-scale mitigation | Repeat execution until at least `50 ms` total timed work per trial |
| Primary statistic | Median seconds per run |
| Workload control | Shared inputs plus comparison-count parity across languages |

This contract is strict by design. If any expected language/case group is missing or the comparison counts disagree across languages, the collection pipeline fails instead of silently publishing partial data.

## B. Shared Inputs and Workload Control

Inputs are generated once and stored on disk in `data/benchmark_inputs/`. Each file contains whitespace-separated integers, and `manifest.csv` records the `input_id`, distribution, `N`, and relative path.

The datasets use unique integers:

- `ascending`: `0..N-1`
- `descending`: `N-1..0`
- `random`: a deterministic shuffle of `0..N-1`

Using shared files removes language-specific PRNG differences from the published runs and makes search hit cases unambiguous. The benchmark also records `comparisons`, which count scalar comparisons inside the algorithm implementation. That metric is the workload-control mechanism for this experiment: if comparison counts match across languages for a given case, the harness has strong evidence that it timed equivalent algorithmic work.

Comparison parity is necessary but not sufficient for full runtime comparability. It does not normalize memory layout, interpreter dispatch, JIT compilation, allocation behavior, cache locality, or other runtime services. The method therefore supports narrow in-process claims, not a claim of total runtime fairness.

## C. Workloads

- Quicksort is evaluated on `random`, `ascending`, and `descending` inputs.
- Linear search is evaluated on `ascending` inputs with `first_hit`, `middle_hit`, `last_hit`, and `miss`.
- Binary search is evaluated on sorted inputs with the same four search cases.

For binary search, sorting is treated as input preparation and is excluded from the timed region. That is a deliberate choice: the benchmark is measuring search over a prepared sorted array, not the cost of turning arbitrary data into searchable data.

## D. Metrics and Timing Boundary

- `comparisons`: hardware-independent work performed by the algorithm
- `elapsed_ns`: in-process execution time measured immediately around the algorithm call

Timing excludes process startup, argument parsing, input loading, and binary-search presorting. Python uses `time.perf_counter_ns()` [6], Java uses `System.nanoTime()` [7], and the C implementation uses `QueryPerformanceCounter` on Windows [8].

Very small workloads are batched until at least `50 ms` of total timed work has been collected. The total elapsed time is then normalized back to seconds per algorithm run. This is a practical microbenchmarking safeguard: it reduces the distortion caused by timer granularity and per-call overhead on very short operations [1][2][9].

The timer boundary is intentionally narrow. That makes the metric cleaner for comparing algorithm-section cost, but it also means the results do not represent full user-visible latency. Public benchmarking projects sometimes report both external wall-clock and in-process timing for exactly this reason [10].

## E. Trial Policy and Summary Statistics

- `5` warm-up trials per configuration
- `20` measured trials per configuration
- Published summaries use the median of measured trials
- Min/max bands and per-group standard deviation are preserved for spread
- Raw trial rows remain available in `results/data/benchmark_runs.csv`

The median is used because it is more robust than the mean to transient scheduler noise and background interruptions [2]. The warm-up policy is a pragmatic compromise: it is enough to avoid treating the first invocation as representative, but it is not a proof that the JVM reached a stable steady state [2][3]. This report therefore treats Java measurements as harness-specific observations, not as a formal steady-state characterization.

## F. Methodology Review Verdict

The final review classified the current methodology as follows:

- **Strong as implemented**: deterministic shared datasets, explicit workload matrix, comparison-count parity checks, preserved raw trials, and strict collector validation.
- **Correct but scope-limited**: in-process timing, binary-search presort exclusion, median-first reporting, and modest warm-up within one process per configuration.
- **Weaker than dedicated benchmark harnesses**: no CPU pinning, no process isolation per measured sample, no confidence intervals, no GC/JIT telemetry, and no end-to-end wall-clock metric.

That means the experiment is methodologically sound for exploratory cross-language analysis, provided the documentation keeps the claims narrow and explicit.
