# III. Methodology

### A. Algorithms Tested
1.  **Quick Sort:** Evaluated across random, ascending (best/worst), and descending (worst/best) distributions.
2.  **Linear Search:** A sequential search algorithm representing $O(N)$ complexity.
3.  **Binary Search:** A logarithmic search algorithm representing $O(\log N)$ complexity on sorted data.

### B. Performance Metrics
- **Execution Time:** Measured in wall-clock time using high-resolution timers (`clock()` in C, `System.nanoTime()` in Java, and `time.perf_counter()` in Python).
- **Comparison Count:** A hardware-independent metric that tracks the absolute number of fundamental operations performed, ensuring theoretical consistency.

### C. Data Distributions
To capture Average, Best, and Worst Case scenarios, tests were conducted on:
- **Random:** Average case for sorting.
- **Ascending:** Sorted input.
- **Descending:** Reverse-sorted input.
