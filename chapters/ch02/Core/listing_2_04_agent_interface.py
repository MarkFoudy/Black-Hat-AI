class Agent:
    def plan(self, history: list[Message]) -> Message:
        """Generate the next action or reasoning step."""
    return None

    def act(self, plan: Message, tools: list[Tool]) -> Observation:
        """Execute the planned action using an appropriate tool."""
    return None

    def reflect(self, observation: Observation) -> Message:
        """Update internal memory and produce a reflection message."""
    return None
