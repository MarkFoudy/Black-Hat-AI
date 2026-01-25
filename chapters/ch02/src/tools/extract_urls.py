"""
URL extraction tool.

From Listing 2.3 in Black Hat AI Chapter 2.

This tool demonstrates the minimal tool pattern by extracting URLs from text
using regex without any external dependencies.
"""

import re
from typing import Dict, Any

from src.core.tool import Tool


class ExtractUrlsTool(Tool):
    """Extract URLs from text using regex."""

    name = "extract_urls"
    description = "Extracts HTTP/HTTPS URLs from text input"

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract URLs from the provided text.

        Args:
            input: Dictionary with "text" key containing the input text

        Returns:
            Dictionary with "urls" key containing list of extracted URLs

        Example:
            >>> tool = ExtractUrlsTool()
            >>> result = tool.invoke({"text": "Visit https://example.com"})
            >>> result["urls"]
            ['https://example.com']
        """
        text = input.get("text", "")
        urls = re.findall(r"https?://[^\s]+", text)
        return {"urls": urls}
