#!/usr/bin/env python3
"""
Minimal Agent Example

From Listing 2.7 in Black Hat AI Chapter 2.

Run from the ch02 directory:
    python scripts/example_01_minimal_agent.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.logger import ArtifactLogger
from src.core.agent import MinimalAgent
from src.tools.extract_urls import ExtractUrlsTool
from src.tools.summarize_urls import SummarizeUrlsTool

with ArtifactLogger() as logger:
    agent = MinimalAgent(
        tools=[ExtractUrlsTool(), SummarizeUrlsTool()],
        logger=logger,
    )
    result = agent.run(
        "Check https://example.com and "
        "https://admin.example.com/login"
    )
    print(result)
