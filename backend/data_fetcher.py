"""
Pure Python data collection — zero LLM calls.
Fetches stock data, news, and regulatory info before CrewAI agents run.
"""
import json
import time

import yfinance as yf
from ddgs import DDGS


def _indian_fy_quarter(ts) -> str:
    """Convert a quarter-end timestamp to Indian FY label, e.g. 'Q1 FY2026 (Apr-Jun 2025)'."""
    m, y = ts.month, ts.year
    if m >= 4:
        fy = y + 1
        q = (m - 4) // 3 + 1
    else:
        fy = y
        q = 4
    month_ranges = {1: "Q1 (Apr-Jun)", 2: "Q2 (Jul-Sep)", 3: "Q3 (Oct-Dec)", 4: "Q4 (Jan-Mar)"}
    return f"{month_ranges[q]} FY{fy}"


def _to_crore(value) -> float | None:
    """Convert raw INR value to Crores (1 Crore = 10,000,000)."""
    if value is None:
        return None
    return round(value / 10_000_000, 2)


def fetch_stock_data(ticker: str) -> dict:
    """Fetch live stock data from NSE/BSE via yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        hist_6m = stock.history(period="6mo")
        price_change_6m = 0.0
        if not hist_6m.empty and len(hist_6m) > 1:
            price_change_6m = round(
                ((hist_6m["Close"].iloc[-1] - hist_6m["Close"].iloc[0])
                 / hist_6m["Close"].iloc[0]) * 100, 2
            )

        hist_1y = stock.history(period="1y")
        avg_vol = 0
        if not hist_1y.empty and len(hist_1y) >= 20:
            avg_vol = int(hist_1y["Volume"].tail(20).mean())

        quarterly = {}
        try:
            # Prefer quarterly_income_stmt (newer API), fall back to quarterly_financials
            qf = stock.quarterly_income_stmt
            if qf is None or qf.empty:
                qf = stock.quarterly_financials
            if not qf.empty:
                for col in qf.columns[:4]:
                    label = _indian_fy_quarter(col) if hasattr(col, "month") else str(col)
                    rev_raw = qf.loc["Total Revenue", col] if "Total Revenue" in qf.index else None
                    ni_raw = qf.loc["Net Income", col] if "Net Income" in qf.index else None
                    quarterly[label] = {
                        "revenue_crore": _to_crore(rev_raw),
                        "net_income_crore": _to_crore(ni_raw),
                    }
        except Exception:
            pass

        return {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
            "currency": info.get("currency", "INR"),
            "week_52_high": info.get("fiftyTwoWeekHigh", 0),
            "week_52_low": info.get("fiftyTwoWeekLow", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "eps": info.get("trailingEps"),
            "book_value": info.get("bookValue"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "profit_margins": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "price_change_6m_pct": price_change_6m,
            "avg_volume_20d": avg_vol,
            "quarterly_financials": quarterly,
            "analyst_target_price": info.get("targetMeanPrice"),
            "recommendation": info.get("recommendationKey"),
            "analyst_count": info.get("numberOfAnalystOpinions"),
            "description": (info.get("longBusinessSummary") or "")[:400],
        }
    except Exception as exc:
        return {"error": str(exc), "ticker": ticker}


def fetch_news(company: str, ticker: str) -> str:
    """Fetch recent financial news via DuckDuckGo — no LLM."""
    queries = [
        f"{company} quarterly results earnings 2025 2026",
        f"{company} stock outlook analyst target",
        f"{company} business strategy news",
    ]
    articles = []
    for query in queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=4))
            for r in results:
                date = r.get("date", "")
                title = r.get("title", "")
                body = r.get("body", r.get("snippet", ""))[:300]
                source = r.get("source", "")
                articles.append(f"[{date}] {title} ({source})\n{body}")
            time.sleep(0.5)
        except Exception:
            pass

    return "\n\n---\n\n".join(articles) if articles else "No recent news found."


def fetch_regulatory(company: str) -> str:
    """Fetch RBI/SEBI regulatory data — FAISS index + DuckDuckGo."""
    sections = []

    # FAISS RAG on local RBI circulars (if indexed)
    try:
        from tools.rbi_rag_tool import _load_index, _embed, _index, _chunks
        import numpy as np

        if _load_index():
            q_vec = _embed(f"RBI action penalty {company}").reshape(1, -1)
            distances, indices = _index.search(q_vec, k=3)
            hits = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and dist > 0.05:
                    hits.append(f"[{_chunks[idx]['source']}] {_chunks[idx]['text'][:300]}")
            if hits:
                sections.append("RBI CIRCULAR DATABASE:\n" + "\n\n".join(hits))
    except Exception:
        pass

    if not sections:
        sections.append("RBI circular index not available — using news-based regulatory check.")

    # Recent regulatory news
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(
                f"{company} RBI SEBI penalty notice regulatory 2025 2026",
                max_results=5
            ))
        if results:
            news_lines = []
            for r in results:
                news_lines.append(
                    f"[{r.get('date','')}] {r.get('title','')}\n{r.get('body','')[:250]}"
                )
            sections.append("REGULATORY NEWS:\n" + "\n\n".join(news_lines))
    except Exception:
        sections.append("REGULATORY NEWS: Could not fetch regulatory news.")

    return "\n\n".join(sections)
