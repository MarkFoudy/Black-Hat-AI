"""
Tests for SummarizeUrlsTool (Listing 2.4).
"""

import pytest
from src.tools.summarize_urls import SummarizeUrlsTool


class TestSummarizeUrlsTool:
    """Test cases for URL summarization tool."""

    def setup_method(self):
        self.tool = SummarizeUrlsTool()

    def test_tool_name(self):
        assert self.tool.name == "summarize_urls"

    def test_summarize_single_url(self):
        result = self.tool.invoke({"urls": ["https://example.com"]})
        assert result["count"] == 1
        assert result["summary"] == "Found 1 URLs."
        assert result["urls"] == ["https://example.com"]

    def test_summarize_multiple_urls(self):
        urls = ["https://example.com", "http://test.com", "https://admin.com"]
        result = self.tool.invoke({"urls": urls})
        assert result["count"] == 3
        assert result["summary"] == "Found 3 URLs."
        assert result["urls"] == urls

    def test_summarize_no_urls(self):
        result = self.tool.invoke({"urls": []})
        assert result["count"] == 0
        assert result["summary"] == "Found 0 URLs."
        assert result["urls"] == []

    def test_missing_urls_key_raises(self):
        """Missing 'urls' key should raise ValueError, not silently default."""
        with pytest.raises(ValueError, match="'urls'"):
            self.tool.invoke({})

    def test_output_format(self):
        """Output must contain count, summary, and urls keys."""
        result = self.tool.invoke({"urls": ["https://example.com"]})
        assert "count" in result
        assert "summary" in result
        assert "urls" in result
        assert isinstance(result["count"], int)
        assert isinstance(result["summary"], str)
        assert isinstance(result["urls"], list)
