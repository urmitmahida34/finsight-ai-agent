from crewai import Agent


def NewsResearcherAgent(llm) -> Agent:
    return Agent(
        role="Financial News & Sentiment Analyst",
        goal=(
            "Analyse pre-fetched news articles about the company. Summarise key developments "
            "and assign an overall sentiment: POSITIVE / NEUTRAL / NEGATIVE."
        ),
        backstory=(
            "Ex-Bloomberg journalist turned equity analyst. Scans dozens of sources rapidly, "
            "separates signal from noise, and distils market-moving information into actionable summaries. "
            "Always focuses on the most recent 3–6 months of news."
        ),
        tools=[],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )
