# Algorithmic Benchmark Report

This folder contains the supporting report for the benchmark harness in this repository. The report is aligned to the current checked-in datasets, summary statistics, metadata sidecar, and regenerated figures.

## Sections

1. [Abstract](00_Abstract.md)
2. [Introduction](01_Introduction.md)
3. [Background](02_Background.md)
4. [Methodology](03_Methodology.md)
5. [Experimental Setup](04_Experimental_Setup.md)
6. [Results and Analysis](05_Results_and_Analysis.md)
7. [Discussion](06_Discussion.md)
8. [Conclusion](07_Conclusion.md)
9. [References](08_References.md)

## Repository Artifacts Used by the Report

- `data/benchmark_inputs/manifest.csv`
- `results/data/benchmark_runs.csv`
- `results/data/benchmark_summary.csv`
- `results/data/benchmark_metadata.json`
- `results/graphs/*.png`, including `comparison_counts.png`, `timing_overview.png`, and `timing_speedup_vs_c.png`

`benchmark_summary.csv` now carries quartiles, IQR, min/max spread, standard deviation, and 95% bootstrap confidence intervals for the median. `benchmark_metadata.json` records the host, toolchain, build configuration, command templates, and artifact hashes used for the checked-in report snapshot.
