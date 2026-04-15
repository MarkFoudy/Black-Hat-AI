#!/usr/bin/env python3
"""
Exercise 2.1 starter — write a simple Tool subclass.

Chapter exercise:
    "Write a simple Tool subclass that performs a harmless text operation
     (e.g., word counting, reversing a string, converting to uppercase).
     Log the input and output using ArtifactLogger."

Fill in the TODO sections below to complete the exercise.

Run from the ch02 directory:
    python scripts/exercise_2_1_starter.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typing import Dict, Any
from src.core.tool import Tool
from src.core.logger import ArtifactLogger


# ---------------------------------------------------------------------------
# TODO: implement your tool
# ---------------------------------------------------------------------------

class WordCountTool(Tool):
    """Count words in a piece of text."""

    def __init__(self) -> None:
        super().__init__(
            name="word_count",
            description="Counts the number of words in the provided text",
        )

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        text = input.get("text")
        if text is None:
            raise ValueError("WordCountTool requires a 'text' key in input")
        # TODO: add more interesting analysis here
        words = text.split()
        return {"word_count": len(words), "text": text}


# ---------------------------------------------------------------------------
# Main: wire the tool into ArtifactLogger
# ---------------------------------------------------------------------------

def main():
    tool = WordCountTool()

    with ArtifactLogger() as logger:
        sample_input = {"text": "Black Hat AI teaches offensive security with LLMs."}
        result = tool.invoke(sample_input)

        logger.write({
            "tool": tool.name,
            "input": sample_input,
            "output": result,
        })

        print(f"Input : {sample_input['text']}")
        print(f"Output: {result}")
        print(f"Log   : {logger.path}")


if __name__ == "__main__":
    main()
