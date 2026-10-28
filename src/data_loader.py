"""
src/data_loader.py
------------------
Loads the three CSV files, validates them, and merges them into a single
master DataFrame used throughout the project.
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd


# ── File Paths ────────────────────────────────────────────────────────────────
DATA_DIR        = "data"
STUDENTS_FILE   = os.path.join(DATA_DIR, "students.csv")
MARKS_FILE      = os.path.join(DATA_DIR, "marks.csv")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")


# ── Individual Loaders ────────────────────────────────────────────────────────

def load_students() -> pd.DataFrame:
    """Load students.csv and return a DataFrame."""
    df = pd.read_csv(STUDENTS_FILE)
    df.columns = df.columns.str.strip()          # remove accidental spaces
    return df


def load_marks() -> pd.DataFrame:
    """Load marks.csv and return a DataFrame."""
    df = pd.read_csv(MARKS_FILE)
    df.columns = df.columns.str.strip()
    # Add percentage column for convenience
    df["marks_pct"] = (df["marks_obtained"] / df["max_marks"] * 100).round(2)
    return df


def load_attendance() -> pd.DataFrame:
    """Load attendance.csv and return a DataFrame."""
    df = pd.read_csv(ATTENDANCE_FILE)
    df.columns = df.columns.str.strip()
    return df


# ── Master Merge ──────────────────────────────────────────────────────────────

def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all three CSVs, validate them, and return:
        students_df, marks_df, attendance_df, master_df
    master_df is marks joined with student info and attendance.
    """
    students_df   = load_students()
    marks_df      = load_marks()
    attendance_df = load_attendance()

    # ── Basic Validation ──────────────────────────────────────────────────────
    _validate(students_df,   name="students",   required=["student_id", "name", "class", "section"])
    _validate(marks_df,      name="marks",      required=["student_id", "subject", "marks_obtained"])
    _validate(attendance_df, name="attendance", required=["student_id", "attendance_pct"])

    # ── Merge into master DataFrame ───────────────────────────────────────────
    master_df = (
        marks_df
        .merge(students_df,   on="student_id", how="left")
        .merge(attendance_df[["student_id", "attendance_pct", "days_present", "total_days"]],
               on="student_id", how="left")
    )

    return students_df, marks_df, attendance_df, master_df


# ── Internal Helper ───────────────────────────────────────────────────────────

def _validate(df: pd.DataFrame, name: str, required: list[str]) -> None:
    """Raise an error if required columns are missing or DataFrame is empty."""
    if df.empty:
        raise ValueError(f"[ERROR] '{name}.csv' is empty.")
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"[ERROR] '{name}.csv' is missing columns: {missing}")
    print(f"[OK] Loaded '{name}.csv'  -- {len(df)} rows, {len(df.columns)} columns")
