# V. Results and Analysis

### A. Execution Time Trends
The disparity in execution time is most evident in the Quick Sort algorithm as $N$ increases.

![Cross Language Time](../results/graphs/cross_time_vs_n_faceted.png)

*Fig 1. Execution time across languages for varied distributions.*

### B. Sorting Distribution Effects
Python shows extreme sensitivity to pre-sorted data when using a standard Quick Sort implementation, while C and Java handle these distributions with significantly less relative penalty.

![Distribution Effect Quicksort Python](../results/graphs/dist_effect_quicksort_python.png)
*Fig 2. Sensitivity of Python Quick Sort to input distribution.*

### C. Speedup vs. C
C serves as the baseline for maximum efficiency. The speedup graph highlights how Java approaches C's performance at scale, while Python remains consistently slower.

![Speedup vs C](../results/graphs/cross_speedup_vs_c.png)
*Fig 3. Speedup of Java and Python relative to C.*
