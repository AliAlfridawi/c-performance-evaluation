# I. Introduction

Algorithm analysis usually starts with asymptotic complexity, but real software runs inside toolchains and runtimes with different overhead models. This project compares the same core algorithms in three environments:

- C with ahead-of-time native compilation
- Java on the JVM
- Python on CPython

The goal is not to produce a universal ranking of languages. The goal is to build a small, reproducible benchmark harness that keeps the algorithmic workload constant and makes the measurement tradeoffs explicit. This allows for a structured exploration of how language-specific abstractions and runtime environments influence the observed performance of fundamental algorithms.
