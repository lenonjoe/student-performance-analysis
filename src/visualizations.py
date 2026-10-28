"""
src/visualizations.py
---------------------
Creates and saves all static charts using matplotlib and seaborn.
Charts are saved to output/charts/ as PNG images.

Charts produced:
  1. Bar chart  — Average marks by subject
  2. Bar chart  — Top 10 students
  3. Heatmap    — Student × Subject marks
  4. Scatter    — Attendance % vs Average Marks
  5. Box plot   — Score distribution by class/section
  6. Pie chart  — Grade distribution
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

# ── Output directory ──────────────────────────────────────────────────────────
CHARTS_DIR = os.path.join("output", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Global Style ──────────────────────────────────────────────────────────────
PALETTE      = "viridis"
BG_COLOR     = "#0f172a"      # dark navy background
CARD_COLOR   = "#1e293b"      # slightly lighter card
TEXT_COLOR   = "#e2e8f0"      # off-white text
ACCENT       = "#6366f1"      # indigo accent
PASS_COLOR   = "#22c55e"      # green
FAIL_COLOR   = "#ef4444"      # red
GRID_COLOR   = "#334155"      # muted grid

def _apply_dark_style(fig, ax_list):
    """Apply consistent dark styling to figure and axes."""
    fig.patch.set_facecolor(BG_COLOR)
    for ax in (ax_list if isinstance(ax_list, (list, np.ndarray)) else [ax_list]):
        ax.set_facecolor(CARD_COLOR)
        ax.tick_params(colors=TEXT_COLOR, labelsize=9)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COLOR)
        ax.grid(color=GRID_COLOR, linestyle="--", linewidth=0.5, alpha=0.6)


def _save(fig, filename: str):
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, bbox_inches="tight", dpi=150, facecolor=BG_COLOR)
    plt.close(fig)
    print(f"  [saved] {path}")
    return path


# ── Chart 1: Subject Averages ─────────────────────────────────────────────────

def plot_subject_averages(subject_avg_df: pd.DataFrame) -> str:
    """Bar chart — Average marks by subject."""
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("cool", len(subject_avg_df))

    bars = ax.bar(subject_avg_df["subject"], subject_avg_df["avg_marks"],
                  color=colors, edgecolor=BG_COLOR, linewidth=0.8)

    # Value labels on bars
    for bar, val in zip(bars, subject_avg_df["avg_marks"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{val:.1f}%", ha="center", va="bottom",
                color=TEXT_COLOR, fontsize=9, fontweight="bold")

    ax.axhline(50, color=FAIL_COLOR, linestyle="--", linewidth=1, alpha=0.8, label="Pass Line (50%)")
    ax.set_title("Average Marks by Subject", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Subject", fontsize=11)
    ax.set_ylabel("Average Marks (%)", fontsize=11)
    ax.set_ylim(0, 110)
    ax.legend(facecolor=CARD_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    _apply_dark_style(fig, ax)
    return _save(fig, "01_subject_averages.png")


# ── Chart 2: Top 10 Students ──────────────────────────────────────────────────

def plot_top_students(top_students_df: pd.DataFrame) -> str:
    """Horizontal bar chart — Top 10 students."""
    df = top_students_df.head(10).iloc[::-1]   # reverse so best is at top

    fig, ax = plt.subplots(figsize=(10, 6))
    colors  = sns.color_palette("magma", len(df))

    bars = ax.barh(df["name"], df["avg_marks"], color=colors, edgecolor=BG_COLOR)

    for bar, val, grade in zip(bars, df["avg_marks"], df["grade"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}% ({grade})", va="center",
                color=TEXT_COLOR, fontsize=9, fontweight="bold")

    ax.axvline(50, color=FAIL_COLOR, linestyle="--", linewidth=1, alpha=0.7)
    ax.set_title("Top 10 Students by Average Marks", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Average Marks (%)", fontsize=11)
    ax.set_xlim(0, 115)

    _apply_dark_style(fig, ax)
    return _save(fig, "02_top_students.png")


# ── Chart 3: Heatmap (Student × Subject) ─────────────────────────────────────

def plot_heatmap(pivot_df: pd.DataFrame) -> str:
    """Heatmap — top 30 students × subjects marks."""
    fig, ax = plt.subplots(figsize=(12, 10))

    sns.heatmap(
        pivot_df,
        annot=True, fmt=".0f", cmap="YlOrRd",
        linewidths=0.4, linecolor=BG_COLOR,
        ax=ax, cbar_kws={"label": "Marks (%)"},
        annot_kws={"size": 7}
    )

    ax.set_title("Student x Subject Marks Heatmap (Top 30)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Subject", fontsize=11)
    ax.set_ylabel("Student Name", fontsize=11)
    ax.tick_params(axis="x", rotation=30)
    ax.tick_params(axis="y", rotation=0)

    _apply_dark_style(fig, ax)
    # Fix colorbar text
    fig.axes[-1].yaxis.label.set_color(TEXT_COLOR)
    fig.axes[-1].tick_params(colors=TEXT_COLOR)

    return _save(fig, "03_heatmap.png")


# ── Chart 4: Attendance vs Marks Scatter ──────────────────────────────────────

def plot_attendance_vs_marks(corr_data: pd.DataFrame, r_value: float) -> str:
    """Scatter plot — attendance % vs average marks with trend line."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Color points by marks: green = pass, red = fail
    colors = [PASS_COLOR if m >= 50 else FAIL_COLOR for m in corr_data["avg_marks"]]
    ax.scatter(corr_data["attendance_pct"], corr_data["avg_marks"],
               c=colors, alpha=0.75, s=60, edgecolors=BG_COLOR, linewidth=0.5)

    # Trend line
    z = np.polyfit(corr_data["attendance_pct"], corr_data["avg_marks"], 1)
    p = np.poly1d(z)
    x_line = np.linspace(corr_data["attendance_pct"].min(),
                          corr_data["attendance_pct"].max(), 100)
    ax.plot(x_line, p(x_line), color=ACCENT, linewidth=2, linestyle="--", label="Trend Line")

    # Reference lines
    ax.axhline(50, color=FAIL_COLOR, linestyle=":", linewidth=1, alpha=0.7, label="Pass Mark (50%)")
    ax.axvline(75, color="#f59e0b", linestyle=":", linewidth=1, alpha=0.7, label="75% Attendance")

    # Correlation annotation
    ax.text(0.05, 0.92, f"Pearson r = {r_value:.3f}",
            transform=ax.transAxes, color=TEXT_COLOR,
            fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=CARD_COLOR, edgecolor=ACCENT))

    # Legend patches
    pass_patch = mpatches.Patch(color=PASS_COLOR, label="Passing (≥50%)")
    fail_patch = mpatches.Patch(color=FAIL_COLOR, label="Failing (<50%)")
    ax.legend(handles=[pass_patch, fail_patch,
                        plt.Line2D([0], [0], color=ACCENT, lw=2, linestyle="--", label="Trend")],
              facecolor=CARD_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    ax.set_title("Attendance vs Average Marks", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Attendance (%)", fontsize=11)
    ax.set_ylabel("Average Marks (%)", fontsize=11)

    _apply_dark_style(fig, ax)
    return _save(fig, "04_attendance_vs_marks.png")


# ── Chart 5: Box Plot (Class/Section Distribution) ───────────────────────────

def plot_class_section_boxplot(master_df: pd.DataFrame) -> str:
    """Box plot — mark distribution by class and section."""
    fig, ax = plt.subplots(figsize=(12, 6))

    master_df = master_df.copy()
    master_df["Class-Section"] = "Class " + master_df["class"].astype(str) + " – " + master_df["section"]

    sns.boxplot(
        data=master_df, x="Class-Section", y="marks_pct",
        hue="Class-Section", palette="cool", linewidth=1.2, ax=ax,
        legend=False,
        flierprops=dict(marker="o", markerfacecolor=ACCENT,
                        markersize=4, linestyle="none")
    )

    ax.axhline(50, color=FAIL_COLOR, linestyle="--", linewidth=1, alpha=0.7, label="Pass Line (50%)")
    ax.set_title("Score Distribution by Class & Section", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Class – Section", fontsize=11)
    ax.set_ylabel("Marks (%)", fontsize=11)
    ax.tick_params(axis="x", rotation=30)
    ax.legend(facecolor=CARD_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    _apply_dark_style(fig, ax)
    return _save(fig, "05_class_section_boxplot.png")


# ── Chart 6: Grade Distribution Pie ──────────────────────────────────────────

def plot_grade_distribution(grade_dist_df: pd.DataFrame) -> str:
    """Pie chart — proportion of students per grade."""
    grade_colors = {
        "A+": "#22c55e", "A": "#4ade80",
        "B": "#60a5fa", "C": "#f59e0b",
        "D": "#fb923c", "F": "#ef4444",
    }
    df  = grade_dist_df[grade_dist_df["count"] > 0]
    clr = [grade_colors.get(g, "#94a3b8") for g in df["grade"]]

    fig, ax = plt.subplots(figsize=(8, 7))
    wedges, texts, autotexts = ax.pie(
        df["count"],
        labels=df["grade"],
        autopct="%1.1f%%",
        colors=clr,
        startangle=140,
        pctdistance=0.75,
        wedgeprops=dict(edgecolor=BG_COLOR, linewidth=1.5),
    )
    for t  in texts:      t.set_color(TEXT_COLOR)
    for at in autotexts:  at.set_color(BG_COLOR); at.set_fontweight("bold")

    ax.set_title("Grade Distribution", fontsize=14, fontweight="bold", pad=20, color=TEXT_COLOR)
    fig.patch.set_facecolor(BG_COLOR)

    return _save(fig, "06_grade_distribution.png")


# ── Run All Charts ────────────────────────────────────────────────────────────

def generate_all_charts(subject_avg_df, top_students_df, pivot_df,
                        corr_result, master_df, grade_dist_df) -> list[str]:
    """Generate and save all 6 charts. Returns list of file paths."""
    print("\n[Charts] Generating charts...")
    paths = []
    paths.append(plot_subject_averages(subject_avg_df))
    paths.append(plot_top_students(top_students_df))
    paths.append(plot_heatmap(pivot_df))
    paths.append(plot_attendance_vs_marks(corr_result["data"], corr_result["correlation"]))
    paths.append(plot_class_section_boxplot(master_df))
    paths.append(plot_grade_distribution(grade_dist_df))
    print(f"  [done] All {len(paths)} charts saved to '{CHARTS_DIR}/'")
    return paths
