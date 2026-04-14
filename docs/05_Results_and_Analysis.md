# V. Results and Analysis

## A. Quick Sort

![Quick sort timing](../results/graphs/quicksort_median_time.png)

Comparison counts match across languages for every quick sort configuration, so the timing gaps reflect observed in-process execution cost under this harness rather than mismatched work. At `N=5000` on random input:

- C median: `0.000098 s`
- Java median: `0.000152 s`
- Python median: `0.012475 s`

The current median-of-three partition logic also changes the sorted-input behavior relative to the older CSVs that were still checked into the repository. Java also shows visibly wider min-max bands than C for several configurations, so the Java medians should be interpreted as harness-specific observations rather than steady-state JVM claims.

## B. Linear Search

![Linear search timing](../results/graphs/linear_search_median_time.png)

The linear-search benchmark now reports explicit search cases instead of one favorable hit case. The measured comparison counts behave exactly as expected:

- `first_hit` stays at `1` comparison
- `middle_hit` grows to `2501` comparisons at `N=5000`
- `last_hit` and `miss` both reach `5000` comparisons at `N=5000`

That makes the search benchmark more useful than the earlier version, which only timed a best-case lookup.

## C. Binary Search

![Binary search timing](../results/graphs/binary_search_median_time.png)

Binary search remains logarithmic in comparison count. At `N=5000`, the search cases range from `23` to `26` comparisons depending on whether the lookup hits early, hits late, or misses.

## D. Comparison Count Consistency

![Comparison counts](../results/graphs/comparison_counts.png)

The summary CSV shows no comparison-count mismatches across languages for any published configuration. That is the strongest evidence that the shared-input protocol is working, because the collection pipeline now fails instead of silently publishing incomplete or inconsistent groups.

## E. Publication Summary Views

![Timing overview](../results/graphs/timing_overview.png)

![Relative timing vs C](../results/graphs/timing_speedup_vs_c.png)

The publication-style timing overview condenses the full timing surface into one cleaner figure for report use, while the normalized timing figure shows how Java and Python move relative to the C baseline across the same workloads. In the normalized figure, `1.0x` indicates parity with C and values above `1.0x` indicate slower median in-process timing than C.
