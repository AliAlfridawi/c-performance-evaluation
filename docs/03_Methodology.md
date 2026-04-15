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
| Uncertainty summaries | Q1/Q3, IQR, min/max, standard deviation, and `95%` bootstrap CI for the median |
| Workload control | Shared inputs plus comparison-count parity across languages |

This contract is enforced rather than merely described. If any expected language-case group is missing or if comparison counts disagree across languages for a published case, the collection and summary pipeline fails instead of silently accepting partial data.

## B. Shared Inputs and Workload Control

Inputs are generated once and stored on disk in `data/benchmark_inputs/`. Each file contains whitespace-separated integers, and `manifest.csv` records the `input_id`, distribution, `N`, and relative path.

The datasets use unique integers:

- `ascending`: `0..N-1`
- `descending`: `N-1..0`
- `random`: a deterministic shuffle of `0..N-1`

Using shared files removes language-specific PRNG differences from the published runs and keeps search cases unambiguous. The benchmark also records `comparisons`, the number of scalar comparisons performed inside each algorithm implementation. That metric is the workload-control variable for this experiment: if comparison counts match across languages for a given case, the harness has strong evidence that it timed equivalent algorithmic work.

Comparison parity does not imply total runtime equivalence. It does not normalize memory layout, interpreter dispatch, JIT compilation, allocation behavior, or cache effects. The method therefore supports narrow in-process claims rather than a claim of complete execution fairness.

## C. Workloads

- Quicksort is evaluated on `random`, `ascending`, and `descending` inputs.
- Linear search is evaluated on `ascending` inputs with `first_hit`, `middle_hit`, `last_hit`, and `miss`.
- Binary search is evaluated on sorted inputs with the same four search cases.

For binary search, sorting is treated as input preparation and is excluded from the timed region. That is a deliberate construct choice: the benchmark measures search over a prepared sorted array, not the cost of turning arbitrary data into searchable data.

## D. Metrics and Timing Boundary

- `comparisons`: hardware-independent work performed by the algorithm
- `elapsed_ns`: in-process execution time measured immediately around the algorithm call

Timing excludes process startup, argument parsing, input loading, and binary-search presorting. Python uses `time.perf_counter_ns()` [6], Java uses `System.nanoTime()` [7], and the C implementation uses `QueryPerformanceCounter` on Windows [8].

Very small workloads are batched until at least `50 ms` of total timed work has been accumulated. The total elapsed time is then normalized back to seconds per algorithm run. This reduces distortion from timer granularity and fixed per-call overhead on extremely small operations [1][2][9].

The timer boundary is intentionally narrow. That improves construct clarity for algorithm-section cost, but it also means the results are not user-visible wall-clock latencies. Public benchmark suites often separate in-process timing from end-to-end timing for exactly this reason [10].

## E. Trial Policy and Summary Statistics

- `5` warm-up trials per configuration
- `20` measured trials per configuration
- Published figures use the median of measured trials
- The summary CSV also records Q1, Q3, IQR, min/max, standard deviation, and a `95%` bootstrap confidence interval for the median
- Raw trial rows remain available in `results/data/benchmark_runs.csv`

The median remains the primary statistic because it is robust to transient scheduler noise and background interruptions [2]. Quartiles and IQR provide a robust spread summary that is less sensitive to isolated extremes than raw min/max. The bootstrap interval adds a descriptive uncertainty band around the median estimate for each benchmark configuration. It does not replace inferential cross-language statistics or justify broad claims beyond this harness.

The warm-up policy is a pragmatic compromise rather than a convergence proof. It reduces the likelihood that a first invocation dominates the published result, but it does not establish that the JVM reached a stable steady state [2][3].

## F. Methodological Positioning

The present methodology is strongest on internal workload alignment and artifact traceability:

- deterministic shared datasets
- explicit benchmark matrices and search scenarios
- comparison-count parity checks across languages
- preserved warm-up rows and measured-trial rows
- strict collector and summary validation
- published summary and metadata artifacts that can be traced back to the raw CSV

It remains weaker than dedicated benchmark frameworks on environment control and formal inference:

- no CPU affinity or core isolation
- no per-sample process isolation
- no GC or JIT telemetry
- no adaptive steady-state detection
- no formal cross-language hypothesis tests

The appropriate reading is therefore: strong exploratory methodology for a transparent repository benchmark, but not a publication-grade runtime study.
