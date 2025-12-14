from adapters.universal.selector import get_agent
from data.targets import targets

triage_agent = get_agent(adapter="langchain", tools=[])

summary_prompt = (
    "Summarize our findings from the triage phase. "
    "List top priorities and any gaps that require manual review."
)
report = triage_agent(summary_prompt)
print(report)
