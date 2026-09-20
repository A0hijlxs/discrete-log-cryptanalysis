"""Renders benchmarks/results/dlp_benchmarks.csv into two charts:

- runtime_vs_bits.png: all five DLP algorithms' mean solve time vs. bit
  length, log-scale y-axis, overlaid for direct comparison.
- bsgs_memory_vs_bits.png: BSGS peak memory vs. bit length, with the two
  claimed bit-length ceilings (the write-up's 45-bit recommendation and
  bsgs.py's own 50-bit guard) shown as extrapolated points beyond the
  measured range.

Run after bench_dlp.py has produced the CSV.
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from bench_dlp import fit_log2_memory, BSGS_CODE_GUARD_BITS, BSGS_WRITEUP_CLAIMED_SAFE_BITS

RESULTS_DIR = Path(__file__).parent / "results"
CSV_PATH = RESULTS_DIR / "dlp_benchmarks.csv"

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

SERIES_COLORS = {
    "pohlig_hellman": "#2a78d6",
    "enhanced_pohlig_hellman": "#eb6834",
    "index_calculus": "#1baf7a",
    "bsgs": "#eda100",
    "pollard_rho": "#e87ba4",
}
SERIES_LABELS = {
    "pohlig_hellman": "Pohlig-Hellman",
    "enhanced_pohlig_hellman": "Enhanced Pohlig-Hellman",
    "index_calculus": "Index calculus",
    "bsgs": "BSGS",
    "pollard_rho": "Pollard's rho",
}


def load_rows():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(BASELINE)
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    ax.grid(True, which="major", axis="y", color=GRIDLINE, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    ax.title.set_color(INK_PRIMARY)
    ax.xaxis.label.set_color(INK_SECONDARY)
    ax.yaxis.label.set_color(INK_SECONDARY)


def plot_runtime(rows):
    by_series = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["success"] != "True":
            continue
        by_series[row["algorithm"]][int(row["bits"])].append(float(row["time_seconds"]))

    fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
    style_axes(ax)

    for algo in ["pohlig_hellman", "enhanced_pohlig_hellman", "index_calculus", "bsgs", "pollard_rho"]:
        bits_list = sorted(by_series[algo])
        means = [sum(by_series[algo][b]) / len(by_series[algo][b]) for b in bits_list]
        ax.plot(
            bits_list,
            means,
            color=SERIES_COLORS[algo],
            linewidth=2,
            solid_joinstyle="round",
            solid_capstyle="round",
            marker="o",
            markersize=8,
            markerfacecolor=SERIES_COLORS[algo],
            markeredgecolor=SURFACE,
            markeredgewidth=1.5,
            label=SERIES_LABELS[algo],
        )

    ax.set_yscale("log")
    ax.set_xlabel("Subgroup / group order (bits)")
    ax.set_ylabel("Mean solve time (seconds, log scale)")
    ax.set_title("DLP algorithm runtime vs. bit length")
    legend = ax.legend(frameon=False, labelcolor=INK_SECONDARY, fontsize=9, loc="upper left")

    fig.tight_layout()
    out_path = RESULTS_DIR / "runtime_vs_bits.png"
    fig.savefig(out_path, facecolor=SURFACE)
    plt.close(fig)
    return out_path


def plot_bsgs_memory(rows):
    by_bits = defaultdict(list)
    for row in rows:
        if row["algorithm"] != "bsgs" or row["success"] != "True":
            continue
        by_bits[int(row["bits"])].append(float(row["peak_memory_mb"]))

    bits_list = sorted(by_bits)
    means = [sum(by_bits[b]) / len(by_bits[b]) for b in bits_list]
    slope, intercept = fit_log2_memory(bits_list, means)

    extrapolated_bits = [BSGS_WRITEUP_CLAIMED_SAFE_BITS, BSGS_CODE_GUARD_BITS]
    extrapolated_mb = [2 ** (slope * b + intercept) for b in extrapolated_bits]

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)
    style_axes(ax)

    ax.plot(
        bits_list,
        means,
        color=SERIES_COLORS["bsgs"],
        linewidth=2,
        solid_joinstyle="round",
        solid_capstyle="round",
        marker="o",
        markersize=8,
        markerfacecolor=SERIES_COLORS["bsgs"],
        markeredgecolor=SURFACE,
        markeredgewidth=1.5,
        label="Measured",
    )

    fit_bits = list(range(bits_list[0], BSGS_CODE_GUARD_BITS + 1))
    fit_mb = [2 ** (slope * b + intercept) for b in fit_bits]
    ax.plot(fit_bits, fit_mb, color=SERIES_COLORS["bsgs"], linewidth=1.5, linestyle="--", alpha=0.5)

    ax.plot(
        extrapolated_bits,
        extrapolated_mb,
        marker="o",
        markersize=8,
        linestyle="none",
        markerfacecolor=SURFACE,
        markeredgecolor=SERIES_COLORS["bsgs"],
        markeredgewidth=2,
        label="Extrapolated (fitted trend)",
    )

    labels = ["45-bit: write-up's claimed safe ceiling", "50-bit: bsgs.py's own guard"]
    for b, mb, label in zip(extrapolated_bits, extrapolated_mb, labels):
        ax.annotate(
            f"{label}\n~{mb:,.0f} MB",
            xy=(b, mb),
            xytext=(-10, 12),
            textcoords="offset points",
            fontsize=8,
            color=INK_SECONDARY,
            ha="right",
        )

    ax.set_yscale("log")
    ax.set_xlabel("Subgroup order (bits)")
    ax.set_ylabel("Peak memory, MB (log scale)")
    ax.set_title("BSGS peak memory vs. bit length")
    ax.legend(frameon=False, labelcolor=INK_SECONDARY, fontsize=9, loc="upper left")

    fig.tight_layout()
    out_path = RESULTS_DIR / "bsgs_memory_vs_bits.png"
    fig.savefig(out_path, facecolor=SURFACE)
    plt.close(fig)
    return out_path


def main():
    rows = load_rows()
    runtime_path = plot_runtime(rows)
    memory_path = plot_bsgs_memory(rows)
    print(f"Wrote {runtime_path}")
    print(f"Wrote {memory_path}")


if __name__ == "__main__":
    main()
