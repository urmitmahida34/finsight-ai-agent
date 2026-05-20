from crewai import Agent


def DataAnalystAgent(llm) -> Agent:
    return Agent(
        role="Senior Financial Data Analyst",
        goal=(
            "Analyse pre-fetched live stock data and produce a clean, structured financial summary "
            "with actual numbers that downstream agents can rely on."
        ),
        backstory=(
            "Quantitative analyst with 10 years at a top Indian brokerage. "
            "Expert in NSE/BSE data — knows how to interpret yfinance output for Indian equities "
            "and which metrics matter for banking vs IT vs FMCG sectors."
        ),
        tools=[],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )
