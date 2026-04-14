# VI. Discussion

The revised benchmark supports stronger claims than the original repository version because the experiment design is tighter:

- Shared inputs remove cross-language randomness as a confounder.
- Warm-up rows make the Java measurements more informative than a cold-start-only run.
- Median summaries reduce the impact of single-run noise.
- Explicit search cases avoid presenting best-case search timings as if they were representative.

The results still need to be interpreted carefully. This is one machine, one operating system, and one set of language runtimes. The timer measures only the in-process algorithm section after setup, so startup costs and input loading are excluded from `elapsed_ns`. That makes the metric cleaner than an end-to-end wall-clock run, but it also means the numbers should be read as algorithm-section timings under this harness, not as full application latency. The visible Java spread in several configurations also means the medians are better treated as practical observations than as evidence of steady-state JVM performance. This remains a repository-level systems exercise, not a highly controlled microbenchmark lab setup.
