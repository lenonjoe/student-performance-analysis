# -*- coding: utf-8 -*-
"""
generate_data.py
----------------
Generates realistic sample CSV data for the Student Performance Analysis project.
Produces three files:
  - data/students.csv
  - data/marks.csv
  - data/attendance.csv
"""

import csv
import random
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from faker import Faker

# ── Configuration ────────────────────────────────────────────────────────────
fake = Faker()
random.seed(42)

NUM_STUDENTS = 60
CLASSES      = ["9", "10"]
SECTIONS     = ["A", "B", "C"]
SUBJECTS     = ["Math", "Science", "English", "History", "Geography", "Computer"]
TOTAL_DAYS   = 200

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Helper: generate marks with realistic distribution ────────────────────────
def generate_mark(base_ability: float) -> int:
    """Return marks (0–100) influenced by the student's base ability."""
    raw = random.gauss(base_ability, 12)          # bell-curve around ability
    return max(0, min(100, round(raw)))


# ── 1. Generate students.csv ─────────────────────────────────────────────────
students = []
for i in range(1, NUM_STUDENTS + 1):
    student_id = f"S{i:03d}"
    name       = fake.name()
    cls        = random.choice(CLASSES)
    section    = random.choice(SECTIONS)
    gender     = random.choice(["Male", "Female"])
    ability    = random.uniform(45, 98)   # hidden base ability (45–98%)

    students.append({
        "student_id": student_id,
        "name":       name,
        "class":      cls,
        "section":    section,
        "gender":     gender,
        "_ability":   ability,            # used internally, not written to CSV
    })

students_file = os.path.join(OUTPUT_DIR, "students.csv")
with open(students_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["student_id", "name", "class", "section", "gender"])
    writer.writeheader()
    for s in students:
        writer.writerow({k: v for k, v in s.items() if not k.startswith("_")})

print(f"[OK] Created {students_file}  ({len(students)} students)")


# ── 2. Generate marks.csv ────────────────────────────────────────────────────
marks_file = os.path.join(OUTPUT_DIR, "marks.csv")
with open(marks_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["student_id", "subject", "marks_obtained", "max_marks"])
    writer.writeheader()
    for s in students:
        for subject in SUBJECTS:
            # Each subject gets a slight random offset from base ability
            subject_offset = random.uniform(-10, 10)
            mark = generate_mark(s["_ability"] + subject_offset)
            writer.writerow({
                "student_id":     s["student_id"],
                "subject":        subject,
                "marks_obtained": mark,
                "max_marks":      100,
            })

print(f"[OK] Created {marks_file}  ({NUM_STUDENTS * len(SUBJECTS)} records)")


# ── 3. Generate attendance.csv ───────────────────────────────────────────────
attendance_file = os.path.join(OUTPUT_DIR, "attendance.csv")
with open(attendance_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["student_id", "total_days", "days_present", "attendance_pct"],
    )
    writer.writeheader()
    for s in students:
        # Higher ability students tend to attend more (loose correlation)
        att_mean    = 60 + (s["_ability"] - 45) * 0.7   # maps ability→attendance
        att_mean    = max(40, min(100, att_mean))
        days_present = round(random.gauss(att_mean / 100 * TOTAL_DAYS, 10))
        days_present = max(0, min(TOTAL_DAYS, days_present))
        att_pct      = round(days_present / TOTAL_DAYS * 100, 2)
        writer.writerow({
            "student_id":    s["student_id"],
            "total_days":    TOTAL_DAYS,
            "days_present":  days_present,
            "attendance_pct": att_pct,
        })

print(f"[OK] Created {attendance_file}  ({NUM_STUDENTS} records)")
print("\nSample data generation complete! Check the 'data/' folder.")
