# 📊 Student Performance Analysis

A modern academic analytics platform and data analysis project built with Python, Pandas, Dash, and Plotly.
Engineered for college presentations — clean, professional, responsive, and fully documented.

---

## ✨ Features & Dashboard Overview

| Section | Capabilities & Visualizations |
|---------|--------------------------------|
| **🏛️ Header** | Clean title, project description, academic session pills, and presentation mode badges |
| **⚡ Filter Toolbar** | Dynamic multidimensional filters: **Class**, **Section**, **Subject**, and **Grade** + **↺ Reset Filters** |
| **📌 Executive KPIs** | 4 primary metric cards: **Total Students**, **Average Marks**, **Average Attendance**, and **Pass Percentage** |
| **🧠 Automated Insights** | Algorithmic findings: Key dataset statistics, weak subject detection, top-performing cohorts, and actionable institutional advice |
| **📚 Academic Performance** | Subject-wise average marks with 50% pass benchmark, grade distribution donut chart, and **Top 10 Students Leaderboard** |
| **📈 Attendance Analysis** | Attendance vs Marks scatter plot with linear regression trendline, attendance category tier breakdown (High ≥85%, Moderate 75–85%, Low <75%), and Pearson correlation verdict card |
| **🏫 Cohort Comparisons** | Side-by-side **Class-wise performance** (Class 9 vs 10) and **Section-wise performance** (Sections A, B, C) |
| **💡 Student Advisory** | Comprehensive, searchable, sortable data table with individual student recommendations and risk flagging |

---

## 📁 Project Architecture

```
Student-Performance-Analysis/
│
├── data/                        # Real/simulated academic CSV files
│   ├── students.csv             # Student ID, name, class, section, gender
│   ├── marks.csv                # Subject-wise marks obtained per student
│   └── attendance.csv           # Attendance percentage & day counts
│
├── src/                         # Reusable core analytical modules
│   ├── __init__.py
│   ├── data_loader.py           # Ingestion, validation, and master dataset merging
│   ├── grades.py                # Grade assignment (A+, A, B, C, D, F) & summaries
│   ├── analysis.py              # Statistical aggregations, correlations, distributions
│   ├── recommendations.py       # Rule-based student recommendation engine
│   └── visualizations.py        # Static matplotlib/seaborn export pipeline
│
├── dashboard/                   # Interactive Dash web application
│   ├── __init__.py
│   ├── app.py                   # Dashboard entry point
│   ├── layout.py                # Modern academic layout & component hierarchy
│   ├── callbacks.py             # Filter callbacks, automated insights, charts
│   └── assets/
│       └── style.css            # Dark theme, typography & dropdown styling
│
├── output/
│   ├── charts/                  # Exported static publication-ready charts (PNG)
│   └── reports/                 # Exported tabular summaries & text reports (CSV & TXT)
│
├── generate_data.py             # Reproducible dataset generator (60 students, 6 subjects)
├── main.py                      # CLI analytical runner, chart export & report generation
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10 or newer (tested on Python 3.10+)
- `pip` package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt --prefer-binary
```

---

## 🚀 How to Run the Project

### Step 1: Generate Dataset (Initial Run)
```bash
python generate_data.py
```
*Generates `students.csv`, `marks.csv`, and `attendance.csv` inside the `data/` directory.*

### Step 2: Launch the Interactive Dashboard (Recommended)
```bash
python dashboard/app.py
```
Open your web browser and navigate to:
👉 **`http://127.0.0.1:8050`**

### Step 3: Run the CLI Analysis Report (Optional)
```bash
python main.py
```
*Prints a comprehensive formatted academic report to your terminal, saves 6 high-resolution static charts to `output/charts/`, and exports structured analytical CSV & text reports to `output/reports/`.*

---

## 🎓 Grading & Evaluation Scale

| Score Range | Grade | Classification |
|-------------|:-----:|----------------|
| **90% – 100%** | **A+** | Outstanding |
| **80% – 89%**  | **A**  | Excellent |
| **70% – 79%**  | **B**  | Good |
| **60% – 69%**  | **C**  | Average |
| **50% – 59%**  | **D**  | Below Average / Passing |
| **< 50%**      | **F**  | At-Risk / Failing |

---

## 📊 Key Findings from Dataset

- **Overall Cohort Size:** 60 enrolled students across Classes 9 & 10 (Sections A, B, C).
- **Academic Average:** **68.8%** with an **86.7%** overall pass rate.
- **Attendance Impact:** Pearson correlation coefficient **r = 0.81** indicates a statistically strong positive link between attendance and examination performance.
- **Attendance Tiers:**
  - High Attendance (≥85%): **84.4%** average mark
  - Moderate Attendance (75–85%): **72.4%** average mark
  - Low Attendance (<75%): **57.8%** average mark
- **Curricular Insight:** English and History lead overall performance (~70%), while Science and Geography represent focus subjects requiring additional pedagogical support.
