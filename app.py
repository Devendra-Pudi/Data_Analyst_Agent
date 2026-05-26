import streamlit as st
import pandas as pd
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.data_loader import load_data
from engine.executor import execute_code
from utils.suggestions import generate_suggestions
from utils.helpers import extract_code_from_text

# --- Page Config ---
st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "AI Data Analyst Agent — Powered by CrewAI & OpenRouter Free Models"
    }
)

# --- Load Custom CSS ---
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    # API Key
    api_key = st.text_input(
        "🔑 OpenRouter API Key",
        type="password",
        value=os.getenv("OPENROUTER_API_KEY", ""),
        help="Get your free API key at [openrouter.ai](https://openrouter.ai)",
        placeholder="sk-or-v1-..."
    )

    st.markdown("---")
    st.markdown("### 🤖 Agent Models")
    st.markdown("""
    | Agent | Model |
    |-------|-------|
    | 🔍 Profiler | Gemma 4 31B |
    | 📊 Analyst | Nemotron 3 Super |
    | 💻 Coder | Qwen3 Coder |
    | 📝 Reporter | DeepSeek V4 Flash |
    """)

    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown(
        "**AI Data Analyst Agent** uses 4 specialized AI agents "
        "to analyze your data, write Python code, execute it, "
        "and generate insightful reports — all with full transparency."
    )
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/GitHub-Repo-181717?logo=github)]"
        "(https://github.com/Devendra-Pudi/Data_Analyst_Agent)"
    )

# --- Hero Header ---
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0;">
    <h1 style="
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6C63FF, #3B82F6, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    ">🧠 AI Data Analyst Agent</h1>
    <p style="
        font-size: 1.2rem;
        color: #9CA3AF;
        max-width: 600px;
        margin: 0 auto;
    ">Upload your data. Ask questions. Get insights with charts, tables, and reports — powered by 4 specialized AI agents.</p>
</div>
""", unsafe_allow_html=True)

# --- File Upload ---
st.markdown("---")
col_upload, col_sample = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "📁 Upload your data file",
        type=["csv", "xlsx", "xls", "json"],
        help="Supported formats: CSV, Excel (.xlsx/.xls), JSON"
    )

with col_sample:
    st.markdown("<br>", unsafe_allow_html=True)
    use_sample = st.button("📊 Use Sample Data", use_container_width=True)

# --- Load Data ---
df = None

if use_sample:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sales_data.csv")
    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
        st.success("✅ Loaded sample sales dataset (170 rows × 8 columns)")
    else:
        st.error("Sample data file not found.")

elif uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.success(f"✅ Loaded **{uploaded_file.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")
    except Exception as e:
        st.error(f"❌ Failed to load file: {e}")

if df is None:
    st.info("👆 Upload a CSV, Excel, or JSON file to get started — or try the sample dataset!")
    st.stop()

# --- Data Preview ---
with st.expander("📋 Data Preview (first 100 rows)", expanded=False):
    st.dataframe(df.head(100), use_container_width=True, height=400)

# --- Quick Stats ---
st.markdown("### 📊 Quick Stats")
stat_cols = st.columns(4)

with stat_cols[0]:
    st.metric("Rows", f"{df.shape[0]:,}")
with stat_cols[1]:
    st.metric("Columns", f"{df.shape[1]}")
with stat_cols[2]:
    null_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100)
    st.metric("Missing %", f"{null_pct:.1f}%")
with stat_cols[3]:
    num_cols = len(df.select_dtypes(include=["number"]).columns)
    st.metric("Numeric Cols", f"{num_cols}")

# --- Smart Suggestions ---
st.markdown("### 🎯 Smart Suggestions")
suggestions = generate_suggestions(df)

suggestion_cols = st.columns(min(len(suggestions), 3))
selected_suggestion = None

for i, suggestion in enumerate(suggestions):
    col_idx = i % 3
    with suggestion_cols[col_idx]:
        if st.button(f"💡 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
            selected_suggestion = suggestion

# --- Question Input ---
st.markdown("### 💬 Ask a Question")
question = st.text_area(
    "What would you like to know about your data?",
    value=selected_suggestion if selected_suggestion else "",
    height=80,
    placeholder="e.g., Show the distribution of Revenue by Region as a bar chart"
)

# --- Run Analysis ---
run_clicked = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

if run_clicked:
    if not question.strip():
        st.warning("⚠️ Please enter a question or select a suggestion.")
        st.stop()

    if not api_key:
        st.warning("⚠️ Please enter your OpenRouter API key in the sidebar.")
        st.stop()

    # Run the CrewAI analysis
    with st.spinner("🤖 AI agents are analyzing your data... This may take 30-60 seconds."):
        try:
            from agents.crew import run_analysis
            result = run_analysis(df, question.strip(), api_key)
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.stop()

    if not result.get("success", False):
        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")

        # Still show partial results if available
        if result.get("code"):
            with st.expander("💻 Generated Code (before failure)"):
                st.code(result["code"], language="python")
        st.stop()

    # --- Display Results ---
    st.markdown("---")
    st.markdown("## 📈 Results")

    # Create tabs for results
    tab_result, tab_code, tab_report, tab_profile = st.tabs([
        "📊 Result", "💻 Code", "📝 Report", "📋 Profile"
    ])

    # --- Result Tab ---
    with tab_result:
        exec_result = result.get("execution_result", {})
        result_type = exec_result.get("type", "text")

        if result_type == "dataframe":
            st.dataframe(exec_result["data"], use_container_width=True)
            # Download button
            csv_data = exec_result["data"].to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download as CSV",
                data=csv_data,
                file_name="analysis_result.csv",
                mime="text/csv"
            )

        elif result_type == "image":
            st.image(exec_result["data"], use_container_width=True)
            # Download chart
            with open(exec_result["data"], "rb") as f:
                st.download_button(
                    "⬇️ Download Chart",
                    data=f.read(),
                    file_name="chart.png",
                    mime="image/png"
                )

        elif result_type == "error":
            st.error(f"Code execution error: {exec_result['data']}")

        else:
            st.markdown(exec_result.get("data", "No output produced."))

    # --- Code Tab ---
    with tab_code:
        code = result.get("code", "No code generated.")
        st.markdown("**The exact Python code used for this analysis:**")
        st.code(code, language="python", line_numbers=True)
        st.caption("💡 This code was generated by the AI Code Writer agent (Qwen3 Coder) and executed in a sandboxed environment.")

    # --- Report Tab ---
    with tab_report:
        report = result.get("report", "No report generated.")
        st.markdown(report)

    # --- Profile Tab ---
    with tab_profile:
        profile = result.get("profile", "No profile generated.")
        st.markdown(profile)
