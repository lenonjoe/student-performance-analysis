"""
dashboard/callbacks.py
-----------------------
Interactive callback logic for the Student Performance Analysis dashboard.

Handles:
  1. Filter updates (Class, Section, Subject, Grade)
  2. Filter Reset button
  3. Dynamic calculation of all 4 KPI cards
  4. Automated Insights generation (Key Findings, Weak Subjects, High Performers, Recommendations)
  5. Interactive Plotly charts:
     - Subject-wise average marks
     - Grade distribution donut chart
     - Top 10 students table
     - Attendance vs Marks scatter plot with linear regression trendline
     - Attendance categories breakdown vs marks
     - Class-wise performance comparison
     - Section-wise performance comparison
  6. Detailed Student Records & Actionable Recommendations data table
"""

import numpy as np
import pandas as pd
from dash import Input, Output, dash_table, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from src.grades import build_student_summary, assign_grade
from src.recommendations import build_recommendations


# ── Shared Dark Theme Tokens for Charts ───────────────────────────────────────
PLOTLY_DARK = "plotly_dark"
TRANSPARENT = "rgba(0,0,0,0)"

PALETTE = {
    "indigo":  "#6366f1",
    "blue":    "#3b82f6",
    "cyan":    "#06b6d4",
    "emerald": "#10b981",
    "amber":   "#f59e0b",
    "rose":    "#ef4444",
    "purple":  "#a855f7",
    "text":    "#f8fafc",
    "muted":   "#94a3b8",
    "border":  "#1e293b",
}

GRADE_COLORS = {
    "A+": "#10b981",  # emerald
    "A":  "#22c55e",  # green
    "B":  "#3b82f6",  # blue
    "C":  "#f59e0b",  # amber
    "D":  "#f97316",  # orange
    "F":  "#ef4444",  # rose/red
}


