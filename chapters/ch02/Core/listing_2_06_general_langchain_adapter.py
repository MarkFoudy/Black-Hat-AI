from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.tools import Tool
from core.logger import ArtifactLogger

def build_langchain_agent(tools: list[Tool]):

    llm = OpenAI(temperature=0.2)
    memory = ConversationBufferMemory(memory_key="chat_history")

    agent = initialize_agent(
        tools,
        llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )

    logger = ArtifactLogger()

    def run(input_text):
        result = agent.run(input_text)
        logger.write({"input": input_text, "output": result})
        return result

    return run
