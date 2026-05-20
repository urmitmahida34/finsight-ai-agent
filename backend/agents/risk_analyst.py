from crewai import Agent


def RiskAnalystAgent(llm) -> Agent:
    return Agent(
        role="Investment Risk Analyst",
        goal=(
            "Synthesise all prior analysis into a comprehensive risk profile. "
            "Evaluate market risk (beta), fundamental risk, regulatory risk, liquidity risk, "
            "and macro/sector risk. Output Overall Risk: LOW / MODERATE / HIGH / VERY HIGH."
        ),
        backstory=(
            "Risk management professional from a top Indian AMC. Has witnessed the Yes Bank "
            "collapse, IL&FS crisis, COVID crash, and multiple rate cycles. Identifies hidden risks "
            "others miss: concentration, management quality, regulatory pipeline, and sector rotation."
        ),
        tools=[],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )
