"""
Tests for ExtractUrlsTool (Listing 2.3).
"""

import pytest
from src.tools.extract_urls import ExtractUrlsTool


class TestExtractUrlsTool:
    """Test cases for URL extraction tool."""

    def setup_method(self):
        self.tool = ExtractUrlsTool()

    def test_tool_name(self):
        assert self.tool.name == "extract_urls"

    def test_extract_single_url(self):
        result = self.tool.invoke({"text": "Visit https://example.com"})
        assert result == {"urls": ["https://example.com"]}

    def test_extract_multiple_urls(self):
        text = "Check https://example.com and http://test.com"
        result = self.tool.invoke({"text": text})
        assert len(result["urls"]) == 2
        assert "https://example.com" in result["urls"]
        assert "http://test.com" in result["urls"]

    def test_extract_no_urls(self):
        result = self.tool.invoke({"text": "No URLs here"})
        assert result == {"urls": []}

    def test_extract_empty_text(self):
        result = self.tool.invoke({"text": ""})
        assert result == {"urls": []}

    def test_missing_text_key_raises(self):
        """Missing 'text' key should raise ValueError, not silently default."""
        with pytest.raises(ValueError, match="'text'"):
            self.tool.invoke({})

    def test_extract_urls_with_paths(self):
        text = "Login at https://admin.example.com/login"
        result = self.tool.invoke({"text": text})
        assert result["urls"] == ["https://admin.example.com/login"]

    def test_extract_urls_with_query_params(self):
        text = "Search https://example.com/search?q=test"
        result = self.tool.invoke({"text": text})
        assert "https://example.com/search?q=test" in result["urls"]

    def test_trailing_punctuation_excluded(self):
        """Regex should not capture trailing commas, parens, or brackets."""
        text = "See (https://example.com) and [https://test.com], done."
        result = self.tool.invoke({"text": text})
        assert "https://example.com" in result["urls"]
        assert "https://test.com" in result["urls"]
        # Parens and brackets must not be part of captured URLs
        for url in result["urls"]:
            assert not url.endswith(")")
            assert not url.endswith("]")
            assert not url.endswith(",")
