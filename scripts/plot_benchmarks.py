"""Plot median benchmark summaries from raw trial data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = REPO_ROOT / "results" / "data" / "benchmark_runs.csv"
DEFAULT_SUMMARY = REPO_ROOT / "results" / "data" / "benchmark_summary.csv"
DEFAULT_OUT = REPO_ROOT / "results" / "graphs"
DEFAULT_LANGUAGES = ("c", "java", "python")
QUICKSORT_DISTRIBUTIONS = ("random", "ascending", "descending")
SEARCH_ALGORITHMS = ("linear_search", "binary_search")

LANG_STYLE = {
    "c": {"color": "#1f77b4", "label": "C"},
    "java": {"color": "#ff7f0e", "label": "Java"},
    "python": {"color": "#2ca02c", "label": "Python"},
}

DIST_LABELS = {"random": "Random", "ascending": "Ascending", "descending": "Descending"}
SEARCH_CASE_LABELS = {
    "first_hit": "First hit",
    "middle_hit": "Middle hit",
    "last_hit": "Last hit",
    "miss": "Miss",
}


class SummaryValidationError(RuntimeError):
    """Raised when raw benchmark data is incomplete or internally inconsistent."""


def load_trials(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    numeric_cols = ("N", "trial", "warmup", "comparisons", "elapsed_ns", "batch_loops")
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["language", "algorithm", "distribution", "N", "elapsed_ns", "batch_loops"])
    df["language"] = df["language"].str.lower().str.strip()
    df["seconds_per_run"] = df["elapsed_ns"] / df["batch_loops"].clip(lower=1) / 1_000_000_000.0
    return df


def _expected_group_keys(n_values: list[int], languages: list[str]) -> set[tuple[str, str, str, str, int, str]]:
    expected: set[tuple[str, str, str, str, int, str]] = set()
    for n in n_values:
        for distribution in QUICKSORT_DISTRIBUTIONS:
            input_id = f"{distribution}_n{n}"
            for language in languages:
                expected.add((language, "quicksort", distribution, input_id, n, "sort"))
        for algorithm in SEARCH_ALGORITHMS:
            input_id = f"ascending_n{n}"
            for search_case in SEARCH_CASE_LABELS:
                for language in languages:
                    expected.add((language, algorithm, "ascending", input_id, n, search_case))
    return expected


def validate_trials(df: pd.DataFrame, *, strict: bool = True) -> None:
    if df.empty:
        raise SummaryValidationError("no rows in raw benchmark CSV")

    present_languages = sorted(df["language"].dropna().unique().tolist())
    if not present_languages:
        raise SummaryValidationError("raw benchmark CSV does not contain any languages")

    languages = list(DEFAULT_LANGUAGES) if strict else present_languages
    if strict:
        missing_languages = sorted(set(DEFAULT_LANGUAGES) - set(present_languages))
        if missing_languages:
            raise SummaryValidationError(
                "raw benchmark CSV is missing required languages: " + ", ".join(missing_languages)
            )

    group_cols = ["language", "algorithm", "distribution", "input_id", "N", "search_case"]
    group_counts = (
        df.groupby(group_cols, as_index=False)
        .agg(
            warmup_rows=("warmup", lambda s: int((s == 1).sum())),
            measured_rows=("warmup", lambda s: int((s == 0).sum())),
            invalid_warmup=("warmup", lambda s: int((~s.isin([0, 1])).sum())),
            comparison_variants=("comparisons", "nunique"),
        )
    )

    if (group_counts["invalid_warmup"] > 0).any():
        raise SummaryValidationError("raw benchmark CSV contains invalid warmup flags")
    if (group_counts["comparison_variants"] != 1).any():
        raise SummaryValidationError("raw benchmark CSV contains inconsistent comparison counts within a group")

    measured_counts = sorted(group_counts["measured_rows"].unique().tolist())
    warmup_counts = sorted(group_counts["warmup_rows"].unique().tolist())
    if len(measured_counts) != 1 or measured_counts[0] <= 0:
        raise SummaryValidationError("raw benchmark CSV has inconsistent measured-trial counts across groups")
    if len(warmup_counts) != 1:
        raise SummaryValidationError("raw benchmark CSV has inconsistent warmup counts across groups")

    n_values = sorted(int(value) for value in df["N"].dropna().unique().tolist())
    expected_groups = _expected_group_keys(n_values, languages)
    actual_groups = {
        (
            row.language,
            row.algorithm,
            row.distribution,
            row.input_id,
            int(row.N),
            row.search_case,
        )
        for row in group_counts.itertuples(index=False)
        if row.language in languages
    }

    missing_groups = sorted(expected_groups - actual_groups)
    if missing_groups:
        preview = ", ".join(
            f"{language}:{algorithm}/{distribution}/N={n}/{search_case}"
            for language, algorithm, distribution, _input_id, n, search_case in missing_groups[:6]
        )
        raise SummaryValidationError("raw benchmark CSV is missing expected groups: " + preview)

    unexpected_groups = sorted(actual_groups - expected_groups)
    if unexpected_groups:
        preview = ", ".join(
            f"{language}:{algorithm}/{distribution}/N={n}/{search_case}"
            for language, algorithm, distribution, _input_id, n, search_case in unexpected_groups[:6]
        )
        raise SummaryValidationError("raw benchmark CSV contains unexpected groups: " + preview)

    comparison_frame = (
        df.groupby(group_cols, as_index=False)
        .agg(comparisons=("comparisons", "first"))
        .groupby(["algorithm", "distribution", "input_id", "N", "search_case"], as_index=False)
        .agg(comparison_variants=("comparisons", "nunique"))
    )
    if (comparison_frame["comparison_variants"] != 1).any():
        raise SummaryValidationError("raw benchmark CSV contains cross-language comparison-count mismatches")


def summarize_trials(df: pd.DataFrame) -> pd.DataFrame:
    measured = df[df["warmup"] == 0].copy()
    if measured.empty:
        return measured
    group_cols = ["language", "algorithm", "distribution", "input_id", "N", "search_case"]
    summary = (
        measured.groupby(group_cols, as_index=False)
        .agg(
            median_seconds=("seconds_per_run", "median"),
            min_seconds=("seconds_per_run", "min"),
            max_seconds=("seconds_per_run", "max"),
            median_comparisons=("comparisons", "median"),
            trials=("trial", "count"),
            median_batch_loops=("batch_loops", "median"),
        )
        .sort_values(["algorithm", "distribution", "search_case", "language", "N"])
    )
    return summary


def _plot_series(ax, group: pd.DataFrame, *, value_col: str, label: str, color: str) -> None:
    group = group.sort_values("N")
    ax.plot(group["N"], group[value_col], marker="o", ms=4, color=color, label=label)
    ax.fill_between(group["N"], group["min_seconds"], group["max_seconds"], color=color, alpha=0.15)


def plot_quicksort(summary: pd.DataFrame, out: Path) -> None:
    sub = summary[summary["algorithm"] == "quicksort"]
    if sub.empty:
        return

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    for ax, distribution in zip(axes, ("random", "ascending", "descending")):
        dist_df = sub[sub["distribution"] == distribution]
        for language in ("c", "java", "python"):
            group = dist_df[dist_df["language"] == language]
            if group.empty:
                continue
            style = LANG_STYLE[language]
            _plot_series(ax, group, value_col="median_seconds", label=style["label"], color=style["color"])
        ax.set_title(DIST_LABELS[distribution])
        ax.set_xlabel("N")
        ax.set_yscale("log")
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("Median seconds per run")
    axes[0].legend()
    fig.suptitle("Quick sort timing (median with min-max band)")
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_search(summary: pd.DataFrame, algorithm: str, out: Path) -> None:
    sub = summary[(summary["algorithm"] == algorithm) & (summary["distribution"] == "ascending")]
    if sub.empty:
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, sharey=True)
    for ax, search_case in zip(axes.flatten(), ("first_hit", "middle_hit", "last_hit", "miss")):
        case_df = sub[sub["search_case"] == search_case]
        for language in ("c", "java", "python"):
            group = case_df[case_df["language"] == language]
            if group.empty:
                continue
            style = LANG_STYLE[language]
            _plot_series(ax, group, value_col="median_seconds", label=style["label"], color=style["color"])
        ax.set_title(SEARCH_CASE_LABELS[search_case])
        ax.set_xlabel("N")
        ax.set_yscale("log")
        ax.grid(True, alpha=0.3)
    axes[0][0].set_ylabel("Median seconds per run")
    axes[1][0].set_ylabel("Median seconds per run")
    axes[0][0].legend()
    title = "Linear search timing" if algorithm == "linear_search" else "Binary search timing"
    fig.suptitle(f"{title} (median with min-max band)")
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_comparisons(summary: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=False)

    quicksort = summary[summary["algorithm"] == "quicksort"]
    for distribution in ("random", "ascending", "descending"):
        dist_df = quicksort[quicksort["distribution"] == distribution]
        ax = axes[0]
        for language in ("c", "java", "python"):
            group = dist_df[dist_df["language"] == language]
            if group.empty:
                continue
            style = LANG_STYLE[language]
            ax.plot(
                group["N"],
                group["median_comparisons"],
                marker="o",
                ms=3,
                linestyle={"random": "-", "ascending": "--", "descending": ":"}[distribution],
                color=style["color"],
                label=f"{style['label']} {DIST_LABELS[distribution]}",
            )
    axes[0].set_title("Quick sort comparisons")
    axes[0].set_xlabel("N")
    axes[0].set_ylabel("Median comparisons")
    axes[0].grid(True, alpha=0.3)

    for ax, algorithm in zip(axes[1:], ("linear_search", "binary_search")):
        sub = summary[(summary["algorithm"] == algorithm) & (summary["distribution"] == "ascending")]
        for language in ("c", "java", "python"):
            for search_case in ("first_hit", "middle_hit", "last_hit", "miss"):
                group = sub[(sub["language"] == language) & (sub["search_case"] == search_case)]
                if group.empty:
                    continue
                style = LANG_STYLE[language]
                ax.plot(
                    group["N"],
                    group["median_comparisons"],
                    marker="o",
                    ms=3,
                    linestyle={
                        "first_hit": "-",
                        "middle_hit": "--",
                        "last_hit": ":",
                        "miss": "-.",
                    }[search_case],
                    color=style["color"],
                    label=f"{style['label']} {SEARCH_CASE_LABELS[search_case]}",
                )
        ax.set_title("Linear search comparisons" if algorithm == "linear_search" else "Binary search comparisons")
        ax.set_xlabel("N")
        ax.grid(True, alpha=0.3)

    axes[0].legend(fontsize=7)
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_all(raw_csv: Path, summary_csv: Path, out_dir: Path, *, strict: bool = True) -> None:
    trials = load_trials(raw_csv)
    validate_trials(trials, strict=strict)
    summary = summarize_trials(trials)
    if summary.empty:
        raise SummaryValidationError("no measured trials found in raw benchmark CSV")

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_csv.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_csv, index=False)

    plot_quicksort(summary, out_dir / "quicksort_median_time.png")
    plot_search(summary, "linear_search", out_dir / "linear_search_median_time.png")
    plot_search(summary, "binary_search", out_dir / "binary_search_median_time.png")
    plot_comparisons(summary, out_dir / "comparison_counts.png")


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot benchmark summaries from raw trial CSV.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Raw trial CSV path")
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY, help="Summary CSV output")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Graph output directory")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Plot partial raw data instead of requiring a complete three-language benchmark matrix",
    )
    args = parser.parse_args()

    if not args.csv.is_file():
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        return 1

    try:
        run_all(args.csv, args.summary_out, args.out, strict=not args.allow_partial)
    except SummaryValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"summary written to {args.summary_out}")
    print(f"graphs written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
