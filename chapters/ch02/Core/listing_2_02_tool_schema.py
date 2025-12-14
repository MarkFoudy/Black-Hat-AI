from typing import Dict, Any

class Tool:
    name: str
    description: str

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Run the tool and return structured output."""
        raise NotImplementedError

