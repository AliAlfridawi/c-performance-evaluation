# VI. Discussion

### A. The "Python Penalty"
The analysis confirms that Python's interpretation overhead is a dominant factor. Even though the iteration counts are identical to C for deterministic inputs, the constant factor in execution time is massive.

### B. Java Warm-up and Peak Performance
Java's performance is initially hampered by JVM startup and JIT compilation. However, for large $N$, the JIT-optimized code performs remarkably close to native C, demonstrating the efficacy of modern bytecode optimization.

### C. C and Machine Efficiency
C remains the gold standard for computational tasks where every CPU cycle counts. The lack of a runtime manager or garbage collector allows for predictable and peak performance.
