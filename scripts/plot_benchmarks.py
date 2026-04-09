"""
Generate benchmark graphs from results/data/benchmark_runs.csv into results/graphs/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = REPO_ROOT / "results" / "data" / "benchmark_runs.csv"
DEFAULT_OUT = REPO_ROOT / "results" / "graphs"

LANG_STYLE = {
    "c": {"color": "#1f77b4", "label": "C"},
    "java": {"color": "#ff7f0e", "label": "Java"},
    "python": {"color": "#2ca02c", "label": "Python"},
}

ALGORITHMS = ("quicksort", "linear_search", "binary_search")
ALGO_LABELS = {
    "quicksort": "Quick sort",
    "linear_search": "Linear search",
    "binary_search": "Binary search",
}
DISTRIBUTIONS = ("random", "ascending", "descending")
DIST_LABELS = {"random": "Random", "ascending": "Ascending", "descending": "Descending"}


def _safe_legend(ax, **kwargs) -> None:
    h, labels = ax.get_legend_handles_labels()
    if h:
        ax.legend(h, labels, **kwargs)


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ("N", "comparisons", "seconds"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["language", "algorithm", "distribution", "N", "seconds"])
    df["language"] = df["language"].str.lower().str.strip()
    return df


def plot_cross_time_faceted(df: pd.DataFrame, out: Path, log_y: bool = True) -> None:
    fig, axes = plt.subplots(
        len(ALGORITHMS), len(DISTRIBUTIONS), figsize=(14, 12), sharex=True, sharey=False
    )
    for i, algo in enumerate(ALGORITHMS):
        for j, dist in enumerate(DISTRIBUTIONS):
            ax = axes[i][j]
            sub = df[(df["algorithm"] == algo) & (df["distribution"] == dist)]
            for lang in sorted(sub["language"].unique()):
                g = sub[sub["language"] == lang].sort_values("N")
                if g.empty:
                    continue
                st = LANG_STYLE.get(lang, {"color": "gray", "label": lang})
                ax.plot(
                    g["N"],
                    g["seconds"],
                    marker="o",
                    ms=3,
                    color=st["color"],
                    label=st["label"],
                )
            ax.set_title(f"{ALGO_LABELS[algo]} — {DIST_LABELS[dist]}")
            ax.grid(True, alpha=0.3)
            if log_y:
                ax.set_yscale("log")
            if j == 0:
                ax.set_ylabel("Time (s)")
            if i == len(ALGORITHMS) - 1:
                ax.set_xlabel("N")
            _safe_legend(ax, fontsize=8, loc="upper left")
    fig.suptitle("Execution time vs N (by algorithm and distribution)", fontsize=14)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_cross_comparisons_faceted(df: pd.DataFrame, out: Path, log_y: bool = True) -> None:
    fig, axes = plt.subplots(
        len(ALGORITHMS), len(DISTRIBUTIONS), figsize=(14, 12), sharex=True, sharey=False
    )
    for i, algo in enumerate(ALGORITHMS):
        for j, dist in enumerate(DISTRIBUTIONS):
            ax = axes[i][j]
            sub = df[(df["algorithm"] == algo) & (df["distribution"] == dist)]
            for lang in sorted(sub["language"].unique()):
                g = sub[sub["language"] == lang].sort_values("N")
                if g.empty:
                    continue
                st = LANG_STYLE.get(lang, {"color": "gray", "label": lang})
                ax.plot(
                    g["N"],
                    g["comparisons"],
                    marker="o",
                    ms=3,
                    color=st["color"],
                    label=st["label"],
                )
            ax.set_title(f"{ALGO_LABELS[algo]} — {DIST_LABELS[dist]}")
            ax.grid(True, alpha=0.3)
            if log_y:
                ax.set_yscale("log")
            if j == 0:
                ax.set_ylabel("Comparisons")
            if i == len(ALGORITHMS) - 1:
                ax.set_xlabel("N")
            _safe_legend(ax, fontsize=8, loc="upper left")
    fig.suptitle(
        "Comparison count vs N (ascending/descending should overlap across languages)",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_speedup_vs_c(df: pd.DataFrame, out: Path) -> None:
    if "c" not in df["language"].values:
        return
    fig, axes = plt.subplots(len(ALGORITHMS), len(DISTRIBUTIONS), figsize=(14, 12), sharex=True)
    for i, algo in enumerate(ALGORITHMS):
        for j, dist in enumerate(DISTRIBUTIONS):
            ax = axes[i][j]
            base_df = df[
                (df["language"] == "c")
                & (df["algorithm"] == algo)
                & (df["distribution"] == dist)
            ][["N", "seconds"]].rename(columns={"seconds": "sec_c"})
            if base_df.empty:
                continue
            for lang in ("java", "python"):
                g = df[
                    (df["language"] == lang)
                    & (df["algorithm"] == algo)
                    & (df["distribution"] == dist)
                ][["N", "seconds"]]
                if g.empty:
                    continue
                merged = g.merge(base_df, on="N", how="inner")
                if merged.empty:
                    continue
                merged = merged[merged["sec_c"] > 0]
                if merged.empty:
                    continue
                ratio = merged["seconds"] / merged["sec_c"]
                st = LANG_STYLE[lang]
                ax.plot(
                    merged["N"],
                    ratio,
                    marker="o",
                    ms=3,
                    color=st["color"],
                    label=st["label"],
                )
            ax.axhline(1.0, color="#666", linestyle="--", linewidth=1)
            ax.set_title(f"{ALGO_LABELS[algo]} — {DIST_LABELS[dist]}")
            ax.grid(True, alpha=0.3)
            ax.set_yscale("log")
            if j == 0:
                ax.set_ylabel("Time / time(C)")
            if i == len(ALGORITHMS) - 1:
                ax.set_xlabel("N")
            _safe_legend(ax, fontsize=7, loc="upper left")
    fig.suptitle("Speedup vs C (time_language / time_C)", fontsize=14)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_grouped_bars(df: pd.DataFrame, out_dir: Path, n_list: list[int]) -> None:
    available = sorted(set(n_list) & set(df["N"].unique()))
    if not available:
        return
    langs = sorted(df["language"].unique())
    if not langs:
        return
    n_lang = len(langs)
    x = np.arange(len(ALGORITHMS))
    width = min(0.8 / max(n_lang, 1), 0.25)
    for dist in DISTRIBUTIONS:
        fig, axes = plt.subplots(1, len(available), figsize=(4 * len(available), 5), sharey=True)
        if len(available) == 1:
            axes = [axes]
        for ax_i, n in enumerate(available):
            ax = axes[ax_i]
            for li, lang in enumerate(langs):
                times = []
                for algo in ALGORITHMS:
                    row = df[
                        (df["language"] == lang)
                        & (df["algorithm"] == algo)
                        & (df["distribution"] == dist)
                        & (df["N"] == n)
                    ]
                    times.append(float(row["seconds"].iloc[0]) if len(row) else 0.0)
                offset = (li - (n_lang - 1) / 2) * width
                ax.bar(
                    x + offset,
                    times,
                    width,
                    label=LANG_STYLE.get(lang, {"label": lang})["label"],
                    color=LANG_STYLE.get(lang, {"color": "gray"})["color"],
                )
            ax.set_xticks(x)
            ax.set_xticklabels([ALGO_LABELS[a] for a in ALGORITHMS], rotation=15, ha="right")
            ax.set_title(f"N = {n}")
            ax.set_ylabel("Time (s)")
            ax.grid(True, axis="y", alpha=0.3)
        fig.suptitle(f"Execution time by language — {DIST_LABELS[dist]}")
        legend_el = [
            Patch(facecolor=LANG_STYLE[l]["color"], edgecolor="gray", label=LANG_STYLE[l]["label"])
            for l in langs
        ]
        fig.legend(handles=legend_el, loc="upper right", bbox_to_anchor=(1.0, 1.0))
        fig.tight_layout()
        fig.savefig(out_dir / f"grouped_bars_{dist}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def plot_heatmaps(df: pd.DataFrame, out_dir: Path, ref_n: int | None) -> None:
    for dist in DISTRIBUTIONS:
        sub = df[df["distribution"] == dist]
        if sub.empty:
            continue
        n_use = ref_n if ref_n is not None else int(sub["N"].max())
        sub = sub[sub["N"] == n_use]
        if sub.empty:
            n_use = int(df[df["distribution"] == dist]["N"].max())
            sub = df[(df["distribution"] == dist) & (df["N"] == n_use)]
        pivot = sub.pivot_table(
            index="language",
            columns="algorithm",
            values="seconds",
            aggfunc="mean",
        )
        if pivot.empty:
            continue
        fig, ax = plt.subplots(figsize=(8, 4))
        im = ax.imshow(np.log10(pivot.values + 1e-15), aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([ALGO_LABELS.get(c, c) for c in pivot.columns])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_title(f"log10(time) heatmap — {DIST_LABELS[dist]} — N={n_use}")
        plt.colorbar(im, ax=ax, label="log10(seconds)")
        fig.tight_layout()
        fig.savefig(out_dir / f"heatmap_time_{dist}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def plot_per_language_time(df: pd.DataFrame, out_dir: Path, log_y: bool = True) -> None:
    for lang in sorted(df["language"].unique()):
        sub = df[df["language"] == lang]
        fig, ax = plt.subplots(figsize=(10, 6))
        for algo in ALGORITHMS:
            for dist in DISTRIBUTIONS:
                g = sub[(sub["algorithm"] == algo) & (sub["distribution"] == dist)].sort_values("N")
                if g.empty:
                    continue
                label = f"{ALGO_LABELS[algo]} ({DIST_LABELS[dist]})"
                ax.plot(g["N"], g["seconds"], marker="o", ms=3, label=label)
        ax.set_title(f"Execution time vs N — {LANG_STYLE.get(lang, {'label': lang})['label']}")
        ax.set_xlabel("N")
        ax.set_ylabel("Time (s)")
        if log_y:
            ax.set_yscale("log")
        ax.grid(True, alpha=0.3)
        _safe_legend(ax, fontsize=7, loc="upper left", ncol=2)
        fig.tight_layout()
        fig.savefig(out_dir / f"per_language_time_{lang}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def plot_per_language_comparisons(df: pd.DataFrame, out_dir: Path, log_y: bool = True) -> None:
    for lang in sorted(df["language"].unique()):
        sub = df[df["language"] == lang]
        fig, ax = plt.subplots(figsize=(10, 6))
        for algo in ALGORITHMS:
            for dist in DISTRIBUTIONS:
                g = sub[(sub["algorithm"] == algo) & (sub["distribution"] == dist)].sort_values("N")
                if g.empty:
                    continue
                label = f"{ALGO_LABELS[algo]} ({DIST_LABELS[dist]})"
                ax.plot(g["N"], g["comparisons"], marker="o", ms=3, label=label)
        ax.set_title(f"Comparison count vs N — {LANG_STYLE.get(lang, {'label': lang})['label']}")
        ax.set_xlabel("N")
        ax.set_ylabel("Comparisons")
        if log_y:
            ax.set_yscale("log")
        ax.grid(True, alpha=0.3)
        _safe_legend(ax, fontsize=7, loc="upper left", ncol=2)
        fig.tight_layout()
        fig.savefig(out_dir / f"per_language_comparisons_{lang}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def plot_distribution_effect_quicksort(df: pd.DataFrame, out_dir: Path) -> None:
    for lang in sorted(df["language"].unique()):
        sub = df[(df["language"] == lang) & (df["algorithm"] == "quicksort")]
        if sub.empty:
            continue
        fig, ax = plt.subplots(figsize=(8, 5))
        for dist in DISTRIBUTIONS:
            g = sub[sub["distribution"] == dist].sort_values("N")
            if g.empty:
                continue
            ax.plot(g["N"], g["seconds"], marker="o", ms=4, label=DIST_LABELS[dist])
        ax.set_title(
            f"Quick sort: distribution effect — {LANG_STYLE.get(lang, {'label': lang})['label']}"
        )
        ax.set_xlabel("N")
        ax.set_ylabel("Time (s)")
        ax.set_yscale("log")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / f"dist_effect_quicksort_{lang}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def plot_throughput(df: pd.DataFrame, out_dir: Path) -> None:
    """N / seconds as a rough throughput proxy (large for fast runs)."""
    df = df.copy()
    df["throughput"] = df["seconds"].clip(lower=1e-15)
    df["throughput"] = df["N"] / df["throughput"]
    for lang in sorted(df["language"].unique()):
        sub = df[df["language"] == lang]
        fig, ax = plt.subplots(figsize=(10, 6))
        for algo in ALGORITHMS:
            for dist in DISTRIBUTIONS:
                g = sub[(sub["algorithm"] == algo) & (sub["distribution"] == dist)].sort_values("N")
                if g.empty:
                    continue
                label = f"{ALGO_LABELS[algo]} ({DIST_LABELS[dist]})"
                ax.plot(g["N"], g["throughput"], marker="o", ms=2, label=label)
        ax.set_title(f"Throughput proxy (N / s) — {LANG_STYLE.get(lang, {'label': lang})['label']}")
        ax.set_xlabel("N")
        ax.set_ylabel("N / seconds")
        ax.set_yscale("log")
        ax.grid(True, alpha=0.3)
        _safe_legend(ax, fontsize=7, loc="upper left", ncol=2)
        fig.tight_layout()
        fig.savefig(out_dir / f"throughput_{lang}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def plot_summary_total_time(df: pd.DataFrame, out: Path) -> None:
    tot = df.groupby("language")["seconds"].sum().sort_values()
    if tot.empty:
        return
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = [LANG_STYLE.get(l, {"color": "gray"})["color"] for l in tot.index]
    tot.plot(kind="bar", ax=ax, color=colors)
    ax.set_ylabel("Sum of seconds (full CSV)")
    ax.set_title("Non-scientific aggregate: total benchmark time in dataset")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_prng_note(out: Path) -> None:
    fig = plt.figure(figsize=(10, 2))
    fig.text(
        0.05,
        0.5,
        "Note: For random inputs, C/Python/Java use different PRNGs — comparison counts and times\n"
        "may diverge across languages for the same seed. Ascending/descending inputs are deterministic.",
        fontsize=11,
        va="center",
        wrap=True,
    )
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_all(csv_path: Path, out_dir: Path, heatmap_n: int | None) -> None:
    df = load_csv(csv_path)
    if df.empty:
        print("no data in CSV", file=sys.stderr)
        return
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_cross_time_faceted(df, out_dir / "cross_time_vs_n_faceted.png")
    plot_cross_comparisons_faceted(df, out_dir / "cross_comparisons_vs_n_faceted.png")
    if "c" in df["language"].values:
        plot_speedup_vs_c(df, out_dir / "cross_speedup_vs_c.png")
    plot_grouped_bars(df, out_dir, n_list=[500, 2000, 5000])
    plot_heatmaps(df, out_dir, heatmap_n)
    plot_per_language_time(df, out_dir)
    plot_per_language_comparisons(df, out_dir)
    plot_distribution_effect_quicksort(df, out_dir)
    plot_throughput(df, out_dir)
    plot_summary_total_time(df, out_dir / "summary_total_seconds_by_language.png")
    plot_prng_note(out_dir / "note_prng_random_inputs.png")


def main() -> int:
    p = argparse.ArgumentParser(description="Plot benchmark graphs from CSV.")
    p.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument(
        "--heatmap-n",
        type=int,
        default=None,
        help="N for heatmaps (default: max N per distribution in CSV)",
    )
    args = p.parse_args()
    if not args.csv.is_file():
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        return 1
    run_all(args.csv, args.out, args.heatmap_n)
    print(f"graphs written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
