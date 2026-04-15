# VI. Discussion

## A. Final Methodology Review

The final review concluded that the benchmark design is methodologically sound for a narrow exploratory purpose. The strongest aspects are:

- shared deterministic inputs instead of language-specific random generation
- explicit scenario coverage for search benchmarks
- preserved warm-up rows and repeated measured trials
- batching of very short operations before normalization
- raw-trial retention and strict validation of missing or inconsistent groups

The most important limitation is scope rather than correctness. The metric is intentionally narrow: `elapsed_ns` covers only the in-process algorithm section after setup. That makes the timing boundary cleaner, but it also means the numbers should not be read as end-to-end application latency, full runtime cost, or universal language rankings.

Two other interpretation limits must remain explicit. First, fixed warm-up counts do not prove that the JVM reached a stable steady state [2][3]. Second, the run was performed on one Windows host under a balanced power plan with no CPU affinity control or background-load isolation. The methodology is therefore defensible as an engineering benchmark harness, but not equivalent to a dedicated lab-grade performance study.

## B. Comparison to Related Evaluations and Guidance

Georges et al. argue that Java performance evaluation should separate startup effects from steady-state behavior and should use statistically rigorous analysis rather than ad hoc samples [2]. This repository aligns with that guidance in part: it records repeated trials, separates warm-up from measured rows, and uses medians instead of single samples. It is still materially weaker than the standard they outline because it does not attempt steady-state detection, confidence intervals, or more formal inferential analysis.

Mytkowicz et al. show how environmental confounders can invalidate benchmark conclusions even when the code under test appears unchanged [1]. The repository responds to that lesson by using shared on-disk datasets, fixed benchmark matrices, and strict validation of published groups. The remaining gap is environment control: CPU affinity, background services, and power-management effects are documented as uncontrolled rather than engineered away.

Barrett et al. demonstrate that VM warm-up behavior can be irregular and that simplistic warm-up assumptions can fail [3]. That is directly relevant here. The current `5` warm-up trials are a practical compromise, not evidence that Java has converged to a steady-state regime. The documentation therefore treats Java timings as harness-specific observations instead of "true JVM peak performance."

Marr et al. emphasize the importance of language-agnostic workload definitions in cross-language benchmarking [4]. This repository is strongest on that dimension: shared datasets and comparison-count parity make it much better controlled than the typical "same idea, different implementation" benchmark. The scope is also much smaller than Marr et al.: only three algorithms, one machine, and one set of runtime versions.

Public tooling and benchmark projects illustrate the same tradeoff in a complementary way. `pyperf` calibrates loop counts, uses worker processes, and documents system-tuning practices for Python benchmarks [9]. JMH is explicitly designed as a dedicated Java benchmarking harness [11]. The Computer Language Benchmarks Game distinguishes between externally measured wall-clock time and in-process timing views [10]. Compared with those systems, this repository is strong on transparency and workload matching, but weaker on isolation, automation of warm-up strategy, and breadth of performance metrics.

Taken together, these comparisons support a clear verdict: the methodology is sound for a transparent repository benchmark, stronger than many casual cross-language comparisons, and weaker than specialized performance harnesses. That is an acceptable position as long as the report states this explicitly.

## C. Threats to Validity

- **Single-machine dependence**: Results were collected on one Windows 11 host with one CPU model, one power plan, and one runtime/toolchain set.
- **Environment noise**: Scheduler activity, background processes, thermal behavior, and power management remain uncontrolled confounders [1][9].
- **Limited warm-up model**: JVM optimization and garbage-collection behavior are not instrumented, and fixed warm-up counts do not guarantee a steady state [2][3].
- **Narrow timing boundary**: Startup, file loading, and binary-search presorting are deliberately excluded, so the metric does not represent full application latency [10].
- **Exploratory statistics**: Median, min/max, and standard deviation are appropriate descriptive summaries here, but they are not a substitute for formal confidence intervals or hypothesis tests [2].
- **Kernel-level workload bias**: Small algorithm kernels can amplify interpreter and dispatch overhead relative to workloads dominated by library calls or I/O.

## D. Recommended Next Steps

If the repository needs to move closer to publication-grade benchmarking, the next upgrades should be:

- record full host metadata alongside every regeneration
- add optional CPU-affinity and background-noise controls
- add a complementary end-to-end wall-clock metric alongside the current in-process metric
- evaluate Java with a dedicated JMH companion benchmark for a steadier warm-up model
- add stronger statistical treatment if precise cross-runtime claims become a requirement
