# II. Background

## A. Cross-Language Benchmarking Context

Cross-language benchmarking is difficult because the comparison is never just "algorithm versus algorithm." It also reflects compiler strategy, runtime services, memory layout, timer choice, and measurement policy. Mytkowicz et al. show how apparently harmless environmental changes can produce incorrect benchmarking conclusions [1]. Georges et al. make the same point for managed runtimes: startup behavior, warm-up policy, and statistics materially affect what the results mean [2].

This project therefore treats methodological control as part of the deliverable, not as incidental scaffolding around the code. The benchmark uses deterministic shared inputs and a language-agnostic comparison counter to keep the algorithmic workload aligned, which is conceptually similar to the workload-normalization goals seen in cross-language benchmarking work such as Marr et al. [4].

## B. C

C serves as the unmanaged native baseline in this repository. Because it compiles ahead of time and executes without a managed runtime, it is useful as a reference point for the in-process timing of the same algorithmic work. The C measurements still reflect the chosen compiler, flags, operating system, allocator behavior, and timer implementation; they should not be treated as a hardware-level lower bound.

## C. Java

Java executes on the JVM, where optimization can depend on code shape, call frequency, and warm-up behavior. That makes repeated trials and warm-up policy necessary even for a small benchmark [2][3][11]. The current repository uses warm-up rows before measured rows within each benchmark configuration, which is better than a cold-start-only run but weaker than a dedicated JVM benchmarking harness.

## D. Python

This project measures CPython, the reference implementation of Python written in C [5]. Because CPython is interpreted and dynamically typed, small algorithm kernels often expose higher runtime overhead than equivalent native or JIT-compiled loops. The Python benchmarking community addresses this with dedicated tooling such as `pyperf`, which adds loop calibration, worker processes, and environment-tuning guidance [9]. This repository adopts the spirit of loop calibration through batched trials, but not the full `pyperf` execution model.
