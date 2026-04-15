# VI. Discussion

## A. Overall Assessment

The benchmark design is methodologically credible for a narrow exploratory purpose. Its strongest features are transparent workload definition, strict cross-language workload checks, preserved raw trials, and explicit publication of both summary statistics and run metadata. Those choices make the artifact substantially stronger than an informal “same algorithm in three languages” comparison.

The main limitation is scope rather than correctness. The metric is intentionally narrow: `elapsed_ns` covers only the in-process algorithm section after setup. That is useful for a tightly defined question, but it is not the same thing as application latency, throughput under service load, or steady-state managed-runtime behavior.

## B. Comparison to Related Guidance

Georges et al. argue that Java performance evaluation should separate startup effects from steady-state behavior and should use statistically rigorous analysis rather than ad hoc sampling [2]. This repository aligns with that guidance in part: it records repeated trials, separates warm-up from measured rows, and publishes a richer descriptive summary than a single median alone. It remains materially weaker than their standard because it does not attempt convergence detection, inferential cross-language statistics, or deeper runtime instrumentation.

Mytkowicz et al. show how environmental confounders can invalidate benchmark conclusions even when the code appears unchanged [1]. The repository responds to that lesson by fixing the workload definition through shared inputs and by validating every published case against cross-language comparison parity. The remaining gap is environment control: CPU affinity, background services, thermal behavior, and power-management effects are documented but not engineered away.

Barrett et al. demonstrate that VM warm-up can be irregular and that simplistic warm-up assumptions may fail [3]. That warning applies directly here. The current `5` warm-up trials are useful for avoiding cold-start-only reporting, but they are not evidence that the JVM has reached a stable optimization regime.

Marr et al. emphasize language-agnostic workload definitions in cross-language compiler benchmarking [4]. This repository is strongest on that exact dimension. Its shared datasets and parity checks create much tighter workload alignment than the common “same idea, different implementation” comparison. Its scope, however, is much smaller than a benchmark suite intended for language-implementation research.

Dedicated tools illustrate the same tradeoff from the tooling side. `pyperf` adds worker processes and system-tuning guidance for Python benchmarks [9], while JMH exists specifically to benchmark JVM code under a more disciplined execution model [11]. Compared with those tools, this repository is more manual and less isolated, but more transparent about the raw benchmark matrix and repository-local artifacts.

## C. Threats to Validity

| Validity type | Mitigation in this repository | Remaining threat |
| --- | --- | --- |
| Internal validity | Shared inputs, explicit benchmark matrix, comparison-count parity, strict validation, preserved raw trials | Environment noise can still perturb timing even when workload is aligned |
| Construct validity | Clear in-process timing boundary, explicit exclusion of startup and presorting, explicit search scenarios | The reported metric is narrower than end-to-end user-visible performance |
| External validity | Host, toolchain, and power plan are documented in `benchmark_metadata.json` | Results are collected on one Windows machine with one set of runtime versions |
| Conclusion validity | `20` measured trials, median-first reporting, quartiles, IQR, bootstrap CI for the median | No formal inferential statistics or cross-language hypothesis tests |

This table is the clearest summary of the repository’s research quality: strong control of what was measured, weaker control over everything that could influence those measurements.

## D. What the Repository Can Defend

The repository can defend the following statements:

- the published benchmark cases impose matched algorithmic work across languages
- substantial timing differences remain after that workload alignment on the documented host
- explicit search-case selection materially changes search behavior and must be reported

It cannot defend the following statements:

- one language is universally faster in general
- the reported medians are end-to-end application latencies
- the Java rows represent confirmed steady-state peak JVM performance

## E. Recommended Next Steps

If the artifact needs to move closer to publication-grade benchmarking, the next upgrades should be:

- add optional CPU-affinity and background-noise controls
- add a complementary end-to-end wall-clock metric alongside the current in-process metric
- add a JMH companion benchmark for the Java kernels
- add repeated regenerations across sessions or machines
- add stronger inferential analysis if precise cross-runtime claims become a requirement
