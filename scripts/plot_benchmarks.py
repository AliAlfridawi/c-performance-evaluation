"""Plot professional benchmark summaries from raw trial data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, LogFormatterMathtext, LogLocator, MaxNLocator, NullFormatter

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = REPO_ROOT / "results" / "data" / "benchmark_runs.csv"
DEFAULT_SUMMARY = REPO_ROOT / "results" / "data" / "benchmark_summary.csv"
DEFAULT_OUT = REPO_ROOT / "results" / "graphs"
DEFAULT_LANGUAGES = ("c", "java", "python")
QUICKSORT_DISTRIBUTIONS = ("random", "ascending", "descending")
SEARCH_ALGORITHMS = ("linear_search", "binary_search")

THEME = {
    "paper": "#f7f5ef",
    "panel": "#fcfbf8",
    "ink": "#2b2722",
    "muted": "#6c6458",
    "grid": "#d8d2c6",
    "grid_minor": "#ece7dc",
    "border": "#8a8377",
    "baseline": "#9a9387",
}

PLOT_THEME = {
    "font.family": "DejaVu Serif",
    "axes.facecolor": THEME["panel"],
    "figure.facecolor": THEME["paper"],
    "savefig.facecolor": THEME["paper"],
    "axes.edgecolor": THEME["border"],
    "axes.labelcolor": THEME["ink"],
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "xtick.color": THEME["ink"],
    "ytick.color": THEME["ink"],
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "grid.color": THEME["grid"],
    "grid.alpha": 0.8,
    "legend.frameon": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
}

LANG_STYLE = {
    "c": {"color": "#355070", "label": "C", "marker": "o"},
    "java": {"color": "#bc6c25", "label": "Java", "marker": "s"},
    "python": {"color": "#4c7a43", "label": "Python", "marker": "D"},
}

DIST_LABELS = {"random": "Random", "ascending": "Ascending", "descending": "Descending"}
SEARCH_CASE_LABELS = {
    "first_hit": "First hit",
    "middle_hit": "Middle hit",
    "last_hit": "Last hit",
    "miss": "Miss",
}
ALGORITHM_LABELS = {
    "quicksort": "Quick sort",
    "linear_search": "Linear search",
    "binary_search": "Binary search",
}

DIST_STYLE = {
    "random": {"label": "Random", "linestyle": "-", "marker": "o", "color": "#355070"},
    "ascending": {"label": "Ascending", "linestyle": "--", "marker": "s", "color": "#9c6b30"},
    "descending": {"label": "Descending", "linestyle": ":", "marker": "^", "color": "#8a4f58"},
}
SEARCH_STYLE = {
    "first_hit": {"label": "First hit", "linestyle": "-", "marker": "o", "color": "#355070"},
    "middle_hit": {"label": "Middle hit", "linestyle": "--", "marker": "s", "color": "#6d8b74"},
    "last_hit": {"label": "Last hit", "linestyle": ":", "marker": "^", "color": "#9c6b30"},
    "miss": {"label": "Miss", "linestyle": "-.", "marker": "D", "color": "#8a4f58"},
}


class SummaryValidationError(RuntimeError):
    """Raised when raw benchmark data is incomplete or internally inconsistent."""


def apply_plot_theme() -> None:
    plt.rcParams.update(PLOT_THEME)


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
            std_seconds=("seconds_per_run", "std"),
            median_comparisons=("comparisons", "median"),
            trials=("trial", "count"),
            median_batch_loops=("batch_loops", "median"),
        )
        .sort_values(["algorithm", "distribution", "search_case", "language", "N"])
    )
    return summary


def _select_xticks(n_values: list[int], max_ticks: int = 5) -> list[int]:
    preferred = [10, 100, 1000, 5000]
    preferred_hits = [tick for tick in preferred if tick in n_values]
    if 3 <= len(preferred_hits) <= max_ticks:
        return preferred_hits
    if len(n_values) <= max_ticks:
        return n_values
    idxs = {round(i * (len(n_values) - 1) / (max_ticks - 1)) for i in range(max_ticks)}
    return [n_values[idx] for idx in sorted(idxs)]


def _format_axis(
    ax,
    *,
    xticks: list[int],
    log_x: bool = False,
    log_y: bool = False,
    integer_y: bool = False,
    ratio_y: bool = False,
) -> None:
    ax.set_facecolor(THEME["panel"])
    ax.spines["left"].set_color(THEME["border"])
    ax.spines["bottom"].set_color(THEME["border"])
    ax.tick_params(axis="both", colors=THEME["ink"], length=4, width=0.8)
    ax.grid(True, which="major", axis="both", linewidth=0.8, color=THEME["grid"])
    ax.grid(True, which="minor", axis="y", linewidth=0.55, color=THEME["grid_minor"])
    ax.set_xticks(xticks)
    ax.margins(x=0.05)

    if log_x:
        ax.set_xscale("log")
        ax.xaxis.set_major_formatter(FuncFormatter(_format_n_tick))
        ax.xaxis.set_minor_formatter(NullFormatter())

    if log_y:
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(LogLocator(base=10))
        ax.yaxis.set_major_formatter(LogFormatterMathtext())
        ax.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5)))
        ax.yaxis.set_minor_formatter(NullFormatter())
    elif ratio_y:
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(LogLocator(base=10))
        ax.yaxis.set_major_formatter(FuncFormatter(_format_ratio_tick))
        ax.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 5)))
        ax.yaxis.set_minor_formatter(NullFormatter())
    else:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6, integer=integer_y))


def _format_ratio_tick(value: float, _position: int) -> str:
    if value >= 10:
        return f"{value:.0f}x"
    if value >= 1:
        return f"{value:g}x"
    return f"{value:.2g}x"


def _format_n_tick(value: float, _position: int) -> str:
    if value < 1:
        return ""
    rounded = round(value)
    if abs(value - rounded) > 1e-6:
        return ""
    return str(int(rounded))


def _language_handles(*, include_band: bool = False) -> list[Line2D | Patch]:
    handles: list[Line2D | Patch] = []
    for language in DEFAULT_LANGUAGES:
        style = LANG_STYLE[language]
        handles.append(
            Line2D(
                [0],
                [0],
                color=style["color"],
                marker=style["marker"],
                markersize=6,
                markeredgecolor="white",
                markeredgewidth=0.9,
                linewidth=2.2,
                label=style["label"],
            )
        )
    if include_band:
        handles.append(Patch(facecolor=LANG_STYLE["c"]["color"], alpha=0.12, label="Min-max band"))
    return handles


def _scenario_handles(style_map: dict[str, dict[str, str]]) -> list[Line2D]:
    handles: list[Line2D] = []
    for key, style in style_map.items():
        handles.append(
            Line2D(
                [0],
                [0],
                color=style["color"],
                linestyle=style["linestyle"],
                marker=style["marker"],
                markersize=5,
                linewidth=2.1,
                label=style["label"],
            )
        )
    return handles


def _row_color_handles(style_map: dict[str, dict[str, str]], color: str) -> list[Line2D]:
    handles: list[Line2D] = []
    for style in style_map.values():
        handles.append(
            Line2D(
                [0],
                [0],
                color=color,
                linestyle=style["linestyle"],
                marker=style["marker"],
                markersize=5,
                linewidth=2.1,
                label=style["label"],
            )
        )
    return handles


def _plot_time_series(
    ax,
    group: pd.DataFrame,
    *,
    style: dict[str, str],
    band_alpha: float = 0.1,
    linewidth: float = 2.2,
    markersize: float = 5.7,
) -> None:
    ordered = group.sort_values("N")
    ax.fill_between(
        ordered["N"],
        ordered["min_seconds"],
        ordered["max_seconds"],
        color=style["color"],
        alpha=band_alpha,
        zorder=1,
    )
    ax.plot(
        ordered["N"],
        ordered["median_seconds"],
        color=style["color"],
        marker=style["marker"],
        markersize=markersize,
        markeredgecolor="white",
        markeredgewidth=0.9,
        linewidth=linewidth,
        solid_capstyle="round",
        zorder=2,
    )


def _plot_comparison_series(ax, group: pd.DataFrame, *, style: dict[str, str]) -> None:
    ordered = group.sort_values("N")
    ax.plot(
        ordered["N"],
        ordered["median_comparisons"],
        color=style["color"],
        linestyle=style["linestyle"],
        marker=style["marker"],
        markersize=5,
        linewidth=2.2,
        markeredgecolor="white",
        markeredgewidth=0.85,
        solid_capstyle="round",
    )


def _plot_relative_series(ax, group: pd.DataFrame, *, color: str, style: dict[str, str]) -> None:
    ordered = group.sort_values("N")
    ax.plot(
        ordered["N"],
        ordered["relative_to_c"],
        color=color,
        linestyle=style["linestyle"],
        marker=style["marker"],
        markersize=5,
        linewidth=2.2,
        markeredgecolor="white",
        markeredgewidth=0.85,
        solid_capstyle="round",
    )


def _annotate_panel(ax, text: str) -> None:
    ax.text(
        0.03,
        0.97,
        text,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.7,
        color=THEME["muted"],
        bbox={"boxstyle": "round,pad=0.28", "facecolor": "white", "edgecolor": "none", "alpha": 0.8},
    )


def _save_figure(fig: plt.Figure, out: Path) -> None:
    fig.savefig(out, dpi=220, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def plot_quicksort(summary: pd.DataFrame, out: Path) -> None:
    sub = summary[summary["algorithm"] == "quicksort"]
    if sub.empty:
        return

    n_values = sorted(int(value) for value in sub["N"].unique().tolist())
    xticks = _select_xticks(n_values)
    fig, axes = plt.subplots(1, 3, figsize=(15.2, 5.7), sharey=True)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.78, bottom=0.16, wspace=0.06)

    for idx, (ax, distribution) in enumerate(zip(axes, QUICKSORT_DISTRIBUTIONS)):
        dist_df = sub[sub["distribution"] == distribution]
        for language in DEFAULT_LANGUAGES:
            group = dist_df[dist_df["language"] == language]
            if group.empty:
                continue
            _plot_time_series(ax, group, style=LANG_STYLE[language], band_alpha=0.1)
        _format_axis(ax, xticks=xticks, log_x=True, log_y=True)
        ax.set_title(DIST_LABELS[distribution], color=THEME["ink"], fontsize=14.5, pad=9)
        ax.set_xlabel("Input size N")
        if idx == 0:
            ax.set_ylabel("Median seconds per run")

    _annotate_panel(axes[0], "Median line with min-max spread")
    fig.suptitle("Quick sort timing", fontsize=19, color=THEME["ink"], y=0.96)
    fig.text(
        0.5,
        0.90,
        "Cross-language median in-process timing across random and structured inputs",
        ha="center",
        fontsize=11,
        color=THEME["muted"],
    )
    fig.legend(
        handles=_language_handles(include_band=True),
        loc="upper center",
        ncol=4,
        bbox_to_anchor=(0.5, 0.86),
        fontsize=10,
        columnspacing=1.4,
        handlelength=2.4,
    )
    fig.text(
        0.5,
        0.055,
        "Input size and timing axes use logarithmic scaling. Timings exclude process startup, input loading, and binary-search presorting.",
        ha="center",
        fontsize=9.1,
        color=THEME["muted"],
    )
    _save_figure(fig, out)


def plot_search(summary: pd.DataFrame, algorithm: str, out: Path) -> None:
    sub = summary[(summary["algorithm"] == algorithm) & (summary["distribution"] == "ascending")]
    if sub.empty:
        return

    n_values = sorted(int(value) for value in sub["N"].unique().tolist())
    xticks = _select_xticks(n_values)
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 8.6), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.82, bottom=0.12, wspace=0.08, hspace=0.15)

    for idx, (ax, search_case) in enumerate(zip(axes.flatten(), SEARCH_CASE_LABELS)):
        case_df = sub[sub["search_case"] == search_case]
        for language in DEFAULT_LANGUAGES:
            group = case_df[case_df["language"] == language]
            if group.empty:
                continue
            _plot_time_series(ax, group, style=LANG_STYLE[language], band_alpha=0.1)
        _format_axis(ax, xticks=xticks, log_x=True, log_y=True)
        ax.set_title(SEARCH_CASE_LABELS[search_case], color=THEME["ink"], fontsize=13.5, pad=8)
        if idx >= 2:
            ax.set_xlabel("Input size N")
    axes[0][0].set_ylabel("Median seconds per run")
    axes[1][0].set_ylabel("Median seconds per run")
    _annotate_panel(axes[0][0], "Ascending input only")

    title = f"{ALGORITHM_LABELS[algorithm]} timing"
    fig.suptitle(title, fontsize=18.5, color=THEME["ink"], y=0.965)
    fig.text(
        0.5,
        0.91,
        "Median in-process timing across explicit search cases",
        ha="center",
        fontsize=10.8,
        color=THEME["muted"],
    )
    fig.legend(
        handles=_language_handles(include_band=True),
        loc="upper center",
        ncol=4,
        bbox_to_anchor=(0.5, 0.865),
        fontsize=9.8,
        columnspacing=1.3,
        handlelength=2.4,
    )
    fig.text(
        0.5,
        0.04,
        "Shaded bands show min-max spread across measured trials. Input size and timing axes use logarithmic scaling.",
        ha="center",
        fontsize=9.1,
        color=THEME["muted"],
    )
    _save_figure(fig, out)


def plot_comparisons(summary: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15.4, 5.2))
    fig.subplots_adjust(left=0.07, right=0.99, top=0.80, bottom=0.18, wspace=0.20)

    baseline_language = "c"
    quicksort = summary[(summary["algorithm"] == "quicksort") & (summary["language"] == baseline_language)]
    for distribution in QUICKSORT_DISTRIBUTIONS:
        group = quicksort[quicksort["distribution"] == distribution]
        if group.empty:
            continue
        _plot_comparison_series(axes[0], group, style=DIST_STYLE[distribution])

    for ax, algorithm in zip(axes[1:], SEARCH_ALGORITHMS):
        sub = summary[(summary["algorithm"] == algorithm) & (summary["distribution"] == "ascending")]
        sub = sub[sub["language"] == baseline_language]
        for search_case in SEARCH_CASE_LABELS:
            group = sub[sub["search_case"] == search_case]
            if group.empty:
                continue
            _plot_comparison_series(ax, group, style=SEARCH_STYLE[search_case])

    n_values = sorted(int(value) for value in summary["N"].unique().tolist())
    xticks = _select_xticks(n_values)
    for ax, title in zip(
        axes,
        (
            "Quick sort comparisons",
            "Linear search comparisons",
            "Binary search comparisons",
        ),
    ):
        _format_axis(ax, xticks=xticks, log_x=True, integer_y=True)
        ax.set_title(title, color=THEME["ink"], fontsize=14.2, pad=8)
        ax.set_xlabel("Input size N")
    axes[0].set_ylabel("Median comparisons")
    axes[0].legend(handles=_scenario_handles(DIST_STYLE), title="Distribution", fontsize=9, title_fontsize=9.2)
    axes[1].legend(handles=_scenario_handles(SEARCH_STYLE), title="Search case", fontsize=8.7, title_fontsize=9.0)
    axes[2].legend(handles=_scenario_handles(SEARCH_STYLE), title="Search case", fontsize=8.7, title_fontsize=9.0)
    _annotate_panel(axes[0], "One curve per scenario; all languages overlap exactly")

    fig.suptitle("Comparison-count consistency", fontsize=18.2, color=THEME["ink"], y=0.96)
    fig.text(
        0.5,
        0.905,
        "Hardware-independent work profiles after collapsing coincident C, Java, and Python trajectories",
        ha="center",
        fontsize=10.7,
        color=THEME["muted"],
    )
    fig.text(
        0.5,
        0.05,
        "Because comparison counts match across languages for every published case, a single scenario curve is shown in each panel.",
        ha="center",
        fontsize=9.0,
        color=THEME["muted"],
    )
    _save_figure(fig, out)


def plot_timing_overview(summary: pd.DataFrame, out: Path) -> None:
    n_values = sorted(int(value) for value in summary["N"].unique().tolist())
    xticks = _select_xticks(n_values, max_ticks=4)
    fig, axes = plt.subplots(3, 4, figsize=(16.2, 10.4), sharey="row")
    fig.subplots_adjust(left=0.075, right=0.985, top=0.88, bottom=0.10, wspace=0.16, hspace=0.28)

    quicksort = summary[summary["algorithm"] == "quicksort"]
    for col, distribution in enumerate(QUICKSORT_DISTRIBUTIONS):
        ax = axes[0, col]
        dist_df = quicksort[quicksort["distribution"] == distribution]
        for language in DEFAULT_LANGUAGES:
            group = dist_df[dist_df["language"] == language]
            if group.empty:
                continue
            _plot_time_series(ax, group, style=LANG_STYLE[language], band_alpha=0.08, linewidth=2.0, markersize=4.8)
        _format_axis(ax, xticks=xticks, log_x=True, log_y=True)
        ax.set_title(DIST_LABELS[distribution], fontsize=13.2, color=THEME["ink"], pad=7)
        ax.set_xlabel("Input size N")
    axes[0, 0].set_ylabel("Quick sort\nMedian sec/run")
    axes[0, 3].axis("off")
    axes[0, 3].text(
        0.0,
        0.98,
        "Figure key\nInput size and timing use log scaling.\nSearch rows use ascending inputs only.",
        ha="left",
        va="top",
        fontsize=9.4,
        color=THEME["muted"],
    )
    axes[0, 3].legend(
        handles=_language_handles(include_band=True),
        loc="upper left",
        bbox_to_anchor=(0.0, 0.48),
        fontsize=9.5,
        handlelength=2.4,
        labelspacing=0.8,
    )

    for col, search_case in enumerate(SEARCH_CASE_LABELS):
        ax = axes[1, col]
        case_df = summary[
            (summary["algorithm"] == "linear_search")
            & (summary["distribution"] == "ascending")
            & (summary["search_case"] == search_case)
        ]
        for language in DEFAULT_LANGUAGES:
            group = case_df[case_df["language"] == language]
            if group.empty:
                continue
            _plot_time_series(ax, group, style=LANG_STYLE[language], band_alpha=0.08, linewidth=2.0, markersize=4.6)
        _format_axis(ax, xticks=xticks, log_y=True)
        ax.set_title(SEARCH_CASE_LABELS[search_case], fontsize=12.8, color=THEME["ink"], pad=7)
        ax.set_xlabel("Input size N")
    axes[1, 0].set_ylabel("Linear search\nMedian sec/run")

    for col, search_case in enumerate(SEARCH_CASE_LABELS):
        ax = axes[2, col]
        case_df = summary[
            (summary["algorithm"] == "binary_search")
            & (summary["distribution"] == "ascending")
            & (summary["search_case"] == search_case)
        ]
        for language in DEFAULT_LANGUAGES:
            group = case_df[case_df["language"] == language]
            if group.empty:
                continue
            _plot_time_series(ax, group, style=LANG_STYLE[language], band_alpha=0.08, linewidth=2.0, markersize=4.6)
        _format_axis(ax, xticks=xticks, log_y=True)
        ax.set_title(SEARCH_CASE_LABELS[search_case], fontsize=12.8, color=THEME["ink"], pad=7)
        ax.set_xlabel("Input size N")
    axes[2, 0].set_ylabel("Binary search\nMedian sec/run")

    fig.suptitle("Cross-language timing overview", fontsize=19.5, color=THEME["ink"], y=0.965)
    fig.text(
        0.5,
        0.92,
        "Report-ready panel summary of median in-process timing across algorithms, distributions, and search cases",
        ha="center",
        fontsize=10.9,
        color=THEME["muted"],
    )
    fig.text(
        0.5,
        0.04,
        "Median of 20 measured trials. Shaded bands show min-max spread within each benchmark configuration.",
        ha="center",
        fontsize=9.1,
        color=THEME["muted"],
    )
    _save_figure(fig, out)


def build_relative_to_c(summary: pd.DataFrame) -> pd.DataFrame:
    baseline_cols = ["algorithm", "distribution", "input_id", "N", "search_case", "median_seconds"]
    baseline = summary[summary["language"] == "c"][baseline_cols].rename(columns={"median_seconds": "c_seconds"})
    relative = summary[summary["language"].isin(("java", "python"))].merge(
        baseline,
        on=["algorithm", "distribution", "input_id", "N", "search_case"],
        how="inner",
        validate="many_to_one",
    )
    if len(relative) != len(summary[summary["language"].isin(("java", "python"))]):
        raise SummaryValidationError("could not align all non-C summary rows to the C baseline")
    relative["relative_to_c"] = relative["median_seconds"] / relative["c_seconds"]
    return relative


def plot_timing_speedup_vs_c(summary: pd.DataFrame, out: Path) -> None:
    relative = build_relative_to_c(summary)
    n_values = sorted(int(value) for value in relative["N"].unique().tolist())
    xticks = _select_xticks(n_values)
    fig, axes = plt.subplots(2, 3, figsize=(15.4, 7.8), sharex=True, sharey="row")
    fig.subplots_adjust(left=0.08, right=0.985, top=0.82, bottom=0.14, wspace=0.16, hspace=0.22)

    row_languages = ("java", "python")
    panel_configs = (
        ("quicksort", QUICKSORT_DISTRIBUTIONS, DIST_STYLE, "Distribution"),
        ("linear_search", tuple(SEARCH_CASE_LABELS), SEARCH_STYLE, "Search case"),
        ("binary_search", tuple(SEARCH_CASE_LABELS), SEARCH_STYLE, "Search case"),
    )

    for row_idx, language in enumerate(row_languages):
        row_color = LANG_STYLE[language]["color"]
        for col_idx, (algorithm, scenarios, style_map, legend_title) in enumerate(panel_configs):
            ax = axes[row_idx, col_idx]
            ax.axhline(1.0, color=THEME["baseline"], linewidth=1.05, linestyle=(0, (3, 3)), zorder=1)
            algo_df = relative[relative["language"] == language]
            algo_df = algo_df[algo_df["algorithm"] == algorithm]
            if algorithm == "quicksort":
                for scenario in scenarios:
                    group = algo_df[algo_df["distribution"] == scenario]
                    if group.empty:
                        continue
                    _plot_relative_series(ax, group, color=row_color, style=style_map[scenario])
            else:
                algo_df = algo_df[algo_df["distribution"] == "ascending"]
                for scenario in scenarios:
                    group = algo_df[algo_df["search_case"] == scenario]
                    if group.empty:
                        continue
                    _plot_relative_series(ax, group, color=row_color, style=style_map[scenario])

            _format_axis(ax, xticks=xticks, log_x=True, ratio_y=True)
            ax.set_xlabel("Input size N")
            if row_idx == 0:
                ax.set_title(ALGORITHM_LABELS[algorithm], fontsize=13.6, color=THEME["ink"], pad=8)
            if col_idx == 0:
                ax.set_ylabel(f"{LANG_STYLE[language]['label']} / C\nrelative time")
            legend_handles = _row_color_handles(style_map, row_color)
            ax.legend(handles=legend_handles, title=legend_title, fontsize=8.2, title_fontsize=8.5, loc="upper left")

    fig.suptitle("Relative median time versus C", fontsize=18.8, color=THEME["ink"], y=0.965)
    fig.text(
        0.5,
        0.90,
        "Normalized timing view for publication-style comparison; values above 1.0x indicate slower median time than C",
        ha="center",
        fontsize=10.8,
        color=THEME["muted"],
    )
    fig.text(
        0.5,
        0.05,
        "Ratios use the median in-process timing per benchmark configuration. Search panels are based on ascending inputs only.",
        ha="center",
        fontsize=9.0,
        color=THEME["muted"],
    )
    _save_figure(fig, out)


def run_all(raw_csv: Path, summary_csv: Path, out_dir: Path, *, strict: bool = True) -> None:
    apply_plot_theme()
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
    plot_timing_overview(summary, out_dir / "timing_overview.png")
    plot_timing_speedup_vs_c(summary, out_dir / "timing_speedup_vs_c.png")


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
