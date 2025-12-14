from adapters.langchain.agent import build_langchain_agent
from adapters.autogen.agent import build_autogen_agent

def get_agent(adapter="langchain", tools=None):
    if adapter == "autogen":
        return build_autogen_agent()
    return build_langchain_agent(tools or [])
