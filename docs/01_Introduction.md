# I. Introduction

Algorithm analysis usually starts with asymptotic complexity, but real programs execute inside runtimes and toolchains with different overhead models. This repository compares the same small set of algorithms in three environments:

- C with ahead-of-time native compilation
- Java on the JVM
- Python on CPython

The research question is intentionally narrow: if the algorithmic workload is held constant through shared deterministic inputs and cross-language comparison-count parity, what in-process timing differences remain for quicksort, linear search, and binary search on this host?

The project is not designed to answer broader questions such as "which language is fastest overall?" or "what is the end-to-end latency of real applications?" Those questions require a different workload mix and stronger environment control. The point of this repository is instead to build a benchmark harness whose measurement boundary, assumptions, and limitations are explicit enough to survive senior-engineering review.

That framing matters because cross-language benchmarking is easy to get wrong. Public guidance and prior research show that weak workload control, insufficient warm-up, environmental confounders, and overconfident interpretation can all produce misleading conclusions [1][2][3]. The goal here is therefore twofold: generate useful benchmark data and document exactly what the data does and does not mean.
