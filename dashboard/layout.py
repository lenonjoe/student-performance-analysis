"""
dashboard/layout.py
--------------------
Defines the visual architecture and UI layout for the Student Performance Analysis dashboard.
Built as a modern academic analytics dashboard suitable for college presentations.

Structure:
  1. Header Bar: Title, Project Description, Meta Badges
  2. Filter Toolbar: Class, Section, Subject, Grade filters + Reset button
  3. KPI Cards: Total Students, Average Marks, Average Attendance, Pass Percentage
  4. Automated Insights Section: Key Findings, Weak Subjects, High-Performing Groups, Recommendations
  5. Performance Section: Subject Averages, Grade Distribution, Top 10 Students Leaderboard
  6. Attendance Analysis: Attendance vs Marks with Trendline, Attendance Categories, Correlation Verdict
  7. Comparison Section: Class-wise Performance & Section-wise Performance
  8. Detailed Student Advisory Table: Searchable table with individualized action items
  9. Footer: Academic attribution and technology credits
"""

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc


# ── Color Palette Tokens ──────────────────────────────────────────────────────
THEME = {
    "bg":             "#0a0f1d",   # Deep obsidian navy
    "surface":        "#131d33",   # Elevated card background
    "surface_subtle": "#0d1527",   # Darker inset background
    "border":         "#1e293b",   # Clean slate border
    "text_main":      "#f8fafc",   # Crisp white
    "text_muted":     "#94a3b8",   # Slate gray
    "accent_indigo":  "#6366f1",   # Modern indigo
    "accent_blue":    "#3b82f6",   # Vibrant blue
    "accent_cyan":    "#06b6d4",   # Cyan / Teal
    "accent_emerald": "#10b981",   # Emerald green (pass / success)
    "accent_amber":   "#f59e0b",   # Amber / Warning
    "accent_rose":    "#ef4444",   # Rose / Alert
}

CARD_STYLE = {
    "backgroundColor": THEME["surface"],
    "border":          f"1px solid {THEME['border']}",
    "borderRadius":    "14px",
    "padding":         "22px",
    "boxShadow":       "0 6px 24px rgba(0, 0, 0, 0.35)",
}


# ── Helper: KPI Metric Card ───────────────────────────────────────────────────
def build_kpi_card(card_id: str, title: str, icon: str, subtitle: str, accent_color: str) -> dbc.Col:
    """
    Builds a single responsive KPI card with an icon, title, dynamic value,
    contextual micro-label, and colored bottom accent border.
    """
    return dbc.Col(
        html.Div([
            html.Div([
                html.Span(icon, style={"fontSize": "26px", "lineHeight": "1"}),
                html.Span(
                    title,
                    style={
                        "color":         THEME["text_muted"],
                        "fontSize":      "11px",
                        "fontWeight":    "700",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.08em",
                    }
                ),
            ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "8px"}),

            # Dynamic Value
            html.Div(
                id=card_id,
                children="--",
                style={
                    "color":        THEME["text_main"],
                    "fontSize":     "30px",
                    "fontWeight":   "800",
                    "letterSpacing": "-0.02em",
                    "lineHeight":   "1.2",
                }
            ),

            # Contextual micro-label
            html.Div(
                subtitle,
                style={
                    "color":     THEME["text_muted"],
                    "fontSize":  "12px",
                    "marginTop": "6px",
                    "fontWeight":"500",
                }
            ),
        ], style={
            **CARD_STYLE,
            "borderBottom": f"3px solid {accent_color}",
            "position":     "relative",
            "overflow":     "hidden",
        }),
        xs=12, sm=6, lg=3,
    )


