import json
import os
from typing import Callable, Optional

from crewai import Crew, LLM, Process, Task

from agents.data_analyst import DataAnalystAgent
from agents.fundamental import FundamentalAnalystAgent
from agents.news_researcher import NewsResearcherAgent
from agents.regulatory import RegulatoryAgent
from agents.report_writer import ReportWriterAgent
from agents.risk_analyst import RiskAnalystAgent
from analysis_cache import get_cached, save_cache
from data_fetcher import fetch_news, fetch_regulatory, fetch_stock_data

STEP_NAMES = [
    "Data Analyst",
    "News Researcher",
    "Fundamental Analyst",
    "Regulatory Agent",
    "Risk Analyst",
    "Report Writer",
]


def build_llm() -> LLM:
    provider = os.environ.get("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        return LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=os.environ.get("GROQ_API_KEY", ""),
            temperature=0.3,
        )
    elif provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "")
        os.environ["GEMINI_API_KEY"] = api_key
        return LLM(
            model="gemini/gemini-2.0-flash",
            api_key=api_key,
            temperature=0.3,
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'groq' or 'gemini'.")


def run_analysis_sync(
    ticker: str,
    company: str,
    progress_callback: Optional[Callable] = None,
) -> dict:

    # ── Step 0: Cache check ──────────────────────────────────────────────────
    cached_report = get_cached(ticker)
    if cached_report:
        if progress_callback:
            for i in range(len(STEP_NAMES)):
                progress_callback({
                    "type": "progress",
                    "step": i,
                    "agent": STEP_NAMES[i],
                    "status": "complete",
                    "from_cache": True,
                })
        return {"status": "success", "report": cached_report, "from_cache": True}

    # ── Step 1: Pure Python data collection (0 LLM calls) ───────────────────
    if progress_callback:
        progress_callback({"type": "fetching", "message": "Fetching live market data..."})

    stock_data = fetch_stock_data(ticker)
    news_text = fetch_news(company, ticker)
    regulatory_text = fetch_regulatory(company)

    stock_json = json.dumps(stock_data, indent=2, default=str)

    # ── Step 2: CrewAI agents (no tools → 1 LLM call each) ──────────────────
    llm = build_llm()

    data_agent = DataAnalystAgent(llm)
    news_agent = NewsResearcherAgent(llm)
    fundamental_agent = FundamentalAnalystAgent(llm)
    regulatory_agent = RegulatoryAgent(llm)
    risk_agent = RiskAnalystAgent(llm)
    report_agent = ReportWriterAgent(llm)

    step_counter = {"n": 0}

    def on_task_done(_):
        idx = step_counter["n"]
        step_counter["n"] += 1
        if progress_callback and idx < len(STEP_NAMES):
            progress_callback({
                "type": "progress",
                "step": idx,
                "agent": STEP_NAMES[idx],
                "status": "complete",
            })

    # Task 1 — Data Analyst (receives pre-fetched data, no tool calls needed)
    task_data = Task(
        description=(
            f"You have been given pre-fetched live stock data for {ticker}.\n\n"
            f"STOCK DATA (JSON):\n{stock_json}\n\n"
            f"Produce a concise structured financial summary covering:\n"
            f"- Current price, 52-week range, market cap\n"
            f"- Key ratios: P/E, P/B, ROE, EPS, dividend yield, beta\n"
            f"- Quarterly revenue and net profit trend (last 4 quarters)\n"
            f"- 6-month price change: {stock_data.get('price_change_6m_pct', 'N/A')}%\n"
            f"IMPORTANT: Revenue and net income in quarterly_financials are already in Crores "
            f"(fields: revenue_crore, net_income_crore). Copy those values directly — do NOT "
            f"re-convert. Use the provided quarter labels exactly (e.g. 'Q1 FY2026 (Apr-Jun)'). "
            f"Flag any missing or unusual data."
        ),
        expected_output=(
            "Structured financial summary with all key metrics, actual numbers, "
            "and a brief note on data quality."
        ),
        agent=data_agent,
    )

    # Task 2 — News Researcher (receives pre-fetched news, no searches needed)
    task_news = Task(
        description=(
            f"You have been given pre-fetched news articles for {company} ({ticker}).\n\n"
            f"NEWS DATA:\n{news_text}\n\n"
            f"Analyse this news and produce:\n"
            f"- 5-6 bullet points of the most important recent developments\n"
            f"- Overall News Sentiment: POSITIVE / NEUTRAL / NEGATIVE\n"
            f"- 2-sentence justification for the sentiment rating"
        ),
        expected_output=(
            "5-6 key news bullet points with dates. "
            "Overall News Sentiment: POSITIVE/NEUTRAL/NEGATIVE with justification."
        ),
        agent=news_agent,
    )

    # Task 3 — Fundamental Analyst (uses Data Analyst output as context)
    task_fundamental = Task(
        description=(
            f"Perform fundamental analysis for {company} ({ticker}) "
            f"using the financial data from the Data Analyst.\n\n"
            f"Evaluate:\n"
            f"1. Profitability — ROE vs 15% benchmark, profit margins, earnings trend\n"
            f"2. Valuation — P/E and P/B vs Indian sector average\n"
            f"3. Financial health — debt levels, balance sheet strength\n"
            f"4. If banking stock — NPA (below 2% = healthy), CASA ratio, NIM, CAR\n\n"
            f"Benchmark against Indian peers, not global standards.\n"
            f"Score fundamentals 1-10. List top 3 strengths and top 3 concerns."
        ),
        expected_output=(
            "Fundamental analysis with specific ratios vs benchmarks. "
            "Fundamental Score: X/10. Top 3 Strengths. Top 3 Concerns."
        ),
        agent=fundamental_agent,
        context=[task_data],
    )

    # Task 4 — Regulatory Agent (receives pre-fetched regulatory data)
    task_regulatory = Task(
        description=(
            f"Assess regulatory and compliance status for {company} ({ticker}).\n\n"
            f"PRE-FETCHED REGULATORY DATA:\n{regulatory_text}\n\n"
            f"Based on this data:\n"
            f"1. Identify any RBI or SEBI penalties, restrictions, or investigations\n"
            f"2. Note relevant regulatory circulars affecting this company\n"
            f"3. Assess: Regulatory Risk: LOW / MEDIUM / HIGH"
        ),
        expected_output=(
            "Regulatory status: key findings from the data above. "
            "Regulatory Risk: LOW/MEDIUM/HIGH with brief justification."
        ),
        agent=regulatory_agent,
    )

    # Task 5 — Risk Analyst (uses all prior outputs as context)
    task_risk = Task(
        description=(
            f"Build a risk profile for {company} ({ticker}) from all prior analysis.\n\n"
            f"Evaluate:\n"
            f"1. Market risk — use beta from the financial data (>1.2 = high)\n"
            f"2. Fundamental risk — from the fundamental analysis\n"
            f"3. Regulatory risk — from the regulatory assessment\n"
            f"4. Macro/sector risk — rate environment, sector headwinds from news\n\n"
            f"Output Overall Risk Level: LOW / MODERATE / HIGH / VERY HIGH.\n"
            f"List top 3 specific risk factors to watch."
        ),
        expected_output=(
            "Risk profile covering all 4 dimensions. "
            "Overall Risk Level: LOW/MODERATE/HIGH/VERY HIGH. "
            "Top 3 risk factors."
        ),
        agent=risk_agent,
        context=[task_data, task_fundamental, task_regulatory],
    )

    # Task 6 — Report Writer (compiles everything)
    task_report = Task(
        description=(
            f"Write the final investment research report for {company} ({ticker}).\n\n"
            f"Use outputs from ALL previous agents. Structure the report as:\n\n"
            f"## Executive Summary\n"
            f"## Financial Snapshot\n"
            f"## News Sentiment\n"
            f"## Fundamental Analysis\n"
            f"## Regulatory Status\n"
            f"## Risk Profile\n"
            f"## Recommendation\n\n"
            f"Use Indian number format (Crores, Lakhs). Cite specific numbers.\n"
            f"End with: BUY / ACCUMULATE / HOLD / REDUCE / SELL rating "
            f"and a 12-month target price in INR."
        ),
        expected_output=(
            "Complete investment research report in markdown. "
            "All 7 sections present. Clear BUY/HOLD/SELL with target price."
        ),
        agent=report_agent,
        context=[task_data, task_news, task_fundamental, task_regulatory, task_risk],
    )

    crew = Crew(
        agents=[data_agent, news_agent, fundamental_agent, regulatory_agent, risk_agent, report_agent],
        tasks=[task_data, task_news, task_fundamental, task_regulatory, task_risk, task_report],
        process=Process.sequential,
        task_callback=on_task_done,
        verbose=False,
    )

    try:
        result = crew.kickoff()
        report = str(result)
        save_cache(ticker, report, company)
        return {"status": "success", "report": report, "from_cache": False}
    except Exception as exc:
        return {"status": "error", "report": f"Analysis failed: {exc}"}
