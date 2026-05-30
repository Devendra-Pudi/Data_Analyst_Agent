# 🧠 AI Data Analyst Agent

An agentic AI Data Analyst powered by **CrewAI** and **OpenRouter free models**. Upload your data, ask questions in natural language, and get actionable insights with charts, tables, and detailed reports — all with full transparency showing the exact Python code behind every result.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-data-analyst-by-devendra.streamlit.app/)

---

## ✨ Features

- 📁 **Multi-format Upload** — CSV, Excel (.xlsx/.xls), and JSON
- 🤖 **4 Specialized AI Agents** — each powered by a different free LLM optimized for its role
- 📊 **Auto-generated Charts** — matplotlib & seaborn visualizations
- 💻 **Show Your Work** — every result displays the exact Python code used
- 📝 **Narrative Reports** — AI-generated insights with key findings
- 🎯 **Smart Suggestions** — auto-generated analysis prompts based on your data
- 🎨 **Premium Dark UI** — glassmorphism, gradient accents, smooth animations
- 🐳 **Dockerized** — one-command deployment
- ☁️ **Streamlit Cloud** — free cloud deployment ready

---

## 🤖 Agent Architecture

| Agent | Model | Role |
|-------|-------|------|
| 🔍 **Data Profiler** | Arcee-AI Trinity Large Thinking | Analyzes dataset schema, types, statistics |
| 📊 **Analyst** | NVIDIA Nemotron 3 Super 120B | Plans analysis strategy from your question |
| 💻 **Code Writer** | Poolside Laguna M.1 | Writes Python code for the analysis |
| 📝 **Reporter** | OpenAI GPT-OSS 120B | Creates narrative reports with insights |

All models are **completely free** via OpenRouter (no credit card required).

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Devendra-Pudi/Data_Analyst_Agent.git
cd Data_Analyst_Agent

# Create .env file with your OpenRouter API key
cp .env.example .env
# Edit .env and add your key from https://openrouter.ai

# Build and run
docker compose up --build
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Option 2: Manual Setup

```bash
# Clone and enter directory
git clone https://github.com/Devendra-Pudi/Data_Analyst_Agent.git
cd Data_Analyst_Agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OpenRouter API key

# Run the app
streamlit run app.py
```

### Option 3: Streamlit Cloud

The app is deployed at: **[ai-data-analyst-by-devendra.streamlit.app](https://ai-data-analyst-by-devendra.streamlit.app/)**

---

## 🔑 Getting an OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai)
2. Create a free account (no credit card required)
3. Go to **Keys** → **Create Key**
4. Copy the key and paste it in the app sidebar or `.env` file

---

## 📁 Project Structure

```
AI_Data_Analyst/
├── app.py                    # Main Streamlit application
├── style.css                 # Custom premium CSS
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker container
├── docker-compose.yml        # Docker Compose
├── agents/
│   ├── config.py             # Model ID mappings
│   ├── profiler.py           # Data Profiler (Trinity Large Thinking)
│   ├── analyst.py            # Analyst (Nemotron 3 Super)
│   ├── coder.py              # Code Writer (Poolside Laguna M.1)
│   ├── reporter.py           # Reporter (GPT-OSS 120B)
│   └── crew.py               # CrewAI orchestrator
├── engine/
│   ├── executor.py           # Safe code executor
│   └── data_loader.py        # File loader
├── utils/
│   ├── suggestions.py        # Smart prompt generator
│   └── helpers.py            # Shared utilities
└── sample_data/
    └── sales_data.csv        # Demo dataset
```

---

## 🛡️ Security

The code executor runs AI-generated Python in a restricted namespace with:
- Limited imports (pandas, numpy, matplotlib, seaborn only)
- 30-second timeout
- Docker container isolation (when using Docker)

> ⚠️ This is designed as a **personal tool**. Do not deploy publicly without additional sandboxing.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
