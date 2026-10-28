"""
src/analysis.py
---------------
Core analysis functions used by both main.py and the dashboard.

Functions:
  - get_top_students()        : Top N students by average marks
  - get_subject_averages()    : Average mark per subject
  - get_class_section_stats() : Per class/section statistics
  - get_attendance_correlation(): Pearson correlation between attendance & marks
  - get_grade_distribution()  : Count of students per grade
  - get_subject_wise_marks()  : Pivot table (student × subject)
"""

import pandas as pd
import numpy as np


# ── Top Students ──────────────────────────────────────────────────────────────

def get_top_students(student_summary: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Return top N students sorted by average marks (highest first).
    student_summary must have 'avg_marks' column (from grades.build_student_summary).
    """
    top = student_summary.nlargest(n, "avg_marks").copy()
    return top[["rank", "name", "class", "section", "avg_marks", "grade", "attendance_pct"]]


# ── Subject Averages ──────────────────────────────────────────────────────────

def get_subject_averages(master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return average marks per subject, sorted highest first.
    Includes the top-scoring student for each subject.
    """
    subj_avg = (
        master_df
        .groupby("subject")["marks_pct"]
        .agg(avg_marks="mean", max_marks="max", min_marks="min", std_dev="std")
        .round(2)
        .reset_index()
        .sort_values("avg_marks", ascending=False)
        .reset_index(drop=True)
    )
    return subj_avg


# ── Class & Section Statistics ────────────────────────────────────────────────

def get_class_section_stats(master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return average marks grouped by class and section.
    Useful for comparing performance across sections.
    """
    stats = (
        master_df
        .groupby(["class", "section"])["marks_pct"]
        .agg(avg_marks="mean", num_records="count")
        .round(2)
        .reset_index()
    )
    # Approximate number of students per section
    student_count = (
        master_df[["student_id", "class", "section"]]
        .drop_duplicates()
        .groupby(["class", "section"])
        .size()
        .reset_index(name="num_students")
    )
    stats = stats.merge(student_count, on=["class", "section"])
    stats = stats.sort_values(["class", "avg_marks"], ascending=[True, False])
    return stats[["class", "section", "num_students", "avg_marks"]]


# ── Attendance vs Marks Correlation ──────────────────────────────────────────

def get_attendance_correlation(student_summary: pd.DataFrame) -> dict:
    """
    Calculate Pearson correlation coefficient between attendance_pct and avg_marks.
    Returns a dict with:
      - 'correlation': float (r value)
      - 'interpretation': str
      - 'data': DataFrame with attendance_pct and avg_marks columns
    """
    data = student_summary[["name", "attendance_pct", "avg_marks"]].dropna()
    r = data["attendance_pct"].corr(data["avg_marks"])
    r = round(r, 4)

    if r >= 0.7:
        interpretation = "Strong positive correlation — higher attendance leads to better marks."
    elif r >= 0.4:
        interpretation = "Moderate positive correlation — attendance has a notable effect on marks."
    elif r >= 0.1:
        interpretation = "Weak positive correlation — some relationship between attendance and marks."
    elif r >= -0.1:
        interpretation = "No significant correlation between attendance and marks."
    else:
        interpretation = "Negative correlation — unusual pattern detected."

    return {"correlation": r, "interpretation": interpretation, "data": data}


# ── Grade Distribution ────────────────────────────────────────────────────────

def get_grade_distribution(student_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Count how many students received each grade.
    Grade order: A+, A, B, C, D, F
    """
    grade_order = ["A+", "A", "B", "C", "D", "F"]
    dist = (
        student_summary["grade"]
        .value_counts()
        .reindex(grade_order, fill_value=0)
        .reset_index()
    )
    dist.columns = ["grade", "count"]
    dist["percentage"] = (dist["count"] / dist["count"].sum() * 100).round(1)
    return dist


# ── Subject-Wise Marks Pivot ──────────────────────────────────────────────────

def get_subject_pivot(master_df: pd.DataFrame, max_students: int = 30) -> pd.DataFrame:
    """
    Build a pivot table: rows = students, columns = subjects, values = marks_pct.
    Limits to max_students rows to keep the heatmap readable.
    """
    pivot = master_df.pivot_table(
        index="name",
        columns="subject",
        values="marks_pct",
        aggfunc="mean"
    ).round(1)

    # Select top max_students by row average for a cleaner heatmap
    pivot["_avg"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("_avg", ascending=False).head(max_students)
    pivot = pivot.drop(columns=["_avg"])
    return pivot


# ── At-Risk Students (low marks or low attendance) ────────────────────────────

def get_at_risk_students(student_summary: pd.DataFrame,
                          marks_threshold: float = 50.0,
                          attendance_threshold: float = 60.0) -> pd.DataFrame:
    """
    Return students who are failing (avg_marks < marks_threshold)
    OR have poor attendance (attendance_pct < attendance_threshold).
    """
    at_risk = student_summary[
        (student_summary["avg_marks"] < marks_threshold) |
        (student_summary["attendance_pct"] < attendance_threshold)
    ].copy()
    return at_risk[["name", "class", "section", "avg_marks", "grade", "attendance_pct"]]
