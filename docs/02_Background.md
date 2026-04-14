# II. Background

## A. C

C offers low-level control, direct array access, and minimal runtime abstraction. In a benchmark like this, that usually translates to small constant factors and predictable execution behavior.

## B. Java

Java executes on the JVM and can apply runtime optimizations after code has been exercised. That makes warm-up policy important. If the benchmark launches a new JVM for every sample and never warms it up, conclusions about steady-state Java performance are weak.

## C. Python

CPython prioritizes flexibility and developer speed over raw loop throughput. For small algorithm kernels, interpreter overhead often dominates the measured runtime even when the comparison counts match a lower-level implementation.
