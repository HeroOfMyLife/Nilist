import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

# Import the reusable analysis function from the sibling module
from analyzer import analyze_data


# ── AI INSIGHT CLASSIFIER ──────────────────────────────────────────────────────
# Keyword-based triage function. Accepts a list of comment strings and returns
# a single actionable insight sentence based on matched keyword categories.
def get_ai_insight(comments_list: list[str]) -> str:
    """Return a triage insight string derived from reviewer comment keywords."""
    combined = " ".join(comments_list).lower()

    if any(kw in combined for kw in ("lgtm", "nit", "format", "rename")):
        return "🤖 AI Insight: Nitpick detected. Suggest auto-fixing with a linter. No human review needed."
    if any(kw in combined for kw in ("typo", "spacing")):
        return "🤖 AI Insight: Minor formatting. Could be handled by pre-commit hooks."
    return "🤖 AI Insight: Low-impact feedback. Consider consolidating with previous rounds."


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

# ── SIDEBAR: ROI CALCULATOR ────────────────────────────────────────────────────
with st.sidebar:
    st.title("💰 ROI Calculator")
    num_developers = st.number_input("Number of Developers", min_value=1, value=10, step=1)
    hourly_rate    = st.number_input("Average Hourly Rate ($)", min_value=1, value=75, step=1)

# ── DATA LOADING ───────────────────────────────────────────────────────────────
# File uploader — appears at the top of the UI before any dashboard content.
# Accepts a JSON file in the same format as data/sample_reviews.json
# (a list of PR objects with a 'rounds' key).
uploaded_file = st.file_uploader(
    "🗃️Upload GitHub/GitLab PR Export (JSON)",
    type=["json"],
    help="For best results, export your Pull Request review history as a JSON file. The app will automatically detect low-value rounds."
)

if uploaded_file is not None:
    # ── User-supplied data ─────────────────────────────────────────────────────

    # ── Guard 1: empty file ───────────────────────────────────────────────────
    raw_bytes = uploaded_file.read()
    if not raw_bytes.strip():
        st.error(
            "❌ The uploaded file is empty. "
            "Please upload a non-empty JSON file."
        )
        st.stop()

    # ── Guard 2: valid JSON ───────────────────────────────────────────────────
    try:
        parsed = json.loads(raw_bytes)
    except json.JSONDecodeError as exc:
        st.error(
            f"❌ **Malformed JSON** — the file could not be parsed.\n\n"
            f"**Parser says:** `{exc.msg}` at line {exc.lineno}, column {exc.colno}.\n\n"
            "**How to fix:** Open the file in a text editor and check for:\n"
            "- Missing or extra commas\n"
            "- Unquoted keys or string values\n"
            "- Unclosed brackets `[` or braces `{`"
        )
        st.stop()

    # ── Guard 3: top-level type & structure ───────────────────────────────────
    if isinstance(parsed, list):
        # ── Format A: raw reviews  [ { "pr_id": …, "rounds": […] }, … ]

        if len(parsed) == 0:
            st.warning(
                "⚠️ The uploaded reviews file contains no PR entries (empty array). "
                "Nothing to analyse — please upload a file with at least one PR object."
            )
            st.stop()

        # Validate that every item is a dict with a 'rounds' key
        invalid = [
            i for i, item in enumerate(parsed)
            if not isinstance(item, dict) or "rounds" not in item
        ]
        if invalid:
            bad_indices = ", ".join(str(i) for i in invalid[:5])
            st.error(
                f"❌ **Missing `rounds` key** in PR object(s) at position(s): {bad_indices}.\n\n"
                "Each PR entry must follow this structure:\n"
                "```json\n"
                "{\n"
                '  "pr_id": "PR-1001",\n'
                '  "title": "Fix auth bug",\n'
                '  "rounds": [\n'
                "    {\n"
                '      "round_number": 1,\n'
                '      "reviewer_comments": ["Security flaw found"],\n'
                '      "lines_of_code_changed": 42,\n'
                '      "time_spent_minutes": 30,\n'
                '      "value_assessment": "high"\n'
                "    }\n"
                "  ]\n"
                "}\n"
                "```"
            )
            st.stop()

        try:
            report = analyze_data(parsed)
        except Exception as exc:
            st.error(
                f"❌ Analysis failed after loading the file: `{exc}`\n\n"
                "The JSON structure looks correct but the data may contain unexpected values. "
                "Check that all required fields (`round_number`, `lines_of_code_changed`, "
                "`time_spent_minutes`, `value_assessment`) are present in every round."
            )
            st.stop()

    elif isinstance(parsed, dict) and "summary" in parsed and "deleted_rounds" in parsed:
        # ── Format B: pre-generated report  { "summary": {…}, "deleted_rounds": […] }
        # Already analysed — use it directly without re-processing.
        report = parsed

    else:
        st.error(
            "❌ **Unrecognised JSON format.**\n\n"
            "Please upload one of these two supported formats:\n\n"
            "**Format A — Reviews file** (a JSON array of PR objects):\n"
            "```json\n"
            '[{ "pr_id": "PR-1001", "title": "...", "rounds": [...] }]\n'
            "```\n"
            "**Format B — Pre-generated report** (a JSON object with these keys):\n"
            "```json\n"
            '{ "summary": { ... }, "deleted_rounds": [ ... ] }\n'
            "```"
        )
        st.stop()

    data_source_label = f"📂 Analysing uploaded file: **{uploaded_file.name}**"
else:
    # ── Fallback: read the pre-generated attention_report.json directly ────────
    # (This keeps the demo working without needing sample_reviews.json present.)
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    report_file = os.path.join(script_dir, '..', 'data', 'attention_report.json')
    with open(report_file, 'r') as f:
        report = json.load(f)
    data_source_label = "🗂 Using built-in demo dataset"

summary        = report['summary']
deleted_rounds = report['deleted_rounds']

# ── HEADER ─────────────────────────────────────────────────────────────────────
# logo.png lives in the same directory as app.py (src/logo.png).
# Build the path relative to __file__ so it works regardless of the CWD
# Streamlit is launched from.
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

logo_col, title_col = st.columns([1, 5], gap="medium")

with logo_col:
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)
    else:
        # Graceful fallback — keeps layout intact if the file is ever missing
        st.markdown("<div style='font-size:3rem;'>⚡</div>", unsafe_allow_html=True)

with title_col:
    st.title("⚡ Nilist: Human Attention Report")
    st.caption(data_source_label)

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
col1, col2, col3, col4, col5 = st.columns(5, gap="medium")

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

with col5:
    monthly_savings = (
        (summary['total_time_wasted_minutes'] / 60)
        * hourly_rate
        * num_developers
        * (4 * 4)  # 4 PRs per dev per week × 4 weeks
    )
    st.metric(
        label="💰 Estimated Monthly Savings",
        value=f"**${monthly_savings:,.0f} / month**",
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

        # Add AI Insight column — apply classifier row-wise from raw 'reviewer_comments' list
        df_display['🤖 AI Insight'] = df['reviewer_comments'].apply(get_ai_insight)

        with st.expander("🔍 View Detailed AI Analysis of Deleted Rounds", expanded=False):
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
