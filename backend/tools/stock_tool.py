import yfinance as yf
from crewai.tools import tool


@tool("Stock Data Fetcher")
def fetch_stock_data(ticker: str) -> dict:
    """
    Fetch comprehensive live stock data for an Indian equity ticker using yfinance.
    Returns price, valuation ratios, financials, and historical trend data.
    ticker: NSE/BSE symbol e.g. HDFCBANK.NS, RELIANCE.NS, TCS.NS
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        hist_6m = stock.history(period="6mo")
        price_change_6m = 0.0
        if not hist_6m.empty and len(hist_6m) > 1:
            price_change_6m = round(
                ((hist_6m["Close"].iloc[-1] - hist_6m["Close"].iloc[0]) / hist_6m["Close"].iloc[0]) * 100, 2
            )

        avg_vol = 0
        hist_1y = stock.history(period="1y")
        if not hist_1y.empty and len(hist_1y) >= 20:
            avg_vol = int(hist_1y["Volume"].tail(20).mean())

        quarterly = {}
        try:
            qf = stock.quarterly_financials
            if not qf.empty:
                for col in qf.columns[:4]:
                    p = str(col.date()) if hasattr(col, "date") else str(col)
                    quarterly[p] = {
                        "revenue": int(qf.loc["Total Revenue", col]) if "Total Revenue" in qf.index else None,
                        "net_income": int(qf.loc["Net Income", col]) if "Net Income" in qf.index else None,
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
            "description": (info.get("longBusinessSummary", "") or "")[:400],
        }
    except Exception as exc:
        return {"error": str(exc), "ticker": ticker}
