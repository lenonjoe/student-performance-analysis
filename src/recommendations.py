"""
src/recommendations.py
----------------------
Rule-based recommendation engine.

Generates personalized text advice for each student based on:
  - Average marks
  - Attendance percentage
  - Weakest subject
  - Grade achieved
"""

import pandas as pd


# Thresholds
FAIL_THRESHOLD      = 50.0   # avg_marks below this -> at risk
LOW_ATT_THRESHOLD   = 60.0   # attendance_pct below this -> concern
MERIT_THRESHOLD     = 85.0   # avg_marks above this -> merit recognition
GOOD_ATT_THRESHOLD  = 90.0   # attendance_pct above this -> commended


def _recommend_for_student(row: pd.Series, master_df: pd.DataFrame) -> str:
    """Return a recommendation string for a single student row."""
    tips = []
    sid  = row["student_id"]

    avg_marks  = row["avg_marks"]
    attendance = row["attendance_pct"]
    grade      = row["grade"]

    # Attendance advice
    if attendance < LOW_ATT_THRESHOLD:
        tips.append(
            f"[WARNING] Attendance is critically low ({attendance:.1f}%). "
            "Regular attendance is strongly linked to better performance."
        )
    elif attendance < 75:
        tips.append(
            f"[NOTE] Attendance ({attendance:.1f}%) is below 75%. "
            "Try to attend more classes to avoid missing key concepts."
        )
    elif attendance >= GOOD_ATT_THRESHOLD:
        tips.append(f"[GREAT] Excellent attendance ({attendance:.1f}%)! Keep it up.")

    # Weakest subject advice
    student_marks = master_df[master_df["student_id"] == sid][["subject", "marks_pct"]]
    if not student_marks.empty:
        weakest = student_marks.loc[student_marks["marks_pct"].idxmin()]
        if weakest["marks_pct"] < FAIL_THRESHOLD:
            tips.append(
                f"[FAIL] Failing in {weakest['subject']} ({weakest['marks_pct']:.1f}%). "
                "Seek extra tutoring or practice resources for this subject."
            )
        elif weakest["marks_pct"] < 60:
            tips.append(
                f"[LOW] Struggling in {weakest['subject']} ({weakest['marks_pct']:.1f}%). "
                "Dedicate extra study time to improve this subject."
            )

    # Overall performance advice
    if avg_marks >= MERIT_THRESHOLD:
        tips.append(
            f"[MERIT] Outstanding performance ({avg_marks:.1f}% -- Grade {grade})! "
            "Eligible for merit recognition. Consider advanced coursework or competitions."
        )
    elif avg_marks >= 70:
        tips.append(
            f"[GOOD] Good overall performance ({avg_marks:.1f}% -- Grade {grade}). "
            "Focus on consistency and push towards the A range."
        )
    elif avg_marks >= FAIL_THRESHOLD:
        tips.append(
            f"[AVG] Average performance ({avg_marks:.1f}% -- Grade {grade}). "
            "Create a structured study schedule and seek help when needed."
        )
    else:
        tips.append(
            f"[ALERT] Below passing threshold ({avg_marks:.1f}% -- Grade {grade}). "
            "Immediate intervention recommended. Speak with a teacher or counsellor."
        )

    return " | ".join(tips) if tips else "[OK] Performance is satisfactory. Keep maintaining your standards."


def build_recommendations(student_summary: pd.DataFrame,
                           master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with one row per student containing:
      student_id, name, class, section, avg_marks, grade, attendance_pct, recommendation
    """
    recs = student_summary.copy()
    recs["recommendation"] = recs.apply(
        lambda row: _recommend_for_student(row, master_df), axis=1
    )
    return recs[
        ["student_id", "name", "class", "section",
         "avg_marks", "grade", "attendance_pct", "recommendation"]
    ]
