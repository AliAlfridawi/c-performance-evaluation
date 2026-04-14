"""Collect raw benchmark trial rows across C, Java, and Python."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "results" / "data" / "benchmark_runs.csv"
DEFAULT_N = [10, 25, 50, 100, 200, 500, 1000, 2000, 5000]
DEFAULT_TRIALS = 20
DEFAULT_WARMUP = 5
DEFAULT_LANGUAGES = ("python", "c", "java")
QUICKSORT_DISTRIBUTIONS = ("random", "ascending", "descending")
SEARCH_ALGORITHMS = ("linear_search", "binary_search")
SEARCH_CASES = ("first_hit", "middle_hit", "last_hit", "miss")
HEADER = (
    "language",
    "algorithm",
    "distribution",
    "input_id",
    "N",
    "search_case",
    "trial",
    "warmup",
    "comparisons",
    "elapsed_ns",
    "batch_loops",
)
CASE_FIELDS = ("algorithm", "distribution", "input_id", "N", "search_case")
GROUP_FIELDS = ("language",) + CASE_FIELDS


class CollectionValidationError(RuntimeError):
    """Raised when the collector cannot produce a complete, consistent dataset."""


@dataclass(frozen=True)
class InputSpec:
    input_id: str
    distribution: str
    n: int
    path: Path


@dataclass(frozen=True)
class BenchCase:
    algorithm: str
    distribution: str
    n: int
    input_spec: InputSpec
    search_case: str


Runner = Callable[[BenchCase, int, int], tuple[int, str]]


def ensure_input_manifest() -> Path:
    manifest = REPO_ROOT / "data" / "benchmark_inputs" / "manifest.csv"
    generator = REPO_ROOT / "data" / "DataSetGenerator.py"
    if manifest.is_file():
        return manifest
    cmd = [sys.executable, str(generator)]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to generate benchmark inputs")
    return manifest


def load_inputs(manifest: Path, n_values: list[int]) -> dict[tuple[str, int], InputSpec]:
    selected_n = set(n_values)
    specs: dict[tuple[str, int], InputSpec] = {}
    with manifest.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            n = int(row["N"])
            if n not in selected_n:
                continue
            spec = InputSpec(
                input_id=row["input_id"],
                distribution=row["distribution"],
                n=n,
                path=REPO_ROOT / row["path"],
            )
            if (spec.distribution, spec.n) in specs:
                raise CollectionValidationError(
                    f"duplicate manifest entry for distribution={spec.distribution}, N={spec.n}"
                )
            specs[(spec.distribution, spec.n)] = spec

    missing = [
        f"{distribution},N={n}"
        for n in n_values
        for distribution in QUICKSORT_DISTRIBUTIONS
        if (distribution, n) not in specs
    ]
    if missing:
        raise CollectionValidationError(
            "benchmark input manifest is missing required datasets: " + "; ".join(missing)
        )
    return specs


def build_cases(inputs: dict[tuple[str, int], InputSpec], n_values: list[int]) -> list[BenchCase]:
    cases: list[BenchCase] = []
    for n in n_values:
        for distribution in ("random", "ascending", "descending"):
            input_spec = inputs[(distribution, n)]
            cases.append(BenchCase("quicksort", distribution, n, input_spec, "sort"))

        search_input = inputs[("ascending", n)]
        for algorithm in ("linear_search", "binary_search"):
            for search_case in SEARCH_CASES:
                cases.append(BenchCase(algorithm, "ascending", n, search_input, search_case))
    return cases


def find_c_benchmark() -> Path | None:
    for name in ("benchmark.exe", "benchmark"):
        path = REPO_ROOT / "src" / "c" / name
        if path.is_file():
            return path
    return None


def find_java_home() -> Path | None:
    java_home = os.environ.get("JAVA_HOME", "").strip()
    if java_home:
        root = Path(java_home)
        if (root / "bin" / "java.exe").is_file() or (root / "bin" / "java").is_file():
            return root
    apps = Path.home() / "scoop" / "apps"
    if not apps.is_dir():
        return None
    for pattern in ("temurin*-jdk", "openjdk*", "microsoft*-jdk", "corretto*"):
        for directory in sorted(apps.glob(pattern), reverse=True):
            for nested in directory.glob("*/bin/java.exe"):
                return nested.parent.parent
            if (directory / "bin" / "java.exe").is_file():
                return directory
    return None


def find_java_executable() -> str | None:
    java_home = find_java_home()
    if java_home is not None:
        for name in ("java.exe", "java"):
            candidate = java_home / "bin" / name
            if candidate.is_file():
                return str(candidate)
    return shutil.which("java")


def find_java_classes_dir() -> Path | None:
    classes_dir = REPO_ROOT / "target" / "classes"
    benchmark_class = classes_dir / "bench" / "Benchmark.class"
    if benchmark_class.is_file():
        return classes_dir
    return None


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[int, str]:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=900,
        )
        output = (result.stdout or "").strip()
        if result.returncode != 0 and result.stderr:
            output = output + "\n" + result.stderr.strip()
        return result.returncode, output
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def parse_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != len(HEADER):
            continue
        if parts[0] not in ("python", "c", "java"):
            continue
        rows.append(dict(zip(HEADER, parts)))
    return rows


def _case_key(case: BenchCase) -> tuple[str, str, str, str, str]:
    return (
        case.algorithm,
        case.distribution,
        case.input_spec.input_id,
        str(case.n),
        case.search_case,
    )


def _group_key_from_row(row: dict[str, str]) -> tuple[str, str, str, str, str, str]:
    return tuple(row[field] for field in GROUP_FIELDS)


def _expected_group_key(language: str, case: BenchCase) -> tuple[str, str, str, str, str, str]:
    return (language,) + _case_key(case)


def _parse_int_field(row: dict[str, str], field: str) -> int | None:
    try:
        return int(row[field])
    except (KeyError, ValueError):
        return None


def validate_case_rows(
    rows: list[dict[str, str]],
    case: BenchCase,
    language: str,
    trials: int,
    warmup: int,
) -> list[str]:
    errors: list[str] = []
    expected_total = trials + warmup
    expected_group = _expected_group_key(language, case)

    if len(rows) != expected_total:
        errors.append(
            f"{language} produced {len(rows)} rows for "
            f"({case.algorithm},{case.distribution},N={case.n},{case.search_case}); "
            f"expected {expected_total}"
        )

    seen_trials: set[int] = set()
    comparisons: set[int] = set()
    for row in rows:
        actual_group = _group_key_from_row(row)
        if actual_group != expected_group:
            errors.append(
                f"{language} emitted mismatched row fields for "
                f"({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
            )
            break

        trial_no = _parse_int_field(row, "trial")
        warmup_flag = _parse_int_field(row, "warmup")
        batch_loops = _parse_int_field(row, "batch_loops")
        comparison_count = _parse_int_field(row, "comparisons")

        if trial_no is None or not 1 <= trial_no <= expected_total:
            errors.append(
                f"{language} emitted invalid trial index {row['trial']} for "
                f"({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
            )
        else:
            seen_trials.add(trial_no)
            expected_warmup_flag = 1 if trial_no <= warmup else 0
            if warmup_flag != expected_warmup_flag:
                errors.append(
                    f"{language} emitted incorrect warmup flag for trial {trial_no} in "
                    f"({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
                )

        if batch_loops is None or batch_loops <= 0:
            errors.append(
                f"{language} emitted invalid batch_loops={row['batch_loops']} for "
                f"({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
            )

        if comparison_count is None or comparison_count < 0:
            errors.append(
                f"{language} emitted invalid comparisons={row['comparisons']} for "
                f"({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
            )
        elif comparison_count is not None:
            comparisons.add(comparison_count)

    if seen_trials and seen_trials != set(range(1, expected_total + 1)):
        errors.append(
            f"{language} emitted non-contiguous trial numbering for "
            f"({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
        )

    if len(comparisons) > 1:
        errors.append(
            f"{language} emitted inconsistent comparison counts for "
            f"({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
        )

    return errors


def validate_collection_rows(
    rows: list[dict[str, str]],
    cases: list[BenchCase],
    languages: list[str],
    trials: int,
    warmup: int,
) -> list[str]:
    errors: list[str] = []
    expected_total = trials + warmup
    grouped: dict[tuple[str, str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[_group_key_from_row(row)].append(row)

    expected_groups = {_expected_group_key(language, case) for case in cases for language in languages}
    actual_groups = set(grouped)

    missing_groups = sorted(expected_groups - actual_groups)
    if missing_groups:
        preview = ", ".join(
            f"{language}:{algorithm}/{distribution}/N={n}/{search_case}"
            for language, algorithm, distribution, _input_id, n, search_case in missing_groups[:6]
        )
        errors.append(f"missing benchmark groups: {preview}")

    unexpected_groups = sorted(actual_groups - expected_groups)
    if unexpected_groups:
        preview = ", ".join(
            f"{language}:{algorithm}/{distribution}/N={n}/{search_case}"
            for language, algorithm, distribution, _input_id, n, search_case in unexpected_groups[:6]
        )
        errors.append(f"unexpected benchmark groups: {preview}")

    for key, group_rows in grouped.items():
        if len(group_rows) != expected_total:
            language, algorithm, distribution, _input_id, n, search_case = key
            errors.append(
                f"{language} has {len(group_rows)} rows for "
                f"({algorithm},{distribution},N={n},{search_case}); expected {expected_total}"
            )

    for case in cases:
        comparison_counts: dict[str, int] = {}
        for language in languages:
            key = _expected_group_key(language, case)
            if key not in grouped:
                continue
            values = {
                comparison
                for comparison in (_parse_int_field(row, "comparisons") for row in grouped[key])
                if comparison is not None
            }
            if len(values) == 1:
                comparison_counts[language] = next(iter(values))
        if len(set(comparison_counts.values())) > 1:
            errors.append(
                "comparison-count mismatch across languages for "
                f"({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
            )

    return errors


def write_rows(output_csv: Path, rows: list[dict[str, str]]) -> None:
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        for row in rows:
            writer.writerow([row[column] for column in HEADER])


def run_python(case: BenchCase, trials: int, warmup: int) -> tuple[int, str]:
    cmd = [
        sys.executable,
        "benchmark.py",
        case.algorithm,
        case.distribution,
        str(case.n),
        "--input-file",
        str(case.input_spec.path),
        "--trials",
        str(trials),
        "--warmup",
        str(warmup),
        "--search-case",
        case.search_case,
    ]
    return _run(cmd, cwd=REPO_ROOT / "src" / "python")


def run_c(exe: Path, case: BenchCase, trials: int, warmup: int) -> tuple[int, str]:
    cmd = [
        str(exe),
        case.algorithm,
        case.distribution,
        str(case.n),
        "--input-file",
        str(case.input_spec.path),
        "--trials",
        str(trials),
        "--warmup",
        str(warmup),
        "--search-case",
        case.search_case,
    ]
    return _run(cmd, cwd=REPO_ROOT)


def run_java(java_exe: str, classes_dir: Path, case: BenchCase, trials: int, warmup: int) -> tuple[int, str]:
    cmd = [
        java_exe,
        "-cp",
        str(classes_dir),
        "bench.Benchmark",
        case.algorithm,
        case.distribution,
        str(case.n),
        "--input-file",
        str(case.input_spec.path),
        "--trials",
        str(trials),
        "--warmup",
        str(warmup),
        "--search-case",
        case.search_case,
    ]
    return _run(cmd, cwd=REPO_ROOT)


def collect(
    output_csv: Path,
    n_values: list[int],
    trials: int,
    warmup: int,
    languages: list[str] | None,
    strict: bool = True,
) -> None:
    manifest = ensure_input_manifest()
    inputs = load_inputs(manifest, n_values)
    cases = build_cases(inputs, n_values)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    requested_languages = list(languages) if languages else list(DEFAULT_LANGUAGES)
    wanted = set(requested_languages)
    runners: dict[str, Runner] = {}
    setup_errors: list[str] = []
    if "python" in wanted:
        runners["python"] = run_python

    if "c" in wanted:
        c_exe = find_c_benchmark()
        if c_exe:
            runners["c"] = lambda case, t, w: run_c(c_exe, case, t, w)
        else:
            setup_errors.append("C benchmark not found (build src/c/benchmark.exe or benchmark)")

    if "java" in wanted:
        java_exe = find_java_executable()
        classes_dir = find_java_classes_dir()
        if java_exe and classes_dir is not None:
            runners["java"] = lambda case, t, w: run_java(java_exe, classes_dir, case, t, w)
        else:
            if not java_exe:
                setup_errors.append("Java runtime not found (install a JDK or set JAVA_HOME)")
            if classes_dir is None:
                setup_errors.append("Java benchmark classes not found (run `mvn -q -DskipTests compile` first)")

    if not runners:
        raise CollectionValidationError("no runnable benchmark targets are available")

    if strict and setup_errors:
        raise CollectionValidationError("\n".join(setup_errors))
    for message in setup_errors:
        print(f"warning: {message}", file=sys.stderr)

    rows: list[dict[str, str]] = []
    run_errors: list[str] = []
    active_languages = [language for language in requested_languages if language in runners]
    for case in cases:
        for language in active_languages:
            runner = runners[language]
            code, output = runner(case, trials, warmup)  # type: ignore[misc]
            if code != 0:
                run_errors.append(
                    f"{language} failed ({case.algorithm},{case.distribution},N={case.n},{case.search_case}): {output[:240]}"
                )
                continue
            parsed = parse_rows(output)
            if not parsed:
                run_errors.append(
                    f"could not parse {language} output ({case.algorithm},{case.distribution},N={case.n},{case.search_case})"
                )
                continue
            case_errors = validate_case_rows(parsed, case, language, trials, warmup)
            if case_errors:
                run_errors.extend(case_errors)
                continue
            rows.extend(parsed)

    validation_errors = validate_collection_rows(rows, cases, active_languages, trials, warmup)
    errors = run_errors + validation_errors
    if errors:
        if strict:
            raise CollectionValidationError("\n".join(errors))
        for message in errors:
            print(f"warning: {message}", file=sys.stderr)

    write_rows(output_csv, rows)

    print(f"wrote {len(rows)} raw trial rows to {output_csv}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect raw benchmark data across languages.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS, help="Measured trials per config")
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP, help="Warm-up trials per config")
    parser.add_argument(
        "--n",
        type=int,
        nargs="*",
        default=None,
        help="N values to sweep (default: built-in series)",
    )
    parser.add_argument(
        "--languages",
        nargs="*",
        choices=list(DEFAULT_LANGUAGES),
        help="Subset of languages (default: all available)",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Write partial data and emit warnings instead of failing on missing or inconsistent cases",
    )
    args = parser.parse_args()

    n_values = list(args.n) if args.n else DEFAULT_N
    try:
        collect(args.output, n_values, args.trials, args.warmup, args.languages, strict=not args.allow_partial)
    except CollectionValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
