# V. Results and Analysis

## A. Quick Sort

![Quick sort timing](../results/graphs/quicksort_median_time.png)

Comparison counts match across languages for every quick sort configuration, so the timing gaps reflect runtime overhead rather than mismatched work. At `N=5000` on random input:

- C median: `0.000132 s`
- Java median: `0.000316 s`
- Python median: `0.012126 s`

The current median-of-three partition logic also changes the sorted-input behavior relative to the older CSVs that were still checked into the repository.

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

The summary CSV shows no comparison-count mismatches across languages for any published configuration. That is the strongest evidence that the shared-input protocol is working.
