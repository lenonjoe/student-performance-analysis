"""
src/grades.py
-------------
Grade calculation logic.

Responsibilities:
  - Assign letter grades based on percentage marks.
  - Calculate per-student average marks.
  - Build a student-level summary DataFrame.
"""

import pandas as pd


# ── Grade Scale ───────────────────────────────────────────────────────────────
GRADE_SCALE = [
    (90, "A+", "Outstanding"),
    (80, "A",  "Excellent"),
    (70, "B",  "Good"),
    (60, "C",  "Average"),
    (50, "D",  "Below Average"),
    (0,  "F",  "Fail"),
]


def assign_grade(pct: float) -> tuple[str, str]:
    """Return (letter_grade, label) for a given percentage."""
    for threshold, grade, label in GRADE_SCALE:
        if pct >= threshold:
            return grade, label
    return "F", "Fail"


def add_grade_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'grade' and 'grade_label' columns to a DataFrame that has 'marks_pct'.
    Works row-by-row.
    """
    df = df.copy()
    results = df["marks_pct"].apply(assign_grade)
    df["grade"]       = results.apply(lambda x: x[0])
    df["grade_label"] = results.apply(lambda x: x[1])
    return df


def build_student_summary(master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate marks across all subjects per student.

    Returns a DataFrame with one row per student containing:
      student_id, name, class, section, gender,
      avg_marks, grade, grade_label, attendance_pct
    """
    # Average marks per student (across all subjects)
    avg_marks = (
        master_df
        .groupby("student_id")["marks_pct"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"marks_pct": "avg_marks"})
    )

    # Student info (take first row per student — info doesn't change)
    student_info = (
        master_df[["student_id", "name", "class", "section", "gender", "attendance_pct"]]
        .drop_duplicates(subset="student_id")
    )

    summary = student_info.merge(avg_marks, on="student_id")

    # Add grade columns
    summary["marks_pct"] = summary["avg_marks"]   # reuse the assign_grade logic
    summary = add_grade_columns(summary)
    summary = summary.drop(columns=["marks_pct"])

    # Sort by avg_marks descending
    summary = summary.sort_values("avg_marks", ascending=False).reset_index(drop=True)
    summary["rank"] = summary.index + 1

    return summary
