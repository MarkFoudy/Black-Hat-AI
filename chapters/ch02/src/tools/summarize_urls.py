"""
URL summarization tool.

From Listing 2.4 in Black Hat AI Chapter 2.

This tool demonstrates the minimal tool pattern by summarizing extracted URLs
without any external dependencies.
"""

from typing import Dict, Any

from src.core.tool import Tool


class SummarizeUrlsTool(Tool):
    """Summarize extracted URLs."""

    name = "summarize_urls"
    description = "Generates a summary of extracted URLs"

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the extracted URLs.

        Args:
            input: Dictionary with "urls" key containing list of URLs

        Returns:
            Dictionary with "count" and "summary" keys

        Example:
            >>> tool = SummarizeUrlsTool()
            >>> result = tool.invoke({"urls": ["https://example.com", "https://test.com"]})
            >>> result["count"]
            2
            >>> result["summary"]
            'Found 2 URLs.'
        """
        urls = input.get("urls", [])
        count = len(urls)
        return {
            "count": count,
            "summary": f"Found {count} URLs."
        }
