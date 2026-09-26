# ⚡ Nilist: Human Attention Report

**Built for the IBM Hackathon using IBM Bob IDE**

## 🚀 The Problem
Code reviews suffer from the law of diminishing returns. After the first 1-2 rounds of critical feedback, subsequent rounds often devolve into nitpicking (e.g., variable naming, minor formatting). This wastes valuable engineering time and breaks developer flow.

## 💡 The Solution
Nilist is an intelligent code review analyzer that identifies and flags "low-value" review rounds. By analyzing PR history, it automatically detects rounds with minimal code changes that occur after the critical review phase, allowing teams to collapse or skip them.

## 📊 Key Features
- **Automated Analysis:** Flags any review round after Round 2 as "Low Value."
- **Attention Dashboard:** Visualizes exactly how many minutes/hours are wasted on low-value rounds.
- **One-Click Cleanup:** Simulates the deletion/collapsing of noisy review rounds to reclaim developer focus.

## 🛠️ Tech Stack
- **Python** & **Streamlit** (Frontend Dashboard)
- **Plotly Express** (Data Visualization)
- **IBM Bob IDE** (Core development and AI-assisted optimization)

## 🏃 How to Run
1. Ensure Python 3.x is installed.
2. Install dependencies: `pip install streamlit pandas plotly`
3. Generate sample data: `python src/generate_data.py`
4. Run the analyzer: `python src/analyzer.py`
5. Launch the app: `python -m streamlit run src/app.py`

