# adapters/autogen/agent.py
from autogen import AssistantAgent, UserProxyAgent
from core.logger import ArtifactLogger
from mytools import ping_host

def build_autogen_agent():
    logger = ArtifactLogger()
    assistant = AssistantAgent("triage", llm_config={"temperature":0.2})
    user = UserProxyAgent("operator", code_execution_config=False)

    assistant.register_function(ping_host)

    def run(prompt: str):
        result = assistant.initiate_chat(user, message=prompt)
        logger.write({"input": prompt, "output": str(result)})
        return result

    return run

if __name__ == "__main__":
    agent_run = build_autogen_agent()
    agent_run("Check reachability of example.com")
