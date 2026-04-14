"""Emit raw benchmark trial rows as CSV."""

from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path
from typing import Literal, Sequence

from algorithms import (
    binary_search,
    get_comparison_count,
    linear_search,
    quick_sort,
    reset_comparison_count,
)

Distribution = Literal["random", "ascending", "descending"]
Algorithm = Literal["quicksort", "linear_search", "binary_search"]
SearchCase = Literal["sort", "first_hit", "middle_hit", "last_hit", "miss"]

MIN_BATCH_TIME_NS = 500_000


def build_array(n: int, distribution: Distribution, seed: int) -> list[int]:
    if n <= 0:
        return []
    if distribution == "ascending":
        return list(range(n))
    if distribution == "descending":
        return list(range(n - 1, -1, -1))
    values = list(range(n))
    random.Random(seed).shuffle(values)
    return values


def load_array(path: Path) -> list[int]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [int(token) for token in text.split()]


def derive_input_id(path: Path | None, distribution: Distribution, n: int) -> str:
    if path is None:
        return f"{distribution}_n{n}"
    return path.stem


def pick_search_target(arr: Sequence[int], search_case: SearchCase) -> int:
    if not arr:
        return 0
    if search_case == "first_hit":
        return arr[0]
    if search_case == "middle_hit":
        return arr[len(arr) // 2]
    if search_case == "last_hit":
        return arr[-1]
    if search_case == "miss":
        return max(arr) + 1
    raise ValueError(f"unsupported search case for searches: {search_case}")


def default_search_case(algorithm: Algorithm) -> SearchCase:
    if algorithm == "quicksort":
        return "sort"
    if algorithm == "linear_search":
        return "first_hit"
    return "middle_hit"


def run_quicksort_once(base_arr: Sequence[int]) -> tuple[int, int]:
    work = list(base_arr)
    reset_comparison_count()
    t0 = time.perf_counter_ns()
    quick_sort(work)
    elapsed_ns = time.perf_counter_ns() - t0
    return get_comparison_count(), elapsed_ns


def run_batched_trial(
    algorithm: Algorithm,
    base_arr: Sequence[int],
    search_case: SearchCase,
) -> tuple[int, int, int]:
    linear_target = pick_search_target(base_arr, search_case) if algorithm == "linear_search" else 0
    sorted_arr = sorted(base_arr) if algorithm == "binary_search" else []
    binary_target = pick_search_target(sorted_arr, search_case) if algorithm == "binary_search" else 0
    batch_loops = 0
    total_elapsed_ns = 0
    comparisons = 0

    while batch_loops == 0 or total_elapsed_ns < MIN_BATCH_TIME_NS:
        if algorithm == "quicksort":
            comparisons, elapsed_ns = run_quicksort_once(base_arr)
        elif algorithm == "linear_search":
            reset_comparison_count()
            t0 = time.perf_counter_ns()
            linear_search(base_arr, linear_target)
            elapsed_ns = time.perf_counter_ns() - t0
            comparisons = get_comparison_count()
        else:
            reset_comparison_count()
            t0 = time.perf_counter_ns()
            binary_search(sorted_arr, binary_target)
            elapsed_ns = time.perf_counter_ns() - t0
            comparisons = get_comparison_count()

        total_elapsed_ns += elapsed_ns
        batch_loops += 1

    return comparisons, total_elapsed_ns, batch_loops


def emit_trials(
    algorithm: Algorithm,
    distribution: Distribution,
    base_arr: Sequence[int],
    input_id: str,
    search_case: SearchCase,
    trials: int,
    warmup: int,
) -> None:
    total_rows = warmup + trials
    for idx in range(total_rows):
        comparisons, elapsed_ns, batch_loops = run_batched_trial(algorithm, base_arr, search_case)
        is_warmup = 1 if idx < warmup else 0
        trial_no = idx + 1
        print(
            ",".join(
                [
                    "python",
                    algorithm,
                    distribution,
                    input_id,
                    str(len(base_arr)),
                    search_case,
                    str(trial_no),
                    str(is_warmup),
                    str(comparisons),
                    str(elapsed_ns),
                    str(batch_loops),
                ]
            ),
            flush=True,
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark one algorithm configuration.")
    parser.add_argument(
        "algorithm",
        choices=["quicksort", "linear_search", "binary_search"],
        help="Algorithm to run",
    )
    parser.add_argument(
        "distribution",
        choices=["random", "ascending", "descending"],
        help="Dataset distribution label",
    )
    parser.add_argument("n", type=int, help="Array length N")
    parser.add_argument("--seed", type=int, default=42, help="Seed for generated random inputs")
    parser.add_argument("--input-file", type=Path, help="Whitespace-separated input file")
    parser.add_argument("--trials", type=int, default=1, help="Measured trial count")
    parser.add_argument("--warmup", type=int, default=0, help="Warm-up trial count")
    parser.add_argument(
        "--search-case",
        choices=["sort", "first_hit", "middle_hit", "last_hit", "miss"],
        help="Search scenario; quicksort uses sort",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.n < 0:
        print("N must be non-negative", file=sys.stderr)
        return 2
    if args.trials <= 0:
        print("trials must be positive", file=sys.stderr)
        return 2
    if args.warmup < 0:
        print("warmup must be non-negative", file=sys.stderr)
        return 2

    search_case: SearchCase = args.search_case or default_search_case(args.algorithm)
    if args.algorithm == "quicksort" and search_case != "sort":
        print("quicksort only supports --search-case sort", file=sys.stderr)
        return 2
    if args.algorithm != "quicksort" and search_case == "sort":
        print("search algorithms require a search hit/miss case", file=sys.stderr)
        return 2

    if args.input_file is not None:
        if not args.input_file.is_file():
            print(f"input file not found: {args.input_file}", file=sys.stderr)
            return 2
        base_arr = load_array(args.input_file)
        if len(base_arr) != args.n:
            print(
                f"N mismatch: expected {args.n}, input file contains {len(base_arr)} values",
                file=sys.stderr,
            )
            return 2
        input_id = derive_input_id(args.input_file, args.distribution, args.n)
    else:
        base_arr = build_array(args.n, args.distribution, args.seed)
        input_id = derive_input_id(None, args.distribution, args.n)

    emit_trials(
        args.algorithm,
        args.distribution,
        base_arr,
        input_id,
        search_case,
        args.trials,
        args.warmup,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
