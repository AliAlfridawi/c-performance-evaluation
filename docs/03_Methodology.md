# III. Methodology

## A. Algorithms

- `quicksort`
- `linear_search`
- `binary_search`

All three languages implement the same algorithm logic and the same comparison-count contract.

## B. Shared Inputs

Inputs are generated once and stored on disk in `data/benchmark_inputs/`. Each file contains whitespace-separated integers, and `manifest.csv` records the `input_id`, distribution, `N`, and relative path.

The datasets use unique integers:

- `ascending`: `0..N-1`
- `descending`: `N-1..0`
- `random`: a deterministic shuffle of `0..N-1`

Using shared files removes the earlier PRNG mismatch between languages and makes search hit cases unambiguous.

## C. Workloads

- Quick sort is evaluated on `random`, `ascending`, and `descending` inputs.
- Linear search is evaluated on `ascending` inputs with `first_hit`, `middle_hit`, `last_hit`, and `miss`.
- Binary search is evaluated on sorted inputs with the same four search cases.

For binary search, sorting is treated as input preparation and is not included in the timed search step.

## D. Metrics

- `comparisons`: hardware-independent work performed by the algorithm
- `elapsed_ns`: in-process execution time measured immediately around the algorithm call

Timing excludes process startup, argument parsing, input loading, and binary-search presorting. Very small workloads are batched until at least `0.5 ms` of total work has been measured. Reported timing is then normalized back to seconds per run.

## E. Trial Policy

- `5` warm-up trials per configuration
- `20` measured trials per configuration
- Published summaries use the median of measured trials
- Min/max bands are preserved to show spread
- The warm-up policy provides a practical JVM baseline, but it is not intended to establish steady-state Java performance
