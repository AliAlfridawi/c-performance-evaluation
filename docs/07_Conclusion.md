# VII. Conclusion

The repository is now in a better state for both technical review and recruiter review. The code, CSVs, plots, and documentation all describe the same experiment, and the main claims are limited to what the regenerated evidence supports.

The benchmark shows three clear patterns:

- identical comparison counts across languages when the algorithm and inputs are held constant
- large differences in observed in-process execution time under this harness
- search behavior that depends strongly on the exact lookup case being measured

Future improvements could add memory metrics, CPU affinity controls, or extra languages such as Rust or Go, but the current version is already a reproducible baseline for this repository-level harness.
