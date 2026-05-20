# FinSight AI — Multi-Agent Indian Equity Research

> AI-powered stock analysis for NSE/BSE listed companies. Type a ticker, get a full investment research report in under 2 minutes — powered by a 6-agent CrewAI pipeline.

![Tech Stack](https://img.shields.io/badge/CrewAI-6%20Agents-blue?style=flat-square)
![LLM](https://img.shields.io/badge/LLM-Llama%203.3%2070B%20%28Groq%29-orange?style=flat-square)
![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SSE-green?style=flat-square)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?style=flat-square)
![Deployed on](https://img.shields.io/badge/Deployed-HuggingFace%20Spaces%20%2B%20Vercel-yellow?style=flat-square)

---

## Live Demo

| Service | URL |
|---------|-----|
| Frontend | _Vercel URL (coming soon)_ |
| Backend API | https://urmitmahida-financial-analysis-agent.hf.space |
| API Docs | https://urmitmahida-financial-analysis-agent.hf.space/docs |

---

## What It Does

Enter any NSE or BSE ticker (e.g. `HDFCBANK.NS`, `TCS.NS`, `RELIANCE.NS`) and the system:

1. Fetches live stock data, recent news, and regulatory information
2. Runs 6 specialised AI agents in sequence
3. Streams live progress to the UI via SSE
4. Returns a structured, professional investment research report with a BUY / HOLD / SELL recommendation

---

## Agent Pipeline

```
  Live Data (yfinance + DuckDuckGo)   ← pure Python, 0 LLM calls
              │
              ▼
  ┌─────────────────────┐
  │  1. Data Analyst    │  Parses stock metrics, P/E, ROE, quarterly revenue
  └──────────┬──────────┘
             │
  ┌──────────▼──────────┐
  │  2. News Researcher │  Analyses recent news, assigns POSITIVE/NEUTRAL/NEGATIVE
  └──────────┬──────────┘
             │
  ┌──────────▼──────────┐
  │  3. Fundamental     │  Scores financials 1–10, benchmarks vs Indian sector peers
  │     Analyst         │
  └──────────┬──────────┘
             │
  ┌──────────▼──────────┐
  │  4. Regulatory      │  Checks RBI/SEBI actions, assigns LOW/MEDIUM/HIGH risk
  │     Agent           │
  └──────────┬──────────┘
             │
  ┌──────────▼──────────┐
  │  5. Risk Analyst    │  Builds full risk profile across market, fundamental,
  │                     │  regulatory, and macro dimensions
  └──────────┬──────────┘
             │
  ┌──────────▼──────────┐
  │  6. Report Writer   │  Compiles everything into a structured markdown report
  └─────────────────────┘
              │
              ▼
   BUY / ACCUMULATE / HOLD / REDUCE / SELL + 12-month target price
```

**6 LLM calls per fresh analysis.** Results are cached by ticker + date — same ticker on the same day returns instantly with 0 LLM calls.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Framer Motion |
| Backend | FastAPI, SSE (Server-Sent Events), Python 3.11 |
| Agents | CrewAI 1.9.x (sequential pipeline, no tool loops) |
| LLM | Llama 3.3 70B via Groq API (free tier) |
| Stock Data | yfinance (NSE/BSE live data) |
| News | DuckDuckGo Search API |
| RAG (optional) | FAISS over RBI circulars |
| Cache | JSON files keyed by `{TICKER}_{DATE}` |
| Frontend Hosting | Vercel |
| Backend Hosting | HuggingFace Spaces (Docker) |

---

## Project Structure

```
finsight-ai-agent/
├── backend/
│   ├── app.py               # FastAPI app — SSE endpoint, cache API, PDF export
│   ├── crew.py              # CrewAI pipeline — 6 agents, Groq LLM
│   ├── data_fetcher.py      # Pure Python data collection (0 LLM calls)
│   ├── analysis_cache.py    # JSON cache — same ticker same day = instant result
│   ├── agents/              # 6 agent definitions (tools=[] — data pre-fetched)
│   │   ├── data_analyst.py
│   │   ├── news_researcher.py
│   │   ├── fundamental.py
│   │   ├── regulatory.py
│   │   ├── risk_analyst.py
│   │   └── report_writer.py
│   ├── tools/               # stock_tool, search_tool, rbi_rag_tool
│   ├── pdf_exporter.py      # PDF generation from markdown report
│   ├── Dockerfile           # HF Spaces — port 7860
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # State machine: idle → analyzing → complete
│   │   ├── components/      # Header, HeroSection, AnalysisForm, ProgressStepper,
│   │   │                    # ReportViewer, DownloadPanel, Footer
│   │   └── hooks/
│   │       └── useAnalysis.js  # SSE client, fromCache state
│   └── package.json
├── .github/
│   └── workflows/
│       └── deploy-hf-spaces.yml  # Auto-deploys backend to HF Spaces on push
└── README.md
```

---

## Running Locally

### Prerequisites
- Python 3.11+ with `crewai>=1.9.0` installed
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

### 1. Clone and configure
```bash
git clone https://github.com/urmitmahida34/finsight-ai-agent.git
cd finsight-ai-agent

# Create .env in the project root
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

### 2. Start the backend
```bash
cd backend/
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 3. Start the frontend
```bash
cd frontend/
npm install

# Create frontend/.env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
# Opens at http://localhost:5173
```

---

## Environment Variables

### Backend (`.env` in project root)
```env
GROQ_API_KEY=gsk_...       # Required — get from console.groq.com
LLM_PROVIDER=groq          # groq or gemini
HF_TOKEN=hf_...            # Only needed for HuggingFace deployment
```

### Frontend (`frontend/.env.local`)
```env
VITE_API_URL=http://localhost:8000   # local dev
# VITE_API_URL=https://urmitmahida-financial-analysis-agent.hf.space  # production
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/analyze?ticker=&company=` | SSE stream — runs full analysis |
| `GET` | `/api/cache` | List all cached analyses |
| `DELETE` | `/api/cache?ticker=` | Clear cache for a ticker (or all) |
| `POST` | `/api/report/pdf` | Generate PDF from a report |

### SSE Event Flow
```
started → fetching → progress (×6) → complete
```

---

## Key Design Decisions

**Why no tools on agents?**
CrewAI agents with tools run a ReAct loop (reason → tool → observe → reason) — roughly 5 LLM calls per agent × 6 agents = ~30–40 calls per analysis. Instead, all data is fetched upfront in pure Python (`data_fetcher.py`), then passed directly into each agent's task description. Result: exactly 6 LLM calls per analysis.

**Why Groq instead of OpenAI/Gemini?**
Groq's free tier offers `llama-3.3-70b-versatile` at 1,000 requests/day and 500K tokens/day — enough for a portfolio demo without a credit card. Gemini's free tier ran out during development.

**Why SSE instead of WebSockets?**
SSE is unidirectional (server → client), simpler to implement, and works perfectly for streaming progress updates. No bidirectional communication needed.

---

## Optional: RBI Circular RAG

The Regulatory Agent can search a local FAISS index of RBI circulars for more accurate compliance checks. To enable:

1. Download PDF circulars from [rbi.org.in](https://rbi.org.in)
2. Place them in `backend/data/rbi_circulars/`
3. Restart the backend — it will auto-index on startup

Without PDFs, the agent falls back to DuckDuckGo regulatory news search.

---

## Deployment

The project auto-deploys via GitHub Actions:
- **Backend**: Push to `main` → GitHub Actions syncs `backend/` to HuggingFace Spaces → Docker rebuild
- **Frontend**: Connect repo to Vercel → set root to `frontend/` → auto-deploys on push

---

## License

MIT
