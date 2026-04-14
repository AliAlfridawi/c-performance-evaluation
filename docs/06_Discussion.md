# VI. Discussion

The revised benchmark supports stronger claims than the original repository version because the experiment design is tighter:

- Shared inputs remove cross-language randomness as a confounder.
- Warm-up rows make the Java measurements more defensible.
- Median summaries reduce the impact of single-run noise.
- Explicit search cases avoid presenting best-case search timings as if they were representative.

The results still need to be interpreted carefully. This is one machine, one operating system, and one set of language runtimes. The harness also launches a separate process per configuration, so startup costs remain part of what is being measured. That is acceptable for a repository-level systems exercise, but it is not the same as a highly controlled microbenchmark lab setup.
