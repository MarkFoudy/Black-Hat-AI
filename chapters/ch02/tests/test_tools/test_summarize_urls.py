"""
Tests for SummarizeUrlsTool.

From Listing 2.4 in Black Hat AI Chapter 2.
"""

import pytest
from src.tools.summarize_urls import SummarizeUrlsTool


class TestSummarizeUrlsTool:
    """Test cases for URL summarization tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = SummarizeUrlsTool()

    def test_tool_name(self):
        """Verify tool has correct name."""
        assert self.tool.name == "summarize_urls"

    def test_summarize_single_url(self):
        """Test summarization of a single URL."""
        result = self.tool.invoke({"urls": ["https://example.com"]})
        assert result["count"] == 1
        assert result["summary"] == "Found 1 URLs."

    def test_summarize_multiple_urls(self):
        """Test summarization of multiple URLs."""
        urls = ["https://example.com", "http://test.com", "https://admin.com"]
        result = self.tool.invoke({"urls": urls})
        assert result["count"] == 3
        assert result["summary"] == "Found 3 URLs."

    def test_summarize_no_urls(self):
        """Test summarization of empty URL list."""
        result = self.tool.invoke({"urls": []})
        assert result["count"] == 0
        assert result["summary"] == "Found 0 URLs."

    def test_summarize_missing_urls_key(self):
        """Test handling of missing urls key."""
        result = self.tool.invoke({})
        assert result["count"] == 0
        assert result["summary"] == "Found 0 URLs."

    def test_output_format(self):
        """Test that output has correct keys."""
        result = self.tool.invoke({"urls": ["https://example.com"]})
        assert "count" in result
        assert "summary" in result
        assert isinstance(result["count"], int)
        assert isinstance(result["summary"], str)
