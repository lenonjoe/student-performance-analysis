"""
dashboard/app.py
-----------------
Entry point for the interactive Student Performance Analysis Dashboard.

HOW TO RUN:
    python dashboard/app.py

Then open your browser at:
    http://127.0.0.1:8050

What this file does:
  1. Loads all data from the CSV files (via src/data_loader.py)
  2. Creates the modern academic analytics Dash application
  3. Applies the responsive layout (from dashboard/layout.py)
  4. Registers all callback functions (from dashboard/callbacks.py)
  5. Starts the development server
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dash
import dash_bootstrap_components as dbc

from src.data_loader import load_all
from dashboard.layout import build_layout
from dashboard.callbacks import register_callbacks


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Load all data from CSV files
# ─────────────────────────────────────────────────────────────────────────────
print("\nStarting Student Performance Analysis Dashboard...")
print("Loading data from CSV files...\n")

students_df, marks_df, attendance_df, master_df = load_all()

# Extract unique values for all filter dropdowns
classes  = sorted(master_df["class"].astype(str).unique().tolist())
sections = sorted(master_df["section"].unique().tolist())
subjects = sorted(master_df["subject"].unique().tolist())
grades   = ["A+", "A", "B", "C", "D", "F"]

print(f"\n  Classes:  {classes}")
print(f"  Sections: {sections}")
print(f"  Subjects: {subjects}")
print(f"  Grades:   {grades}\n")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Create the Dash application
# ─────────────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    assets_folder=os.path.join(os.path.dirname(__file__), "assets"),
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
    ],
    title="Student Performance Analysis",
    suppress_callback_exceptions=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Set the layout
# ─────────────────────────────────────────────────────────────────────────────
app.layout = build_layout(classes, sections, subjects, grades)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Register all interactive callbacks
# ─────────────────────────────────────────────────────────────────────────────
register_callbacks(app, master_df)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Start the server
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  Student Performance Analysis Dashboard is LIVE!")
    print("  Access URL: http://127.0.0.1:8050")
    print("  College Presentation Edition")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 55 + "\n")
    app.run(debug=True, host="127.0.0.1", port=8050)
