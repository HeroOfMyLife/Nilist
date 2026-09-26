import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nilist: Human Attention Report",
    page_icon="⚡",
    layout="wide",
)

# ── GLOBAL THEME CSS ───────────────────────────────────────────────────────────
# Green-on-black palette with a custom primary action button style.
st.markdown("""
<style>
/* ── App background & default text ── */
[data-testid="stAppViewContainer"] {
    background-color: #0d0d0d;
    color: #e0ffe0;
}
[data-testid="stHeader"] { background-color: #0d0d0d; }
[data-testid="stSidebar"] { background-color: #111811; }

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 { color: #39ff14 !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background-color: #111811;
    border: 1px solid #39ff14;
    border-radius: 8px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] > div { color: #7fcd7f !important; font-size: 0.85rem; }
[data-testid="stMetricValue"] > div { color: #39ff14 !important; font-size: 1.8rem; font-weight: 700; }
[data-testid="stMetricDelta"] > div { color: #ff4b4b !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #1e3d1e; border-radius: 6px; }

/* ── Divider ── */
hr { border-color: #1e3d1e !important; }

/* ── Caption / muted text ── */
[data-testid="stCaptionContainer"] p { color: #4d8f4d; }

/* ── Execute Nilist Protocol button ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #1a6b1a 0%, #39ff14 100%);
    color: #0d0d0d !important;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.05em;
    border: none;
    border-radius: 6px;
    padding: 0.65rem 2rem;
    box-shadow: 0 0 12px rgba(57, 255, 20, 0.45);
    transition: box-shadow 0.2s ease;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 0 24px rgba(57, 255, 20, 0.75);
}
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ───────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
report_file = os.path.join(script_dir, '..', 'data', 'attention_report.json')

with open(report_file, 'r') as f:
    report = json.load(f)

summary       = report['summary']
deleted_rounds = report['deleted_rounds']

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.title("⚡ Nilist: Human Attention Report")
st.markdown(
    "<p style='color:#7fcd7f; font-size:1.05rem; max-width:760px;'>"
    "<strong style='color:#39ff14;'>The Problem:</strong> Code reviews suffer from diminishing returns — "
    "rounds after the first two drift into nitpicks that waste valuable engineering time.<br>"
    "<strong style='color:#39ff14;'>The Solution:</strong> Nilist analyses review history, automatically "
    "flags low-value rounds (anything after Round 2), and collapses them — protecting human attention "
    "for work that actually matters."
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── KEY METRICS ────────────────────────────────────────────────────────────────
st.subheader("📊 Summary Metrics")
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.metric(label="PRs Analyzed", value=summary['total_prs_analyzed'])
with col2:
    st.metric(label="High-Value Rounds Kept", value=summary['total_high_value_rounds'])
with col3:
    st.metric(
        label="Low-Value Rounds Deleted",
        value=summary['total_low_value_rounds'],
        delta="-100% Noise",
    )
with col4:
    st.metric(
        label="⏱ Engineering Time Saved",
        value=f"{summary['time_saved_hours']} hrs",
        delta=f"{summary['total_time_wasted_minutes']} min reclaimed",
    )

st.divider()

# ── CHART + TABLE ──────────────────────────────────────────────────────────────
if deleted_rounds:
    df = pd.DataFrame(deleted_rounds)

    # ── Build display DataFrame ──
    df_display = df[
        ['pr_id', 'round_number', 'lines_of_code_changed', 'time_spent_minutes', 'reviewer_comments']
    ].copy()
    df_display.columns = ['Pull Request', 'Round #', 'Lines Changed', 'Time Wasted (min)', 'Comments']

    chart_col, table_col = st.columns([1, 1], gap="large")

    # ── Bar chart: Time Wasted per PR ──
    with chart_col:
        st.subheader("⏱ Time Wasted by PR")
        st.caption("Total minutes burned on low-value review rounds, grouped by Pull Request.")

        # Aggregate total time wasted per PR so multi-round PRs stack correctly
        chart_df = (
            df.groupby('pr_id', sort=False)['time_spent_minutes']
            .sum()
            .reset_index()
            .rename(columns={'pr_id': 'Pull Request', 'time_spent_minutes': 'Time Wasted (min)'})
        )

        fig = px.bar(
            chart_df,
            x='Pull Request',
            y='Time Wasted (min)',
            text='Time Wasted (min)',
            color_discrete_sequence=['#39ff14'],
        )
        fig.update_traces(textposition='outside', marker_line_color='#1a6b1a', marker_line_width=1.2)
        fig.update_layout(
            paper_bgcolor='#0d0d0d',
            plot_bgcolor='#111811',
            font_color='#7fcd7f',
            xaxis=dict(tickfont_color='#7fcd7f', gridcolor='#1e3d1e'),
            yaxis=dict(tickfont_color='#7fcd7f', gridcolor='#1e3d1e'),
            margin=dict(t=20, b=10, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Detail table ──
    with table_col:
        st.subheader("🗑 Rounds Flagged for Deletion")
        st.caption("Every round that added minimal code changes after the critical review phase.")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ── Action button ──
    st.divider()
    st.markdown(
        "<p style='color:#7fcd7f; margin-bottom:0.4rem;'>"
        "Ready to reclaim your team's attention? Execute the protocol to collapse all flagged rounds."
        "</p>",
        unsafe_allow_html=True,
    )
    if st.button("⚡ Execute Nilist Protocol — Delete Low-Value Rounds", type="primary"):
        st.success("✅ Protocol executed. Low-value rounds collapsed. The team just reclaimed hours of deep-focus time.")
        st.balloons()

else:
    st.info("No low-value rounds found. Great job, team!")

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Built for the IBM Hackathon using IBM Bob IDE · Data is synthetic for demonstration purposes.")
