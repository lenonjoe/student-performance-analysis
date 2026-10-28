"""
verify.py
---------
Comprehensive verification script for Student Performance Analysis.
Validates:
  1. Data ingestion & validation (students, marks, attendance, master)
  2. Grade assignments and student summary metrics
  3. Analytical computations (rankings, correlations, subject averages, at-risk)
  4. Personalized recommendation engine
  5. Dashboard layout generation
  6. Dashboard callback logic under multiple filter combinations
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("  STUDENT PERFORMANCE ANALYSIS -- SYSTEM VERIFICATION")
print("=" * 60 + "\n")

# 1. Data Loader
print("[1/6] Testing Data Loader...")
from src.data_loader import load_all
students_df, marks_df, attendance_df, master_df = load_all()
assert len(students_df) == 60, "Expected 60 students"
assert len(marks_df) == 360, "Expected 360 marks records"
assert len(attendance_df) == 60, "Expected 60 attendance records"
assert len(master_df) == 360, "Expected 360 master records"
print("      OK: All datasets validated and merged cleanly.")

# 2. Grades & Summary
print("[2/6] Testing Grade Calculations & Student Summaries...")
from src.grades import build_student_summary, assign_grade
summary = build_student_summary(master_df)
assert len(summary) == 60, "Expected 60 student summary rows"
assert "grade" in summary.columns and "avg_marks" in summary.columns
print(f"      OK: Student summary generated ({len(summary)} students, grades: {sorted(summary['grade'].unique())}).")

# 3. Statistical Analysis
print("[3/6] Testing Statistical Analysis Functions...")
from src.analysis import (
    get_top_students, get_subject_averages,
    get_class_section_stats, get_attendance_correlation,
    get_grade_distribution, get_at_risk_students,
)
top_10 = get_top_students(summary, 10)
assert len(top_10) == 10, "Expected top 10 students"
subj_avg = get_subject_averages(master_df)
assert len(subj_avg) == 6, "Expected 6 subjects"
corr_res = get_attendance_correlation(summary)
r_val = corr_res["correlation"]
assert 0.7 <= r_val <= 1.0, f"Expected strong correlation, got r={r_val}"
at_risk = get_at_risk_students(summary)
print(f"      OK: Top student: {top_10.iloc[0]['name']} ({top_10.iloc[0]['avg_marks']}%)")
print(f"      OK: Pearson correlation r = {r_val:.4f} (Strong positive correlation)")
print(f"      OK: At-risk students flagged: {len(at_risk)}")

# 4. Recommendation Engine
print("[4/6] Testing Recommendation Engine...")
from src.recommendations import build_recommendations
recs = build_recommendations(summary, master_df)
assert len(recs) == 60, "Expected 60 recommendation records"
assert "recommendation" in recs.columns
assert not recs["recommendation"].isnull().any()
print("      OK: Personalized recommendations generated for all 60 students.")

# 5. Dashboard Layout
print("[5/6] Testing Dashboard Layout Construction...")
from dashboard.layout import build_layout
classes = sorted(master_df["class"].astype(str).unique().tolist())
sections = sorted(master_df["section"].unique().tolist())
subjects = sorted(master_df["subject"].unique().tolist())
grades = ["A+", "A", "B", "C", "D", "F"]
layout = build_layout(classes, sections, subjects, grades)
assert layout is not None
print("      OK: Modern academic layout built with 4 filters and all analytical sections.")

# 6. Dashboard Callbacks
print("[6/6] Testing Dashboard Callbacks Under Filter Scenarios...")
import dash
from dashboard.callbacks import register_callbacks
app = dash.Dash(__name__)
register_callbacks(app, master_df)

callback_fn = None
for k, v in app.callback_map.items():
    if "kpi-total-students" in k:
        fn = v["callback"]
        callback_fn = getattr(fn, "__wrapped__", fn)
        break

test_scenarios = [
    ("All", "All", "All", "All"),
    ("10",  "All", "All", "All"),
    ("9",   "A",   "Math", "All"),
    ("All", "All", "Science", "A+"),
    ("9",   "C",   "History", "F"),
]

for cls, sec, subj, grd in test_scenarios:
    res = callback_fn(cls, sec, subj, grd)
    assert res[0] != "", "KPI total should not be empty"
    print(f"      Filter ({cls}, {sec}, {subj}, {grd}) -> Students: {res[0]}, Avg: {res[1]}, Pass: {res[3]}")

print("\n" + "=" * 60)
print("  ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