# ── Helper: Filter Dropdown ───────────────────────────────────────────────────
def build_filter(dropdown_id: str, label: str, options: list) -> html.Div:
    """Creates a labeled dropdown filter with an 'All' option included."""
    return html.Div([
        html.Label(label, style={
            "color":         THEME["text_muted"],
            "fontSize":      "11px",
            "fontWeight":    "700",
            "marginBottom":  "6px",
            "display":       "block",
            "textTransform": "uppercase",
            "letterSpacing": "0.06em",
        }),
        dcc.Dropdown(
            id=dropdown_id,
            options=[{"label": "All", "value": "All"}] + options,
            value="All",
            clearable=False,
            style={
                "backgroundColor": THEME["surface_subtle"],
                "color":           THEME["text_main"],
            },
        ),
    ], style={"flex": "1", "minWidth": "160px"})


# ── Helper: Section Title Header ──────────────────────────────────────────────
def build_section_header(badge_text: str, title: str, subtitle: str) -> html.Div:
    """Builds a standardized section title banner with an uppercase pill badge."""
    return html.Div([
        html.Div(badge_text, className="section-badge"),
        html.H3(title, className="section-heading", style={"fontSize": "19px", "fontWeight": "800", "margin": "0 0 4px 0"}),
        html.P(subtitle, className="section-subtext", style={"fontSize": "13px", "color": THEME["text_muted"], "margin": "0 0 16px 0"}),
    ], style={"marginBottom": "12px", "marginTop": "10px"})


