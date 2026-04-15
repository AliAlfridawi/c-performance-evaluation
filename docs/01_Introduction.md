# I. Introduction

Asymptotic complexity explains how work grows, but it does not explain how that work is realized inside different runtimes and toolchains. Even small algorithm kernels can expose meaningful differences in native compilation, JIT optimization, interpreter dispatch, allocation behavior, and timer policy. That is why cross-language performance comparisons are easy to overstate and easy to misread.

This repository studies a deliberately narrow problem. It compares the same small set of algorithms in three environments:

- C with ahead-of-time native compilation
- Java on the JVM
- Python on CPython

The central research question is:

> When the algorithmic workload is held constant through shared deterministic inputs and cross-language comparison-count parity, what in-process timing differences remain for quicksort, linear search, and binary search on this host?

The project also tests two working hypotheses:

- `H1`: comparison counts will match across languages for every published benchmark configuration if the workload definitions are aligned correctly.
- `H2`: C and Java will remain closer to each other than either remains to Python on these small algorithm kernels, even after setup costs are excluded from the timed region.

The intended contribution is not a broad claim about “which language is fastest.” It is a transparent benchmark harness with explicit scope boundaries, preserved raw data, and enough methodological detail to support careful interpretation. That contribution has three parts:

- a shared-input benchmark matrix that removes language-specific random-input generation from the published runs
- a workload-control check based on comparison-count parity across languages
- a reproducible reporting pipeline that publishes raw trials, summary statistics, figures, and machine-readable metadata together

That framing matters because prior work shows that environment noise, warm-up behavior, weak statistics, and mismatched workloads can all distort performance claims [1][2][3]. The goal here is therefore narrower and more defensible: produce a benchmark artifact whose claims are limited to what the code and measurements actually support.
