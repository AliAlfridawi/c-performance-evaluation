# II. Background and Related Work

### A. Compiled Languages (C)
C is a statically typed, compiled language that provides low-level memory access and minimal runtime abstraction. Compilers like GCC apply aggressive optimizations (e.g., `-O2`), resulting in code that maps closely to machine instructions.

### B. JIT-Compiled Languages (Java)
Java employs a bytecode-based execution model. The Java Virtual Machine (JVM) uses a Just-In-Time (JIT) compiler to translate bytecode into native machine code at runtime. This allows for profile-guided optimizations but introduces a "warm-up" period where performance may be suboptimal.

### C. Interpreted Languages (Python)
Python is a dynamically typed, interpreted language. The standard implementation (CPython) executes code on a virtual machine by interpreting bytecode line-by-line. While this offers high flexibility and developer productivity, it introduces significant overhead for computational tasks.
