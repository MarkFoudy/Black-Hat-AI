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

    def __init__(self) -> None:
        super().__init__(
            name="summarize_urls",
            description="Generates a summary of extracted URLs",
        )

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the extracted URLs.

        Args:
            input: Dictionary with "urls" key containing list of URLs

        Returns:
            Dictionary with "count", "summary", and "urls" keys

        Raises:
            ValueError: If "urls" key is missing from input

        Example:
            >>> tool = SummarizeUrlsTool()
            >>> result = tool.invoke({"urls": ["https://example.com"]})
            >>> result["count"]
            1
            >>> result["summary"]
            'Found 1 URL(s).'
        """
        urls = input.get("urls")
        if urls is None:
            raise ValueError("SummarizeUrlsTool requires a 'urls' key in input")
        return {
            "count": len(urls),
            "summary": f"Found {len(urls)} URL(s).",
            "urls": urls,
        }