def _empty_figure(message: str = "No data available for this filter selection") -> go.Figure:
    """Returns a sleek empty figure with a centered explanatory label."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(color=PALETTE["muted"], size=13),
    )
    fig.update_layout(
        template=PLOTLY_DARK,
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        margin=dict(t=20, b=20, l=20, r=20),
    )
    return fig


def register_callbacks(app, master_df: pd.DataFrame):
    """
    Registers all Dash callbacks on the given app instance.
    master_df is preloaded and passed from app.py.
    """

    # ── 1. Reset Filters Callback ─────────────────────────────────────────────
    @app.callback(
        Output("filter-class",   "value"),
        Output("filter-section", "value"),
        Output("filter-subject", "value"),
        Output("filter-grade",   "value"),
        Input("btn-reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_all_filters(n_clicks):
        return "All", "All", "All", "All"

    # ── 2. Primary Dashboard Update Callback ──────────────────────────────────
    @app.callback(
        # 4 KPI Cards
        Output("kpi-total-students",       "children"),
        Output("kpi-avg-marks",            "children"),
        Output("kpi-avg-attendance",       "children"),
        Output("kpi-pass-pct",             "children"),
        # 4 Automated Insights
        Output("insight-key-findings",     "children"),
        Output("insight-weak-subjects",    "children"),
        Output("insight-high-performers",  "children"),
        Output("insight-recommendations",  "children"),
        # Performance Charts
        Output("chart-subject-avg",        "figure"),
        Output("chart-grade-dist",         "figure"),
        Output("container-top-students",   "children"),
        # Attendance Analysis
        Output("card-attendance-correlation", "children"),
        Output("chart-attendance-scatter", "figure"),
        Output("chart-attendance-tiers",   "figure"),
        # Cohort Comparisons
        Output("chart-class-comparison",   "figure"),
        Output("chart-section-comparison", "figure"),
        # Detailed Advisory Table
        Output("container-student-table",  "children"),
        # Inputs (All 4 Filters)
        Input("filter-class",   "value"),
        Input("filter-section", "value"),
        Input("filter-subject", "value"),
        Input("filter-grade",   "value"),
    )
    def update_dashboard(sel_class, sel_section, sel_subject, sel_grade):
        # ── Step A: Filter Dataset ────────────────────────────────────────────
        df = master_df.copy()

        # Class filter
        if sel_class != "All":
            df = df[df["class"].astype(str) == str(sel_class)]

        # Section filter
        if sel_section != "All":
            df = df[df["section"] == sel_section]

        # Subject-specific or multi-subject marks
        # For subject-level marks chart, we keep df filtered by class & section
        subject_marks_df = df.copy()

        if sel_subject != "All":
            df = df[df["subject"] == sel_subject]

        # Calculate student summary from the filtered marks
        if df.empty:
            empty_fig = _empty_figure("No student records match the selected filters.")
            no_data_div = html.Div("No records found.", style={"color": PALETTE["muted"], "padding": "20px", "textAlign": "center"})
            return (
                "0", "N/A", "N/A", "N/A",
                html.Div("No data for selection."),
                html.Div("No data for selection."),
                html.Div("No data for selection."),
                html.Div("No data for selection."),
                empty_fig, empty_fig, no_data_div,
                html.Div(), empty_fig, empty_fig,
                empty_fig, empty_fig, no_data_div
            )

        # Build student-level summary
        student_summary = build_student_summary(df)

        # Grade filter
        if sel_grade != "All":
            student_summary = student_summary[student_summary["grade"] == sel_grade]
            # Also align df to only these students
            matching_ids = student_summary["student_id"].unique()
            df = df[df["student_id"].isin(matching_ids)]
            subject_marks_df = subject_marks_df[subject_marks_df["student_id"].isin(matching_ids)]

        # Check if student_summary is empty after grade filter
        if student_summary.empty:
            empty_fig = _empty_figure("No students found with Grade " + str(sel_grade))
            no_data_div = html.Div("No students with Grade " + str(sel_grade) + " in this selection.",
                                   style={"color": PALETTE["muted"], "padding": "20px", "textAlign": "center"})
            return (
                "0", "N/A", "N/A", "N/A",
                html.Div("No matching students."),
                html.Div("No matching students."),
                html.Div("No matching students."),
                html.Div("No matching students."),
                empty_fig, empty_fig, no_data_div,
                html.Div(), empty_fig, empty_fig,
                empty_fig, empty_fig, no_data_div
            )

        # ── Step B: Calculate 4 Primary KPIs ──────────────────────────────────
        total_students = len(student_summary)
        avg_marks_val  = student_summary["avg_marks"].mean()
        avg_att_val    = student_summary["attendance_pct"].mean()
        passing_count  = (student_summary["avg_marks"] >= 50.0).sum()
        pass_pct_val   = (passing_count / total_students * 100.0) if total_students > 0 else 0.0

        kpi_total = f"{total_students}"
        kpi_marks = f"{avg_marks_val:.1f}%"
        kpi_att   = f"{avg_att_val:.1f}%"
        kpi_pass  = f"{pass_pct_val:.1f}%"

        # ── Step C: Automated Insights Generation ─────────────────────────────
        # 1. Key Findings
        top_student = student_summary.iloc[0]
        top_name    = top_student["name"]
        top_score   = top_student["avg_marks"]
        failing_cnt = total_students - passing_count

        insight_findings = html.Div([
            html.Div("📌 Key Findings", style={"fontWeight": "700", "fontSize": "13px", "color": PALETTE["indigo"], "marginBottom": "6px"}),
            html.P([
                f"Cohort of ", html.Strong(f"{total_students} students"),
                f" holds an average score of ", html.Strong(f"{avg_marks_val:.1f}%"),
                f" with an overall pass rate of ", html.Strong(f"{pass_pct_val:.1f}%"), "."
            ], style={"fontSize": "12px", "margin": "0 0 6px 0", "lineHeight": "1.4"}),
            html.Div([
                f"Top Performer: {top_name} ({top_score:.1f}%)"
            ], style={"fontSize": "11px", "color": PALETTE["muted"]}),
            html.Div([
                f"At-Risk Students (<50%): {failing_cnt} student(s)"
            ], style={"fontSize": "11px", "color": PALETTE["rose"] if failing_cnt > 0 else PALETTE["emerald"]}),
        ])

        # 2. Weak Subjects Detection
        subj_stats = (
            subject_marks_df.groupby("subject")["marks_pct"]
            .agg(avg="mean", fail_count=lambda x: (x < 50.0).sum(), total="count")
            .reset_index()
            .sort_values("avg", ascending=True)
        )
        if not subj_stats.empty:
            weakest_subj = subj_stats.iloc[0]
            w_name = weakest_subj["subject"]
            w_avg  = weakest_subj["avg"]
            w_fail = int(weakest_subj["fail_count"])

            insight_weak = html.Div([
                html.Div("⚠️ Weakest Subject Alert", style={"fontWeight": "700", "fontSize": "13px", "color": PALETTE["rose"], "marginBottom": "6px"}),
                html.P([
                    f"Curricular analysis flags ", html.Strong(f"{w_name}"),
                    f" as the lowest-performing subject with an average of ", html.Strong(f"{w_avg:.1f}%"), "."
                ], style={"fontSize": "12px", "margin": "0 0 6px 0", "lineHeight": "1.4"}),
                html.Div([
                    f"Failing Students in {w_name}: {w_fail} student(s)"
                ], style={"fontSize": "11px", "color": PALETTE["amber"]}),
                html.Div([
                    "Recommendation: Schedule dedicated remedial tutorials."
                ], style={"fontSize": "11px", "color": PALETTE["muted"], "marginTop": "4px"}),
            ])
        else:
            insight_weak = html.Div("No subject data available.")

        # 3. High-Performing Groups
        strongest_subj = subj_stats.iloc[-1] if not subj_stats.empty else None
        s_name = strongest_subj["subject"] if strongest_subj is not None else "N/A"
        s_avg  = strongest_subj["avg"] if strongest_subj is not None else 0.0

        # Best section
        sec_group = student_summary.groupby("section")["avg_marks"].mean()
        best_sec  = sec_group.idxmax() if not sec_group.empty else "N/A"
        best_sec_score = sec_group.max() if not sec_group.empty else 0.0

        distinction_count = (student_summary["grade"].isin(["A+", "A"])).sum()

        insight_high = html.Div([
            html.Div("🌟 High-Performing Groups", style={"fontWeight": "700", "fontSize": "13px", "color": PALETTE["emerald"], "marginBottom": "6px"}),
            html.P([
                f"Top Subject: ", html.Strong(f"{s_name} ({s_avg:.1f}%)"),
                html.Br(),
                f"Leading Section: ", html.Strong(f"Section {best_sec} ({best_sec_score:.1f}%)"),
            ], style={"fontSize": "12px", "margin": "0 0 6px 0", "lineHeight": "1.4"}),
            html.Div([
                f"Distinction Achievers (Grade A/A+): {distinction_count} student(s)"
            ], style={"fontSize": "11px", "color": PALETTE["cyan"]}),
            html.Div([
                "Commendation: Eligible for peer-tutoring leadership."
            ], style={"fontSize": "11px", "color": PALETTE["muted"], "marginTop": "4px"}),
        ])

        # 4. Actionable Simple Recommendations
        insight_recs = html.Div([
            html.Div("💡 Actionable Recommendations", style={"fontWeight": "700", "fontSize": "13px", "color": PALETTE["amber"], "marginBottom": "6px"}),
            html.Ul([
                html.Li("Enforce attendance follow-ups for students with <75% attendance.", style={"marginBottom": "4px"}),
                html.Li(f"Provide diagnostic quizzes in {w_name if not subj_stats.empty else 'weak subjects'}.", style={"marginBottom": "4px"}),
                html.Li("Pair high achievers with at-risk students for collaborative study.", style={"marginBottom": "4px"}),
            ], style={"fontSize": "11px", "paddingLeft": "16px", "margin": "0", "color": PALETTE["text"]}),
        ])

        # ── Step D: Performance Charts ────────────────────────────────────────
        # 1. Subject-wise average marks chart
        if not subj_stats.empty:
            sorted_subj = subj_stats.sort_values("avg", ascending=True)
            # Dynamic bar colors based on score
            bar_colors = [
                PALETTE["rose"] if score < 60 else
                PALETTE["amber"] if score < 70 else
                PALETTE["blue"] if score < 75 else
                PALETTE["emerald"]
                for score in sorted_subj["avg"]
            ]

            fig_subj = go.Figure()
            fig_subj.add_trace(go.Bar(
                x=sorted_subj["avg"],
                y=sorted_subj["subject"],
                orientation="h",
                marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,0.15)", width=1)),
                text=[f"  {val:.1f}%" for val in sorted_subj["avg"]],
                textposition="outside",
                textfont=dict(color=PALETTE["text"], size=11, family="Inter"),
                hovertemplate="<b>%{y}</b><br>Average Mark: %{x:.1f}%<extra></extra>",
            ))
            # Passing benchmark line at 50%
            fig_subj.add_vline(x=50, line_dash="dash", line_color=PALETTE["rose"], annotation_text="Pass Benchmark (50%)",
                               annotation_position="top left", annotation_font=dict(color=PALETTE["rose"], size=10))
            fig_subj.update_layout(
                template=PLOTLY_DARK,
                paper_bgcolor=TRANSPARENT,
                plot_bgcolor=TRANSPARENT,
                margin=dict(t=20, b=30, l=80, r=40),
                xaxis=dict(title="Average Mark (%)", range=[0, 105], gridcolor=PALETTE["border"], zeroline=False),
                yaxis=dict(title="", tickfont=dict(size=12, color=PALETTE["text"])),
            )
        else:
            fig_subj = _empty_figure()

        # 2. Grade Distribution Chart (Donut)
        grade_order = ["A+", "A", "B", "C", "D", "F"]
        grade_counts = student_summary["grade"].value_counts().reindex(grade_order, fill_value=0).reset_index()
        grade_counts.columns = ["grade", "count"]
        # Keep grades that have > 0 students or show full scale
        pie_colors = [GRADE_COLORS.get(g, PALETTE["indigo"]) for g in grade_counts["grade"]]

        fig_grade = go.Figure(data=[go.Pie(
            labels=grade_counts["grade"],
            values=grade_counts["count"],
            hole=0.55,
            sort=False,
            marker=dict(colors=pie_colors, line=dict(color="#131d33", width=2)),
            textinfo="label+percent",
            textfont=dict(color="#ffffff", size=12, family="Inter"),
            hovertemplate="<b>Grade %{label}</b><br>Students: %{value}<br>Share: %{percent}<extra></extra>",
        )])
        fig_grade.update_layout(
            template=PLOTLY_DARK,
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            margin=dict(t=10, b=20, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(color=PALETTE["muted"], size=11)),
            annotations=[dict(
                text=f"<b>{total_students}</b><br><span style='font-size:10px; color:#94a3b8'>Students</span>",
                x=0.5, y=0.5, font_size=16, font_color=PALETTE["text"], showarrow=False
            )]
        )

        # 3. Top 10 Students Table / Leaderboard
        top_10 = student_summary.head(10).copy()
        top_10["display_rank"] = [
            f"🥇 #{i+1}" if i == 0 else
            f"🥈 #{i+1}" if i == 1 else
            f"🥉 #{i+1}" if i == 2 else
            f"#{i+1}"
            for i in range(len(top_10))
        ]
        top_10["class_sec"] = top_10["class"].astype(str) + " - " + top_10["section"]

        top_table_rows = []
        for _, row in top_10.iterrows():
            g = row["grade"]
            badge_color = GRADE_COLORS.get(g, PALETTE["indigo"])
            top_table_rows.append(
                html.Tr([
                    html.Td(row["display_rank"], style={"fontWeight": "700", "fontSize": "13px"}),
                    html.Td(row["name"], style={"fontWeight": "600", "color": PALETTE["text"]}),
                    html.Td(row["class_sec"], style={"color": PALETTE["muted"]}),
                    html.Td(
                        html.Span(f"{row['avg_marks']:.1f}%", style={
                            "fontWeight": "700",
                            "color": PALETTE["emerald"] if row["avg_marks"] >= 75 else PALETTE["text"]
                        })
                    ),
                    html.Td(
                        html.Span(g, style={
                            "backgroundColor": f"{badge_color}25",
                            "color": badge_color,
                            "padding": "2px 8px",
                            "borderRadius": "12px",
                            "fontSize": "11px",
                            "fontWeight": "700",
                            "border": f"1px solid {badge_color}50"
                        })
                    ),
                    html.Td(f"{row['attendance_pct']:.1f}%", style={"color": PALETTE["muted"]}),
                ], style={"borderBottom": f"1px solid {PALETTE['border']}"})
            )

        top_students_elem = html.Div(
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Rank", style={"color": PALETTE["muted"], "fontSize": "11px", "textTransform": "uppercase"}),
                        html.Th("Student Name", style={"color": PALETTE["muted"], "fontSize": "11px", "textTransform": "uppercase"}),
                        html.Th("Class & Sec", style={"color": PALETTE["muted"], "fontSize": "11px", "textTransform": "uppercase"}),
                        html.Th("Average Marks", style={"color": PALETTE["muted"], "fontSize": "11px", "textTransform": "uppercase"}),
                        html.Th("Grade", style={"color": PALETTE["muted"], "fontSize": "11px", "textTransform": "uppercase"}),
                        html.Th("Attendance", style={"color": PALETTE["muted"], "fontSize": "11px", "textTransform": "uppercase"}),
                    ], style={"borderBottom": f"1px solid {PALETTE['border']}"})
                ),
                html.Tbody(top_table_rows)
            ], style={"width": "100%", "borderCollapse": "collapse", "textAlign": "left"}),
            style={"overflowX": "auto"}
        )

        # ── Step E: Attendance & Correlation Analysis ─────────────────────────
        # 1. Pearson Correlation
        x_att = student_summary["attendance_pct"]
        y_mrk = student_summary["avg_marks"]

        if len(student_summary) >= 3 and x_att.std() > 0 and y_mrk.std() > 0:
            corr = x_att.corr(y_mrk)
            corr_val = round(float(corr), 4)

            # Trendline via np.polyfit
            slope, intercept = np.polyfit(x_att, y_mrk, 1)
            x_line = np.linspace(x_att.min(), x_att.max(), 50)
            y_line = slope * x_line + intercept
            has_trend = True
        else:
            corr_val = 0.0
            has_trend = False

        # Correlation Callout Card
        if corr_val >= 0.7:
            verdict_badge = "Strong Positive Association (r = " + f"{corr_val:.2f}" + ")"
            verdict_color = PALETTE["emerald"]
            verdict_text  = (
                f"Empirical statistical analysis confirms a strong positive correlation (r = {corr_val:.2f}). "
                "Higher attendance directly corresponds to superior examination marks. "
                "Students attending regularly develop stronger conceptual foundations and significantly outperform irregular attendees."
            )
        elif corr_val >= 0.4:
            verdict_badge = "Moderate Positive Association (r = " + f"{corr_val:.2f}" + ")"
            verdict_color = PALETTE["blue"]
            verdict_text  = (
                f"Statistical analysis confirms a moderate positive correlation (r = {corr_val:.2f}). "
                "Classroom attendance is a meaningful factor influencing academic outcomes."
            )
        elif corr_val >= 0.1:
            verdict_badge = "Weak Positive Association (r = " + f"{corr_val:.2f}" + ")"
            verdict_color = PALETTE["amber"]
            verdict_text  = "Mild positive correlation detected. Additional academic factors also contribute to mark variances."
        else:
            verdict_badge = "Negligible / Uncorrelated"
            verdict_color = PALETTE["muted"]
            verdict_text  = "Insufficient correlation in the current small subset."

        card_correlation = html.Div([
            html.Div([
                html.Span("🔍 Correlation Verdict:", style={"fontWeight": "800", "fontSize": "13px", "color": verdict_color, "marginRight": "8px"}),
                html.Span(verdict_badge, style={
                    "backgroundColor": f"{verdict_color}20",
                    "color": verdict_color,
                    "padding": "3px 10px",
                    "borderRadius": "12px",
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "border": f"1px solid {verdict_color}50",
                }),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px", "flexWrap": "wrap", "gap": "6px"}),
            html.P(verdict_text, style={"margin": "0", "fontSize": "12px", "color": PALETTE["text"], "lineHeight": "1.4"}),
        ], style={
            "backgroundColor": "#0d1527",
            "border": f"1px solid {verdict_color}40",
            "borderLeft": f"4px solid {verdict_color}",
            "borderRadius": "10px",
            "padding": "14px 18px",
        })

        # 2. Scatter Plot: Attendance vs Marks with Regression Line
        fig_scatter = go.Figure()

        # Student Scatter Points
        fig_scatter.add_trace(go.Scatter(
            x=student_summary["attendance_pct"],
            y=student_summary["avg_marks"],
            mode="markers",
            marker=dict(
                size=9,
                color=[GRADE_COLORS.get(g, PALETTE["indigo"]) for g in student_summary["grade"]],
                opacity=0.85,
                line=dict(color="#0a0f1d", width=1),
            ),
            text=student_summary["name"],
            customdata=np.stack((
                student_summary["class"].astype(str) + " - " + student_summary["section"],
                student_summary["grade"],
            ), axis=-1),
            hovertemplate="<b>%{text}</b><br>Class-Sec: %{customdata[0]}<br>Grade: %{customdata[1]}<br>Attendance: %{x:.1f}%<br>Marks: %{y:.1f}%<extra></extra>",
            name="Students",
        ))

        # Regression Trendline
        if has_trend:
            fig_scatter.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                line=dict(color=PALETTE["cyan"], width=2.5, dash="solid"),
                name=f"Linear Fit (r = {corr_val:.2f})",
                hoverinfo="skip",
            ))

        fig_scatter.update_layout(
            template=PLOTLY_DARK,
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            margin=dict(t=20, b=30, l=40, r=20),
            xaxis=dict(title="Attendance (%)", range=[40, 102], gridcolor=PALETTE["border"], zeroline=False),
            yaxis=dict(title="Average Marks (%)", range=[10, 105], gridcolor=PALETTE["border"], zeroline=False),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(color=PALETTE["muted"], size=11)),
        )

        # 3. Attendance Categories
        def classify_att(val):
            if val >= 85:
                return "High (≥85%)"
            elif val >= 75:
                return "Moderate (75–85%)"
            else:
                return "Low (<75%)"

        tier_summary = student_summary.copy()
        tier_summary["att_category"] = tier_summary["attendance_pct"].apply(classify_att)

        tier_order = ["High (≥85%)", "Moderate (75–85%)", "Low (<75%)"]
        tier_stats = (
            tier_summary.groupby("att_category")
            .agg(count=("student_id", "count"), avg_marks=("avg_marks", "mean"))
            .reindex(tier_order, fill_value=0)
            .reset_index()
        )

        tier_colors = [PALETTE["emerald"], PALETTE["amber"], PALETTE["rose"]]

        fig_tiers = go.Figure()
        # Bars for Average Marks in each category
        fig_tiers.add_trace(go.Bar(
            x=tier_stats["att_category"],
            y=tier_stats["avg_marks"],
            marker=dict(color=tier_colors, line=dict(color="rgba(255,255,255,0.15)", width=1)),
            text=[f"{m:.1f}%<br>({c} students)" for m, c in zip(tier_stats["avg_marks"], tier_stats["count"])],
            textposition="outside",
            textfont=dict(color=PALETTE["text"], size=11, family="Inter"),
            hovertemplate="<b>%{x}</b><br>Average Marks: %{y:.1f}%<extra></extra>",
            name="Avg Marks",
        ))
        fig_tiers.update_layout(
            template=PLOTLY_DARK,
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            margin=dict(t=20, b=30, l=40, r=20),
            xaxis=dict(title="", tickfont=dict(size=11, color=PALETTE["text"])),
            yaxis=dict(title="Average Mark (%)", range=[0, 105], gridcolor=PALETTE["border"], zeroline=False),
        )

        # ── Step F: Cohort Comparisons ────────────────────────────────────────
        # 1. Class-wise performance (Class 9 vs 10)
        # We compute metrics from master_df aligned to current filters
        class_summary = (
            master_df.groupby(["class", "student_id"])
            .agg(student_avg=("marks_pct", "mean"), att=("attendance_pct", "first"))
            .reset_index()
            .groupby("class")
            .agg(
                avg_marks=("student_avg", "mean"),
                avg_att=("att", "mean"),
                pass_rate=("student_avg", lambda x: (x >= 50.0).mean() * 100.0),
            )
            .round(1)
            .reset_index()
        )
        class_summary["class_label"] = "Class " + class_summary["class"].astype(str)

        fig_class = go.Figure()
        fig_class.add_trace(go.Bar(
            name="Avg Marks (%)",
            x=class_summary["class_label"],
            y=class_summary["avg_marks"],
            marker_color=PALETTE["indigo"],
            text=[f"{v:.1f}%" for v in class_summary["avg_marks"]],
            textposition="outside",
            textfont=dict(color=PALETTE["text"], size=11),
        ))
        fig_class.add_trace(go.Bar(
            name="Pass Rate (%)",
            x=class_summary["class_label"],
            y=class_summary["pass_rate"],
            marker_color=PALETTE["emerald"],
            text=[f"{v:.1f}%" for v in class_summary["pass_rate"]],
            textposition="outside",
            textfont=dict(color=PALETTE["text"], size=11),
        ))
        fig_class.update_layout(
            barmode="group",
            template=PLOTLY_DARK,
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            margin=dict(t=20, b=30, l=40, r=20),
            xaxis=dict(title=""),
            yaxis=dict(title="Percentage (%)", range=[0, 110], gridcolor=PALETTE["border"], zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(color=PALETTE["muted"], size=11)),
        )

        # 2. Section-wise performance (Sections A, B, C)
        sec_summary = (
            master_df.groupby(["section", "student_id"])
            .agg(student_avg=("marks_pct", "mean"), att=("attendance_pct", "first"))
            .reset_index()
            .groupby("section")
            .agg(
                avg_marks=("student_avg", "mean"),
                student_count=("student_id", "count"),
            )
            .round(1)
            .reset_index()
        )
        sec_summary["sec_label"] = "Section " + sec_summary["section"]

        fig_sec = go.Figure()
        fig_sec.add_trace(go.Bar(
            x=sec_summary["sec_label"],
            y=sec_summary["avg_marks"],
            marker=dict(color=[PALETTE["cyan"], PALETTE["blue"], PALETTE["purple"]], line=dict(color="rgba(255,255,255,0.15)", width=1)),
            text=[f"{m:.1f}%<br>({c} students)" for m, c in zip(sec_summary["avg_marks"], sec_summary["student_count"])],
            textposition="outside",
            textfont=dict(color=PALETTE["text"], size=11, family="Inter"),
            hovertemplate="<b>%{x}</b><br>Average Marks: %{y:.1f}%<extra></extra>",
        ))
        fig_sec.update_layout(
            template=PLOTLY_DARK,
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            margin=dict(t=20, b=30, l=40, r=20),
            xaxis=dict(title=""),
            yaxis=dict(title="Average Mark (%)", range=[0, 105], gridcolor=PALETTE["border"], zeroline=False),
        )

        # ── Step G: Detailed Student Advisory Table ───────────────────────────
        # Generate individualized recommendations using rule-based engine
        recs_df = build_recommendations(student_summary, master_df)
        recs_df["class_sec"] = recs_df["class"].astype(str) + " - " + recs_df["section"]

        display_df = recs_df[[
            "student_id", "name", "class_sec", "avg_marks", "grade", "attendance_pct", "recommendation"
        ]].copy()
        display_df.columns = [
            "ID", "Student Name", "Class & Sec", "Marks (%)", "Grade", "Attendance (%)", "Actionable Academic Advice"
        ]

        table_elem = dash_table.DataTable(
            data=display_df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in display_df.columns],
            sort_action="native",
            filter_action="native",
            page_action="native",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#0d1527",
                "color":           PALETTE["text"],
                "fontWeight":      "700",
                "fontSize":        "12px",
                "border":          f"1px solid {PALETTE['border']}",
                "textTransform":   "uppercase",
                "padding":         "10px 12px",
            },
            style_cell={
                "backgroundColor": "#131d33",
                "color":           PALETTE["text"],
                "fontSize":        "12px",
                "border":          f"1px solid {PALETTE['border']}",
                "padding":         "10px 12px",
                "fontFamily":      "'Inter', sans-serif",
                "textAlign":       "left",
                "whiteSpace":      "normal",
                "height":          "auto",
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#0f172a",
                },
                {
                    "if": {"column_id": "Grade", "filter_query": "{Grade} = 'A+' || {Grade} = 'A'"},
                    "color": PALETTE["emerald"],
                    "fontWeight": "700",
                },
                {
                    "if": {"column_id": "Grade", "filter_query": "{Grade} = 'F'"},
                    "color": PALETTE["rose"],
                    "fontWeight": "700",
                },
                {
                    "if": {"column_id": "Marks (%)"},
                    "fontWeight": "600",
                },
            ],
        )

        return (
            kpi_total,
            kpi_marks,
            kpi_att,
            kpi_pass,
            insight_findings,
            insight_weak,
            insight_high,
            insight_recs,
            fig_subj,
            fig_grade,
            top_students_elem,
            card_correlation,
            fig_scatter,
            fig_tiers,
            fig_class,
            fig_sec,
            table_elem
        )
