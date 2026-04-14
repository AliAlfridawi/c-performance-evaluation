"""Collect raw benchmark trial rows across C, Java, and Python."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "results" / "data" / "benchmark_runs.csv"
DEFAULT_N = [10, 25, 50, 100, 200, 500, 1000, 2000, 5000]
DEFAULT_TRIALS = 20
DEFAULT_WARMUP = 5
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
            specs[(spec.distribution, spec.n)] = spec
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


def find_maven_executable() -> str | None:
    which = shutil.which("mvn")
    if which:
        return which
    base = Path.home() / "scoop" / "apps" / "maven"
    if not base.is_dir():
        return None
    for path in sorted(base.glob("*/bin/mvn.cmd"), reverse=True):
        return str(path)
    for path in sorted(base.glob("*/bin/mvn"), reverse=True):
        return str(path)
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


def parse_rows(text: str) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != len(HEADER):
            continue
        if parts[0] not in ("python", "c", "java"):
            continue
        rows.append(tuple(parts))
    return rows


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


def run_java(mvn_exe: str, java_home: Path | None, case: BenchCase, trials: int, warmup: int) -> tuple[int, str]:
    args = " ".join(
        [
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
    )
    cmd = [
        mvn_exe,
        "-q",
        "exec:java",
        "-Dexec.mainClass=bench.Benchmark",
        f"-Dexec.args={args}",
    ]
    env = None
    if java_home is not None:
        env = os.environ.copy()
        env["JAVA_HOME"] = str(java_home)
        env["PATH"] = str(java_home / "bin") + os.pathsep + env.get("PATH", "")
    return _run(cmd, cwd=REPO_ROOT, env=env)


def collect(
    output_csv: Path,
    n_values: list[int],
    trials: int,
    warmup: int,
    languages: list[str] | None,
) -> None:
    manifest = ensure_input_manifest()
    inputs = load_inputs(manifest, n_values)
    cases = build_cases(inputs, n_values)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    wanted = set(languages) if languages else {"python", "c", "java"}
    runners: dict[str, object] = {}
    if "python" in wanted:
        runners["python"] = run_python

    if "c" in wanted:
        c_exe = find_c_benchmark()
        if c_exe:
            runners["c"] = lambda case, t, w: run_c(c_exe, case, t, w)
        else:
            print("warning: C benchmark not found (build src/c/benchmark.exe or benchmark)", file=sys.stderr)

    if "java" in wanted:
        mvn_exe = find_maven_executable()
        java_home = find_java_home()
        if mvn_exe and java_home is not None:
            runners["java"] = lambda case, t, w: run_java(mvn_exe, java_home, case, t, w)
        else:
            if not mvn_exe:
                print("warning: mvn not found (install Maven or add to PATH)", file=sys.stderr)
            else:
                print("warning: JDK not found (set JAVA_HOME or install a JDK)", file=sys.stderr)

    rows: list[tuple[str, ...]] = []
    for case in cases:
        for language, runner in runners.items():
            code, output = runner(case, trials, warmup)  # type: ignore[misc]
            if code != 0:
                print(
                    f"warning: {language} failed ({case.algorithm},{case.distribution},N={case.n},{case.search_case}): {output[:240]}",
                    file=sys.stderr,
                )
                continue
            parsed = parse_rows(output)
            if not parsed:
                print(
                    f"warning: could not parse {language} output ({case.algorithm},{case.distribution},N={case.n},{case.search_case})",
                    file=sys.stderr,
                )
                continue
            rows.extend(parsed)

    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerows(rows)

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
        choices=["python", "c", "java"],
        help="Subset of languages (default: all available)",
    )
    args = parser.parse_args()

    n_values = list(args.n) if args.n else DEFAULT_N
    collect(args.output, n_values, args.trials, args.warmup, args.languages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
