# V. Results and Analysis

The results below are medians over the `20` measured trials for each benchmark configuration. They are summaries of the current harness, not confidence intervals for a universal language ordering.

## A. Quicksort

![Quicksort timing](../results/graphs/quicksort_median_time.png)

Comparison counts match across languages for every quicksort configuration, so the published timing gaps reflect observed in-process execution cost under a matched workload. At `N=5000` on random input:

- C median: `0.000098 s`
- Java median: `0.000152 s`
- Python median: `0.012475 s`

Those medians correspond to about `1.55x` for Java vs. C and `126.9x` for Python vs. C on this host. Because startup and input loading are excluded, these values should be interpreted as algorithm-section timings under the harness rather than as full-program latency.

The current quicksort implementation uses a median-of-three pivot strategy before the Lomuto partition step. That materially improves behavior on already ordered inputs compared with the older result artifacts that were previously checked into the repository, which is why regenerated data rather than stale CSVs must drive the report.

## B. Linear Search

![Linear search timing](../results/graphs/linear_search_median_time.png)

The linear-search benchmark reports explicit search cases instead of a single favorable hit case. The measured comparison counts behave exactly as expected:

- `first_hit` stays at `1` comparison
- `middle_hit` grows to `2501` comparisons at `N=5000`
- `last_hit` and `miss` both reach `5000` comparisons at `N=5000`

That case split is methodologically important because it prevents the report from presenting best-case search timing as representative behavior.

## C. Binary Search

![Binary search timing](../results/graphs/binary_search_median_time.png)

Binary search remains logarithmic in comparison count. At `N=5000`, the published cases range from `23` to `26` comparisons depending on whether the lookup hits early, hits late, or misses.

The interpretation boundary is especially important here: the timed region covers search over a prepared sorted array. It does not include the cost of sorting unsorted data into that form.

## D. Workload Consistency Check

![Comparison counts](../results/graphs/comparison_counts.png)

The summary CSV shows no comparison-count mismatches across languages for any published configuration. That is the strongest internal validity signal in the repository because the collection and plotting pipeline both fail rather than silently accept incomplete or inconsistent groups.

This does not prove perfect runtime comparability, but it does show that the experiment held the algorithmic work itself constant for the benchmark cases that were published.

## E. Summary Figures

![Timing overview](../results/graphs/timing_overview.png)

![Relative timing vs C](../results/graphs/timing_speedup_vs_c.png)

The overview figure condenses the timing surface into one report-friendly panel. The relative-timing figure shows how Java and Python move against the C baseline across identical workloads. In that normalized view, `1.0x` indicates parity with C and values above `1.0x` indicate slower median in-process timing than C for the same benchmark case.

These figures are intended as interpretation aids, not as substitutes for the raw rows. Any claim in the report should be traceable back to `benchmark_runs.csv` and `benchmark_summary.csv`.
