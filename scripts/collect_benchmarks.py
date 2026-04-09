"""
Sweep benchmark CLIs and write results/data/benchmark_runs.csv.

For random distribution, C/Python/Java use different PRNGs, so comparison counts
and timings are not directly comparable across languages for the same seed.
Ascending/descending inputs are deterministic; comparison counts should match.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_N = [10, 25, 50, 100, 200, 500, 1000, 2000, 5000]
ALGORITHMS = ("quicksort", "linear_search", "binary_search")
DISTRIBUTIONS = ("random", "ascending", "descending")
HEADER = ("language", "algorithm", "distribution", "N", "comparisons", "seconds")


def find_c_benchmark() -> Path | None:
    for name in ("benchmark.exe", "benchmark"):
        p = REPO_ROOT / "src" / "c" / name
        if p.is_file():
            return p
    return None


def find_maven_executable() -> str | None:
    w = shutil.which("mvn")
    if w:
        return w
    base = Path.home() / "scoop" / "apps" / "maven"
    if not base.is_dir():
        return None
    for p in sorted(base.glob("*/bin/mvn.cmd"), reverse=True):
        return str(p)
    for p in sorted(base.glob("*/bin/mvn"), reverse=True):
        return str(p)
    return None


def find_java_home() -> Path | None:
    jh = os.environ.get("JAVA_HOME", "").strip()
    if jh:
        root = Path(jh)
        if (root / "bin" / "java.exe").is_file() or (root / "bin" / "java").is_file():
            return root
    apps = Path.home() / "scoop" / "apps"
    if not apps.is_dir():
        return None
    for pattern in ("temurin*-jdk", "openjdk*", "microsoft*-jdk", "corretto*"):
        for d in sorted(apps.glob(pattern), reverse=True):
            for nested in d.glob("*/bin/java.exe"):
                return nested.parent.parent
            if (d / "bin" / "java.exe").is_file():
                return d
    return None


def run_python(algo: str, dist: str, n: int, seed: int) -> tuple[int, str]:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "src" / "python" / "benchmark.py"),
        algo,
        dist,
        str(n),
        "--seed",
        str(seed),
    ]
    return _run(cmd, cwd=REPO_ROOT)


def run_c(exe: Path, algo: str, dist: str, n: int, seed: int) -> tuple[int, str]:
    cmd = [str(exe), algo, dist, str(n), "--seed", str(seed)]
    return _run(cmd, cwd=REPO_ROOT)


def run_java(mvn_exe: str, java_home: Path | None) -> object:
    def inner(algo: str, dist: str, n: int, seed: int) -> tuple[int, str]:
        args = f"{algo} {dist} {n} --seed {seed}"
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

    return inner


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[int, str]:
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
        )
        out = (r.stdout or "").strip()
        if r.returncode != 0 and r.stderr:
            out = out + "\n" + r.stderr.strip()
        return r.returncode, out
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def parse_row(text: str) -> tuple[str, ...] | None:
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("usage:"):
            continue
        parts = line.split(",")
        if len(parts) != 6:
            continue
        if parts[0] not in ("python", "c", "java"):
            continue
        return tuple(p.strip() for p in parts)
    return None


def collect(
    output_csv: Path,
    seed: int,
    n_values: list[int],
    languages: list[str] | None,
) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    c_exe = find_c_benchmark()
    want = set(languages) if languages else {"python", "c", "java"}
    runners: dict[str, object] = {}
    if "python" in want:
        runners["python"] = run_python
    if "c" in want and c_exe:
        runners["c"] = lambda a, d, n, s: run_c(c_exe, a, d, n, s)
    elif "c" in want:
        print("warning: C benchmark not found (build src/c/benchmark.exe or benchmark)", file=sys.stderr)
    if "java" in want:
        mvn_exe = find_maven_executable()
        jdk = find_java_home()
        if mvn_exe and jdk is not None:
            runners["java"] = run_java(mvn_exe, jdk)
        else:
            if not mvn_exe:
                print("warning: mvn not found (install Maven or add to PATH)", file=sys.stderr)
            elif jdk is None:
                print(
                    "warning: JAVA_HOME / JDK not found (set JAVA_HOME or install a JDK, e.g. scoop install temurin17-jdk)",
                    file=sys.stderr,
                )

    rows: list[tuple[str, ...]] = []
    for algo in ALGORITHMS:
        for dist in DISTRIBUTIONS:
            for n in n_values:
                if n < 0:
                    continue
                for lang, runner in runners.items():
                    code, out = runner(algo, dist, n, seed)  # type: ignore[operator]
                    if code != 0:
                        print(
                            f"warning: {lang} failed ({algo},{dist},N={n}): {out[:200]}",
                            file=sys.stderr,
                        )
                        continue
                    parsed = parse_row(out)
                    if not parsed:
                        print(
                            f"warning: could not parse {lang} output ({algo},{dist},N={n})",
                            file=sys.stderr,
                        )
                        continue
                    rows.append(parsed)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)

    print(f"wrote {len(rows)} rows to {output_csv}")


def main() -> int:
    p = argparse.ArgumentParser(description="Collect benchmark CSV across languages.")
    p.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "results" / "data" / "benchmark_runs.csv",
        help="Output CSV path",
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--n",
        type=int,
        nargs="*",
        default=None,
        help="N values to sweep (default: built-in series)",
    )
    p.add_argument(
        "--languages",
        nargs="*",
        choices=["python", "c", "java"],
        help="Subset of languages (default: all available)",
    )
    args = p.parse_args()
    n_vals = list(args.n) if args.n else DEFAULT_N
    collect(args.output, args.seed, n_vals, args.languages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
