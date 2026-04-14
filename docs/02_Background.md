# II. Background

## A. C

C serves as the unmanaged native baseline in this repository. Because it compiles ahead of time and exposes arrays without a managed runtime layer, it is useful for observing how much overhead remains once the algorithmic work is held constant [1][3].

## B. Java

Java executes on the JVM and can apply runtime optimizations after code has been exercised. That makes warm-up policy important. If the benchmark launches a new JVM for every sample and never warms it up, conclusions about steady-state Java performance are weak [2][3].

## C. Python

This project measures CPython, the original and most widely used implementation of Python, written in C [4]. Because Python remains interpreted and dynamically typed, small algorithm kernels can expose more runtime overhead than comparable native or JIT-compiled loops even when the comparison counts match [1][3][4].