# ── Main Layout Builder ───────────────────────────────────────────────────────
def build_layout(classes: list, sections: list, subjects: list, grades: list = None) -> html.Div:
    """
    Constructs the entire dashboard UI tree.
    Called once during app initialization.
    """
    if grades is None:
        grades = ["A+", "A", "B", "C", "D", "F"]
    class_opts   = [{"label": f"Class {c}", "value": c} for c in sorted(classes)]
    section_opts = [{"label": f"Section {s}", "value": s} for s in sorted(sections)]
    subject_opts = [{"label": s,             "value": s} for s in sorted(subjects)]
    grade_opts   = [{"label": f"Grade {g}",   "value": g} for g in grades]

    return html.Div(
        style={
            "backgroundColor": THEME["bg"],
            "minHeight":       "100vh",
            "color":           THEME["text_main"],
            "fontFamily":      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "paddingBottom":   "60px",
        },
        children=[

            # =================================================================
            # 1. HEADER BAR
            # =================================================================
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("🎓", style={"fontSize": "38px", "marginRight": "14px"}),
                        html.Div([
                            html.H1(
                                "Student Performance Analysis",
                                style={
                                    "margin":        "0",
                                    "fontSize":      "24px",
                                    "fontWeight":    "800",
                                    "letterSpacing": "-0.02em",
                                    "color":         THEME["text_main"],
                                }
                            ),
                            html.P(
                                "Modern Academic Analytics & Pedagogical Decision Support Platform",
                                style={
                                    "margin":    "3px 0 0 0",
                                    "color":     THEME["text_muted"],
                                    "fontSize":  "13px",
                                    "fontWeight":"400",
                                }
                            ),
                        ]),
                    ], style={"display": "flex", "alignItems": "center"}),

                    # Meta Pills on the right
                    html.Div([
                        html.Span("Academic Year 2025–26", style={
                            "backgroundColor": "rgba(99, 102, 241, 0.15)",
                            "color":           "#a5b4fc",
                            "padding":         "6px 12px",
                            "borderRadius":    "20px",
                            "fontSize":        "12px",
                            "fontWeight":      "600",
                            "border":          "1px solid rgba(99, 102, 241, 0.3)",
                            "marginRight":     "8px",
                        }),
                        html.Span("College Presentation Edition", style={
                            "backgroundColor": "rgba(16, 185, 129, 0.15)",
                            "color":           "#6ee7b7",
                            "padding":         "6px 12px",
                            "borderRadius":    "20px",
                            "fontSize":        "12px",
                            "fontWeight":      "600",
                            "border":          "1px solid rgba(16, 185, 129, 0.3)",
                        }),
                    ], style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "6px"}),
                ], style={
                    "display":        "flex",
                    "justifyContent": "space-between",
                    "alignItems":     "center",
                    "flexWrap":       "wrap",
                    "gap":            "16px",
                    "maxWidth":       "1400px",
                    "margin":         "0 auto",
                }),
            ], style={
                "background":   "linear-gradient(135deg, #0d1527 0%, #162444 100%)",
                "padding":      "20px 36px",
                "borderBottom": f"1px solid {THEME['border']}",
                "boxShadow":    "0 4px 20px rgba(0, 0, 0, 0.4)",
                "position":     "sticky",
                "top":          "0",
                "zIndex":       "999",
            }),

            # Container Wrapper
            html.Div(style={"maxWidth": "1400px", "margin": "0 auto", "padding": "28px 24px"}, children=[

                # =============================================================
                # 2. INTERACTIVE FILTER TOOLBAR
                # =============================================================
                html.Div([
                    html.Div([
                        html.Span("⚡", style={"fontSize": "18px"}),
                        html.Span("Filter Dataset", style={
                            "color":         THEME["text_main"],
                            "fontWeight":    "700",
                            "fontSize":      "13px",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.06em",
                        }),
                    ], style={"display": "flex", "alignItems": "center", "gap": "8px", "paddingBottom": "6px"}),

                    html.Div([
                        build_filter("filter-class",   "Class",   class_opts),
                        build_filter("filter-section", "Section", section_opts),
                        build_filter("filter-subject", "Subject", subject_opts),
                        build_filter("filter-grade",   "Grade",   grade_opts),

                        # Reset Button
                        html.Div([
                            html.Label("\u00a0", style={"display": "block", "fontSize": "11px", "marginBottom": "6px"}),
                            html.Button(
                                "↺ Reset Filters",
                                id="btn-reset-filters",
                                n_clicks=0,
                                style={
                                    "backgroundColor": "#1e293b",
                                    "color":           "#e2e8f0",
                                    "border":          "1px solid #334155",
                                    "borderRadius":    "8px",
                                    "padding":         "8px 16px",
                                    "fontSize":        "13px",
                                    "fontWeight":      "600",
                                    "cursor":          "pointer",
                                    "height":          "38px",
                                    "transition":      "all 0.2s ease",
                                }
                            ),
                        ], style={"alignSelf": "flex-end"}),
                    ], style={
                        "display":  "flex",
                        "gap":      "16px",
                        "flexWrap": "wrap",
                        "flex":     "1",
                        "alignItems":"flex-end",
                    }),
                ], style={
                    **CARD_STYLE,
                    "marginBottom":   "28px",
                    "padding":         "16px 22px",
                    "display":        "flex",
                    "flexDirection":  "column",
                    "gap":            "12px",
                    "background":     "linear-gradient(145deg, #10192e 0%, #0d1527 100%)",
                }),

                # =============================================================
                # 3. EXECUTIVE KPI CARDS (4 Essential Metrics)
                # =============================================================
                dbc.Row([
                    build_kpi_card(
                        "kpi-total-students",
                        "Total Students",
                        "👥",
                        "Active Enrolled Cohort",
                        THEME["accent_indigo"]
                    ),
                    build_kpi_card(
                        "kpi-avg-marks",
                        "Average Marks",
                        "📊",
                        "Overall Score Across Subjects",
                        THEME["accent_blue"]
                    ),
                    build_kpi_card(
                        "kpi-avg-attendance",
                        "Average Attendance",
                        "📅",
                        "Classroom Engagement Rate",
                        THEME["accent_cyan"]
                    ),
                    build_kpi_card(
                        "kpi-pass-pct",
                        "Pass Percentage",
                        "✅",
                        "Passing Threshold ≥ 50%",
                        THEME["accent_emerald"]
                    ),
                ], className="g-3 mb-4"),

                # =============================================================
                # 4. AUTOMATED INSIGHTS SECTION
                # =============================================================
                build_section_header(
                    "Executive Intelligence",
                    "Automated Dataset Insights & Pedagogical Findings",
                    "Synthesized algorithmic findings, weakness detection, top cohorts, and institutional recommendations."
                ),

                dbc.Row([
                    # Key Findings Card
                    dbc.Col(
                        html.Div(id="insight-key-findings", children=[
                            html.Div("Calculating key findings...", style={"color": THEME["text_muted"]})
                        ], style={**CARD_STYLE, "height": "100%", "borderLeft": f"4px solid {THEME['accent_indigo']}"}),
                        md=6, lg=3
                    ),
                    # Weak Subjects Card
                    dbc.Col(
                        html.Div(id="insight-weak-subjects", children=[
                            html.Div("Analyzing subject vulnerabilities...", style={"color": THEME["text_muted"]})
                        ], style={**CARD_STYLE, "height": "100%", "borderLeft": f"4px solid {THEME['accent_rose']}"}),
                        md=6, lg=3
                    ),
                    # High-Performing Groups Card
                    dbc.Col(
                        html.Div(id="insight-high-performers", children=[
                            html.Div("Identifying top academic groups...", style={"color": THEME["text_muted"]})
                        ], style={**CARD_STYLE, "height": "100%", "borderLeft": f"4px solid {THEME['accent_emerald']}"}),
                        md=6, lg=3
                    ),
                    # Simple Recommendations Card
                    dbc.Col(
                        html.Div(id="insight-recommendations", children=[
                            html.Div("Formulating academic guidance...", style={"color": THEME["text_muted"]})
                        ], style={**CARD_STYLE, "height": "100%", "borderLeft": f"4px solid {THEME['accent_amber']}"}),
                        md=6, lg=3
                    ),
                ], className="g-3 mb-4"),

                # =============================================================
                # 5. ACADEMIC PERFORMANCE SECTION
                # =============================================================
                build_section_header(
                    "Performance Analytics",
                    "Subject Mastery, Grade Spread & Student Leaderboard",
                    "In-depth breakdown of curricular achievement, overall grade distribution, and top 10 ranked scholars."
                ),

                dbc.Row([
                    # Subject-wise average marks
                    dbc.Col(
                        html.Div([
                            html.Div([
                                html.Span("📚", style={"fontSize": "20px"}),
                                html.Span("Subject-Wise Average Marks (%)", style={
                                    "fontWeight": "700", "fontSize": "14px", "color": THEME["text_main"]
                                }),
                            ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "14px"}),
                            dcc.Graph(
                                id="chart-subject-avg",
                                config={"displayModeBar": False},
                                style={"height": "340px"},
                            ),
                        ], style=CARD_STYLE),
                        lg=6
                    ),

                    # Grade distribution
                    dbc.Col(
                        html.Div([
                            html.Div([
                                html.Span("🎯", style={"fontSize": "20px"}),
                                html.Span("Grade Distribution Breakdown", style={
                                    "fontWeight": "700", "fontSize": "14px", "color": THEME["text_main"]
                                }),
                            ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "14px"}),
                            dcc.Graph(
                                id="chart-grade-dist",
                                config={"displayModeBar": False},
                                style={"height": "340px"},
                            ),
                        ], style=CARD_STYLE),
                        lg=6
                    ),
                ], className="g-3 mb-3"),

                # Top 10 Students Table / Leaderboard
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.Div([
                                html.Span("🏆", style={"fontSize": "22px"}),
                                html.Div([
                                    html.Span("Top 10 Students Leaderboard", style={
                                        "fontWeight": "700", "fontSize": "15px", "color": THEME["text_main"], "display": "block"
                                    }),
                                    html.Span("Recognizing highest cumulative academic achievers across the filtered cohort", style={
                                        "fontSize": "12px", "color": THEME["text_muted"]
                                    }),
                                ]),
                            ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "16px"}),

                            html.Div(id="container-top-students"),
                        ], style=CARD_STYLE),
                        width=12
                    ),
                ], className="g-3 mb-4"),

                # =============================================================
                # 6. ATTENDANCE & CORRELATION ANALYSIS
                # =============================================================
                build_section_header(
                    "Attendance & Impact Analysis",
                    "Attendance Correlation & Attendance Category Breakdown",
                    "Evaluating the empirical relationship between classroom attendance and academic outcomes."
                ),

                # Correlation Verdict Highlight Banner
                html.Div(id="card-attendance-correlation", style={"marginBottom": "20px"}),

                dbc.Row([
                    # Scatter plot: Attendance vs Marks with Trendline
                    dbc.Col(
                        html.Div([
                            html.Div([
                                html.Span("📈", style={"fontSize": "20px"}),
                                html.Span("Attendance vs Marks (Regression Analysis)", style={
                                    "fontWeight": "700", "fontSize": "14px", "color": THEME["text_main"]
                                }),
                            ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "14px"}),
                            dcc.Graph(
                                id="chart-attendance-scatter",
                                config={"displayModeBar": False},
                                style={"height": "350px"},
                            ),
                        ], style=CARD_STYLE),
                        lg=7
                    ),

                    # Attendance Categories
                    dbc.Col(
                        html.Div([
                            html.Div([
                                html.Span("🗂️", style={"fontSize": "20px"}),
                                html.Span("Attendance Categories vs Marks", style={
                                    "fontWeight": "700", "fontSize": "14px", "color": THEME["text_main"]
                                }),
                            ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "14px"}),
                            dcc.Graph(
                                id="chart-attendance-tiers",
                                config={"displayModeBar": False},
                                style={"height": "350px"},
                            ),
                        ], style=CARD_STYLE),
                        lg=5
                    ),
                ], className="g-3 mb-4"),

                # =============================================================
                # 7. COMPARISON SECTION (Class & Section)
                # =============================================================
                build_section_header(
                    "Cohort Comparisons",
                    "Class-Wise & Section-Wise Performance Comparative",
                    "Direct benchmarking across academic standards (Class 9 vs 10) and classroom sections (A, B, C)."
                ),

                dbc.Row([
                    # Class-wise performance
                    dbc.Col(
                        html.Div([
                            html.Div([
                                html.Span("🏫", style={"fontSize": "20px"}),
                                html.Span("Class-Wise Performance (Average Marks & Pass Rate)", style={
                                    "fontWeight": "700", "fontSize": "14px", "color": THEME["text_main"]
                                }),
                            ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "14px"}),
                            dcc.Graph(
                                id="chart-class-comparison",
                                config={"displayModeBar": False},
                                style={"height": "330px"},
                            ),
                        ], style=CARD_STYLE),
                        lg=6
                    ),

                    # Section-wise performance
                    dbc.Col(
                        html.Div([
                            html.Div([
                                html.Span("🏢", style={"fontSize": "20px"}),
                                html.Span("Section-Wise Performance Comparison", style={
                                    "fontWeight": "700", "fontSize": "14px", "color": THEME["text_main"]
                                }),
                            ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "14px"}),
                            dcc.Graph(
                                id="chart-section-comparison",
                                config={"displayModeBar": False},
                                style={"height": "330px"},
                            ),
                        ], style=CARD_STYLE),
                        lg=6
                    ),
                ], className="g-3 mb-4"),

                # =============================================================
                # 8. DETAILED STUDENT ADVISORY & RECOMMENDATIONS TABLE
                # =============================================================
                build_section_header(
                    "Student Advisory",
                    "Comprehensive Student Records & Targeted Recommendations",
                    "Complete interactive roster with personalized academic advice and subject interventions."
                ),

                html.Div([
                    html.Div(id="container-student-table"),
                ], style={**CARD_STYLE, "marginBottom": "36px"}),

                # =============================================================
                # 9. FOOTER
                # =============================================================
                html.Div([
                    html.P([
                        "Student Performance Analysis Dashboard  •  Academic Analytics Platform",
                    ], style={"margin": "0 0 6px 0", "fontWeight": "600", "color": THEME["text_main"]}),
                    html.P([
                        "Engineered with Python, Pandas, NumPy, Plotly & Dash  •  College Project Presentation",
                    ], style={"margin": "0", "fontSize": "12px", "color": THEME["text_muted"]}),
                ], style={
                    "textAlign":    "center",
                    "padding":      "24px 0",
                    "borderTop":    f"1px solid {THEME['border']}",
                    "marginTop":    "20px",
                }),

            ]),
        ]
    )
