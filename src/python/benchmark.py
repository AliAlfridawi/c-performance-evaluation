"""CLI: print one CSV row with language, algorithm, distribution, N, comparisons, seconds."""

from __future__ import annotations

import argparse
import random
import sys
import time
from typing import Literal

from algorithms import (
    binary_search,
    get_comparison_count,
    linear_search,
    quick_sort,
    reset_comparison_count,
)

Distribution = Literal["random", "ascending", "descending"]
Algorithm = Literal["quicksort", "linear_search", "binary_search"]


def build_array(n: int, distribution: Distribution, seed: int) -> list[int]:
    if n <= 0:
        return []
    if distribution == "ascending":
        return list(range(n))
    if distribution == "descending":
        return list(range(n - 1, -1, -1))
    rng = random.Random(seed)
    return [rng.randint(1, 1000) for _ in range(n)]


def run_benchmark(algorithm: Algorithm, distribution: Distribution, n: int, seed: int) -> None:
    arr = build_array(n, distribution, seed)
    if algorithm == "quicksort":
        reset_comparison_count()
        t0 = time.perf_counter()
        quick_sort(arr)
        elapsed = time.perf_counter() - t0
    elif algorithm == "linear_search":
        target = arr[0] if arr else 0
        reset_comparison_count()
        t0 = time.perf_counter()
        linear_search(arr, target)
        elapsed = time.perf_counter() - t0
    else:
        sorted_arr = sorted(arr)
        target = sorted_arr[len(sorted_arr) // 2] if sorted_arr else 0
        reset_comparison_count()
        t0 = time.perf_counter()
        binary_search(sorted_arr, target)
        elapsed = time.perf_counter() - t0
    comparisons = get_comparison_count()
    print(
        f"python,{algorithm},{distribution},{n},{comparisons},{elapsed:.9f}",
        flush=True,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Benchmark one algorithm run (CSV row).")
    p.add_argument(
        "algorithm",
        choices=["quicksort", "linear_search", "binary_search"],
        help="Algorithm to run",
    )
    p.add_argument(
        "distribution",
        choices=["random", "ascending", "descending"],
        help="Input distribution",
    )
    p.add_argument("n", type=int, help="Array length N")
    p.add_argument("--seed", type=int, default=42, help="RNG seed for random distribution")
    args = p.parse_args(argv)
    if args.n < 0:
        print("N must be non-negative", file=sys.stderr)
        return 2
    run_benchmark(args.algorithm, args.distribution, args.n, args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
