"""Generate shared deterministic benchmark input files."""

from __future__ import annotations

import csv
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "data" / "benchmark_inputs"
MANIFEST_PATH = OUTPUT_DIR / "manifest.csv"
DEFAULT_N = [10, 25, 50, 100, 200, 500, 1000, 2000, 5000]
DISTRIBUTIONS = ("random", "ascending", "descending")
BASE_SEED = 20260413


def build_dataset(n: int, distribution: str) -> list[int]:
    if distribution == "ascending":
        return list(range(n))
    if distribution == "descending":
        return list(range(n - 1, -1, -1))
    values = list(range(n))
    random.Random(BASE_SEED + n).shuffle(values)
    return values


def write_dataset(path: Path, values: list[int]) -> None:
    path.write_text(" ".join(str(value) for value in values), encoding="utf-8")


def generate_inputs(n_values: list[int] | None = None) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[tuple[str, str, int, str]] = []

    for n in (n_values or DEFAULT_N):
        for distribution in DISTRIBUTIONS:
            input_id = f"{distribution}_n{n}"
            relative_path = Path("data") / "benchmark_inputs" / f"{input_id}.txt"
            values = build_dataset(n, distribution)
            write_dataset(REPO_ROOT / relative_path, values)
            manifest_rows.append((input_id, distribution, n, relative_path.as_posix()))

    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("input_id", "distribution", "N", "path"))
        writer.writerows(manifest_rows)

    return MANIFEST_PATH


def main() -> int:
    manifest = generate_inputs()
    print(f"wrote deterministic benchmark inputs to {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
