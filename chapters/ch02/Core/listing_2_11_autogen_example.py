from autogen import AssistantAgent, UserProxyAgent
from mytools import ping_host

assistant = AssistantAgent(name="triage", llm_config={"temperature":0.2})
user = UserProxyAgent("operator", code_execution_config=False)
assistant.register_function(ping_host)
assistant.initiate_chat(user, message="Check reachability of example.com")
