# VII. Conclusion

The experiment provides a baseline for a small-scale, multi-language benchmark suite. The code, datasets, and analysis align to provide a consistent view of performance under the defined conditions.

The benchmark shows three clear patterns:

- identical comparison counts across languages when the algorithm and inputs are held constant
- large differences in observed in-process execution time under this harness
- search behavior that depends strongly on the exact lookup case being measured

This demonstrates that while algorithms define the theoretical behavior, runtime environments significantly influence the observed performance, even when the underlying work is constant.
