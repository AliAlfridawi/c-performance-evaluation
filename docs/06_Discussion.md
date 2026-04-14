# VI. Discussion

The revised benchmark supports stronger claims than the original repository version because the experiment design is tighter:

- Shared inputs remove cross-language randomness as a confounder.
- Warm-up rows make the Java measurements more informative than a cold-start-only run.
- Median summaries reduce the impact of single-run noise.
- Explicit search cases avoid presenting best-case search timings as if they were representative.

The results still need to be interpreted carefully. This is one machine, one operating system, and one set of language runtimes. The timer measures only the in-process algorithm section after setup, so startup costs and input loading are excluded from `elapsed_ns`. That makes the metric cleaner than an end-to-end wall-clock run, but it also means the numbers should be read as algorithm-section timings under this harness, not as full application latency. The visible Java spread in several configurations also means the medians are better treated as practical observations than as evidence of steady-state JVM performance [3].

## A. Threats to Validity

- **Hardware Dependence**: Measurements are restricted to a single CPU architecture and memory subsystem. Results may vary on different hardware.
- **Operating System Effects**: Background processes and the OS scheduler introduce noise into timings [2]. While the median reduces this impact, it remains a factor.
- **Timer Resolution**: High-resolution timers differ by platform. The C implementation uses `QueryPerformanceCounter` on Windows [7], Java uses `System.nanoTime()` [6], and Python uses `time.perf_counter_ns()` [5].
- **Excluded Costs**: Memory allocation, input/output, and runtime initialization are intentionally excluded from the timing, though they are significant in real-world applications.
