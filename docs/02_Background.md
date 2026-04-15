# II. Background

## A. Cross-Language Benchmarking Context

Cross-language benchmarking compares more than source code. It also compares compilation strategy, runtime services, object layout, memory management, timer behavior, and measurement policy. Mytkowicz et al. show how small environmental differences can produce misleading conclusions even when the benchmark appears unchanged [1]. Georges et al. make the same point for managed runtimes, where startup behavior, warm-up policy, and statistics materially affect what a measurement means [2].

For that reason, this repository treats methodological control as part of the research artifact rather than as invisible scaffolding. Shared input files define the workload. Comparison counters test whether that workload stayed aligned across languages. The reporting pipeline preserves raw trial rows so the published figures can be audited back to source data.

## B. C

C provides the ahead-of-time compiled native baseline in this repository. That baseline is useful because it excludes a managed runtime and makes the timed region comparatively direct. It is still not a hardware-level lower bound: the C measurements depend on the chosen compiler, optimization flags, operating system, allocator behavior, and timer implementation.

## C. Java

Java executes on the JVM, where optimization can depend on call history, code shape, and warm-up behavior. Repeated trials and explicit warm-up rows are therefore necessary even for a small benchmark [2][3]. This repository uses a fixed warm-up policy rather than adaptive steady-state detection, which makes the Java measurements more informative than a cold-start-only run but weaker than a dedicated JVM harness such as JMH [11].

## D. Python

This repository measures CPython, the reference Python implementation written largely in C [5]. Because CPython is interpreted and dynamically typed, small algorithm kernels often expose higher dispatch and object-model overhead than equivalent native or JIT-compiled loops. Python benchmarking guidance such as `pyperf` responds to this with loop calibration, worker processes, and system-tuning recommendations [9]. The current repository adopts the loop-calibration idea through batched trials, but not the full `pyperf` process model.

## E. Positioning

The method in this repository is strongest where many casual cross-language benchmarks are weakest: workload definition and internal traceability. It is weaker where specialized benchmark frameworks are strongest: environment isolation, runtime-specific warm-up control, and inferential statistics. The remainder of the report keeps that balance explicit.
