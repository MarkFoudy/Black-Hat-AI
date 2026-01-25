"""
Tests for ExtractUrlsTool.

From Listing 2.3 in Black Hat AI Chapter 2.
"""

import pytest
from src.tools.extract_urls import ExtractUrlsTool


class TestExtractUrlsTool:
    """Test cases for URL extraction tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = ExtractUrlsTool()

    def test_tool_name(self):
        """Verify tool has correct name."""
        assert self.tool.name == "extract_urls"

    def test_extract_single_url(self):
        """Test extraction of a single URL."""
        result = self.tool.invoke({"text": "Visit https://example.com"})
        assert result == {"urls": ["https://example.com"]}

    def test_extract_multiple_urls(self):
        """Test extraction of multiple URLs."""
        text = "Check https://example.com and http://test.com"
        result = self.tool.invoke({"text": text})
        assert len(result["urls"]) == 2
        assert "https://example.com" in result["urls"]
        assert "http://test.com" in result["urls"]

    def test_extract_no_urls(self):
        """Test handling of text with no URLs."""
        result = self.tool.invoke({"text": "No URLs here"})
        assert result == {"urls": []}

    def test_extract_empty_text(self):
        """Test handling of empty text."""
        result = self.tool.invoke({"text": ""})
        assert result == {"urls": []}

    def test_extract_missing_text_key(self):
        """Test handling of missing text key."""
        result = self.tool.invoke({})
        assert result == {"urls": []}

    def test_extract_urls_with_paths(self):
        """Test extraction of URLs with paths."""
        text = "Login at https://admin.example.com/login"
        result = self.tool.invoke({"text": text})
        assert result["urls"] == ["https://admin.example.com/login"]

    def test_extract_urls_with_query_params(self):
        """Test extraction of URLs with query parameters."""
        text = "Search https://example.com/search?q=test"
        result = self.tool.invoke({"text": text})
        assert "https://example.com/search?q=test" in result["urls"]
