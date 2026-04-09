# IV. Experimental Setup

The benchmarks were executed in a controlled environment to minimize external interference.

### A. Environment
- **Compiler/Runtime:**
    - C: GCC 11.0+ (C11 standard) with `-O2` optimization.
    - Java: OpenJDK 17 (Temurin) with Maven-driven execution.
    - Python: CPython 3.10+ with standard library implementations.
- **System:** x86_64 architecture (Win32).

### B. Instrumentation
All implementations were modified to include a global or object-scoped comparison counter. Timing was measured only for the core algorithmic execution, excluding dataset generation and I/O overhead.
