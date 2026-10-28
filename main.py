"""
main.py
--------
Command-line runner for the Student Performance Analysis project.

Runs the full analysis pipeline and prints a formatted report to the terminal.
Also saves all 6 static charts to output/charts/.

Usage:
    python main.py
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Imports
from src.data_loader      import load_all
from src.grades           import build_student_summary
from src.analysis         import (
    get_top_students, get_subject_averages,
    get_class_section_stats, get_attendance_correlation,
    get_grade_distribution, get_subject_pivot, get_at_risk_students,
)
from src.recommendations  import build_recommendations
from src.visualizations   import generate_all_charts


def print_section(title: str) -> None:
    """Print a styled section header."""
    width = 65
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def main():
    print("\n" + "#" * 65)
    print("   STUDENT PERFORMANCE ANALYSIS  --  Full Report")
    print("#" * 65)

    # Load data
    print("\nLoading data...")
    students_df, marks_df, attendance_df, master_df = load_all()

    # Build student summary
    summary = build_student_summary(master_df)

    # -------------------------------------------------------------------------
    # 1. OVERVIEW
    # -------------------------------------------------------------------------
    print_section("1. OVERVIEW")
    print(f"  Total Students   : {len(summary)}")
    print(f"  Subjects Covered : {', '.join(master_df['subject'].unique())}")
    print(f"  Classes          : {', '.join(sorted(master_df['class'].astype(str).unique()))}")
    print(f"  Overall Average  : {summary['avg_marks'].mean():.2f}%")
    pass_rate = (summary["avg_marks"] >= 50).mean() * 100
    print(f"  Pass Rate        : {pass_rate:.1f}%")

    # -------------------------------------------------------------------------
    # 2. TOP PERFORMERS
    # -------------------------------------------------------------------------
    print_section("2. TOP 10 STUDENTS")
    top = get_top_students(summary, n=10)
    print(f"  {'Rank':<5} {'Name':<22} {'Class':<7} {'Sec':<5} {'Avg Marks':<12} {'Grade':<6} {'Attendance'}")
    print(f"  {'-'*4} {'-'*21} {'-'*6} {'-'*4} {'-'*11} {'-'*5} {'-'*10}")
    for _, row in top.iterrows():
        print(f"  {int(row['rank']):<5} {row['name']:<22} {row['class']:<7} "
              f"{row['section']:<5} {row['avg_marks']:<12.1f} {row['grade']:<6} "
              f"{row['attendance_pct']:.1f}%")

    # -------------------------------------------------------------------------
    # 3. SUBJECT AVERAGES
    # -------------------------------------------------------------------------
    print_section("3. SUBJECT AVERAGES (Ranked)")
    subj = get_subject_averages(master_df)
    print(f"  {'Rank':<5} {'Subject':<14} {'Avg Marks':<12} {'Max':<8} {'Min':<8} {'Std Dev'}")
    print(f"  {'-'*4} {'-'*13} {'-'*11} {'-'*7} {'-'*7} {'-'*7}")
    for i, (_, row) in enumerate(subj.iterrows(), 1):
        print(f"  {i:<5} {row['subject']:<14} {row['avg_marks']:<12.1f} "
              f"{row['max_marks']:<8.1f} {row['min_marks']:<8.1f} {row['std_dev']:.1f}")

    # -------------------------------------------------------------------------
    # 4. CLASS & SECTION COMPARISON
    # -------------------------------------------------------------------------
    print_section("4. CLASS & SECTION COMPARISON")
    class_stats = get_class_section_stats(master_df)
    print(f"  {'Class':<7} {'Section':<9} {'Students':<11} {'Avg Marks'}")
    print(f"  {'-'*6} {'-'*8} {'-'*10} {'-'*9}")
    for _, row in class_stats.iterrows():
        print(f"  {row['class']:<7} {row['section']:<9} {int(row['num_students']):<11} {row['avg_marks']:.2f}%")

    # -------------------------------------------------------------------------
    # 5. ATTENDANCE CORRELATION
    # -------------------------------------------------------------------------
    print_section("5. ATTENDANCE vs MARKS CORRELATION")
    corr = get_attendance_correlation(summary)
    print(f"  Pearson r = {corr['correlation']:.4f}")
    print(f"  {corr['interpretation']}")

    # -------------------------------------------------------------------------
    # 6. GRADE DISTRIBUTION
    # -------------------------------------------------------------------------
    print_section("6. GRADE DISTRIBUTION")
    grade_dist = get_grade_distribution(summary)
    for _, row in grade_dist.iterrows():
        bar = "|" * int(row["percentage"] / 2)
        print(f"  {row['grade']:<4} {bar:<25} {int(row['count'])} students ({row['percentage']}%)")

    # -------------------------------------------------------------------------
    # 7. AT-RISK STUDENTS
    # -------------------------------------------------------------------------
    print_section("7. AT-RISK STUDENTS (marks < 50% OR attendance < 60%)")
    at_risk = get_at_risk_students(summary)
    if at_risk.empty:
        print("  [OK] No at-risk students found.")
    else:
        print(f"  {'Name':<22} {'Class':<7} {'Sec':<5} {'Avg Marks':<12} {'Grade':<6} {'Attendance'}")
        print(f"  {'-'*21} {'-'*6} {'-'*4} {'-'*11} {'-'*5} {'-'*10}")
        for _, row in at_risk.iterrows():
            print(f"  {row['name']:<22} {row['class']:<7} {row['section']:<5} "
                  f"{row['avg_marks']:<12.1f} {row['grade']:<6} {row['attendance_pct']:.1f}%")

    # -------------------------------------------------------------------------
    # 8. SAMPLE RECOMMENDATIONS (first 5)
    # -------------------------------------------------------------------------
    print_section("8. SAMPLE RECOMMENDATIONS (first 5 students)")
    recs = build_recommendations(summary, master_df).head(5)
    for _, row in recs.iterrows():
        print(f"\n  [Student] {row['name']} (Class {row['class']}-{row['section']}, Grade {row['grade']})")
        print(f"     {row['recommendation']}")

    # -------------------------------------------------------------------------
    # 9. GENERATE STATIC CHARTS
    # -------------------------------------------------------------------------
    print_section("9. GENERATING STATIC CHARTS")
    pivot = get_subject_pivot(master_df)
    top10 = get_top_students(summary, n=10)
    generate_all_charts(
        subject_avg_df  = get_subject_averages(master_df),
        top_students_df = top10,
        pivot_df        = pivot,
        corr_result     = corr,
        master_df       = master_df,
        grade_dist_df   = grade_dist,
    )

    # -------------------------------------------------------------------------
    # 10. SAVE TABULAR REPORTS TO output/reports/
    # -------------------------------------------------------------------------
    print_section("10. EXPORTING ANALYTICAL REPORTS")
    reports_dir = os.path.join("output", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Complete Student Summary with recommendations
    all_recs = build_recommendations(summary, master_df)
    full_student_report = summary.merge(
        all_recs[["student_id", "recommendation"]], on="student_id"
    )
    summary_csv = os.path.join(reports_dir, "student_summary.csv")
    full_student_report.to_csv(summary_csv, index=False)
    print(f"  [saved] {summary_csv}")

    # 2. Subject Analysis CSV
    subj_csv = os.path.join(reports_dir, "subject_analysis.csv")
    subj.to_csv(subj_csv, index=False)
    print(f"  [saved] {subj_csv}")

    # 3. Class-Section Analysis CSV
    class_sec_csv = os.path.join(reports_dir, "class_section_analysis.csv")
    class_stats.to_csv(class_sec_csv, index=False)
    print(f"  [saved] {class_sec_csv}")

    # 4. Text Report Summary
    txt_report = os.path.join(reports_dir, "analysis_report.txt")
    with open(txt_report, "w", encoding="utf-8") as f:
        f.write("STUDENT PERFORMANCE ANALYSIS -- SUMMARY REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Enrolled Students: {len(summary)}\n")
        f.write(f"Overall Cohort Average:   {summary['avg_marks'].mean():.2f}%\n")
        f.write(f"Cohort Pass Rate:         {pass_rate:.1f}%\n")
        f.write(f"Attendance Correlation:   r = {corr['correlation']:.4f} ({corr['interpretation']})\n")
        f.write(f"Top Performer:            {top.iloc[0]['name']} ({top.iloc[0]['avg_marks']}%, Grade {top.iloc[0]['grade']})\n")
        f.write(f"At-Risk Count:            {len(at_risk)} students\n\n")
        f.write("Subject Rankings:\n")
        for i, (_, row) in enumerate(subj.iterrows(), 1):
            f.write(f"  {i}. {row['subject']}: {row['avg_marks']:.1f}% (Max: {row['max_marks']}, Min: {row['min_marks']})\n")
    print(f"  [saved] {txt_report}")

    print("\n" + "#" * 65)
    print("   [DONE] Analysis & Report Generation Complete!")
    print("   Charts saved in:  output/charts/")
    print("   Reports saved in: output/reports/")
    print("   Run dashboard:    python dashboard/app.py")
    print("#" * 65 + "\n")


if __name__ == "__main__":
    main()
