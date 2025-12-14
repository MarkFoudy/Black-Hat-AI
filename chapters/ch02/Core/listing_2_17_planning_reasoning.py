from adapters.universal.selector import get_agent
from data.targets import targets

input_text = (
    "Given these host entries, rank which are most likely "
    "to expose sensitive admin or test interfaces. "
    "Explain your reasoning briefly."
)

triage_agent = get_agent(adapter="langchain", tools=[])
result = triage_agent(f"{input_text}\n{targets}")
print(result)
