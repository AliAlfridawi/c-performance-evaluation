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


def load_trials(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    numeric_cols = ("N", "trial", "warmup", "comparisons", "elapsed_ns", "batch_loops")
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["language", "algorithm", "distribution", "N", "elapsed_ns", "batch_loops"])
    df["language"] = df["language"].str.lower().str.strip()
    df["seconds_per_run"] = df["elapsed_ns"] / df["batch_loops"].clip(lower=1) / 1_000_000_000.0
    return df


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


def run_all(raw_csv: Path, summary_csv: Path, out_dir: Path) -> None:
    trials = load_trials(raw_csv)
    if trials.empty:
        print("no rows in raw benchmark CSV", file=sys.stderr)
        return
    summary = summarize_trials(trials)
    if summary.empty:
        print("no measured trials found in raw benchmark CSV", file=sys.stderr)
        return

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
    args = parser.parse_args()

    if not args.csv.is_file():
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        return 1

    run_all(args.csv, args.summary_out, args.out)
    print(f"summary written to {args.summary_out}")
    print(f"graphs written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
