"""
Tests for src/safety/scope.py (Section 4.6)
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.safety.scope import (
    ScopeConfig,
    ScopeChecker,
    load_scope,
    load_scope_safe,
    save_scope,
    create_scope_checker,
)


class TestScopeConfig:
    """Tests for the ScopeConfig dataclass."""

    def test_scope_config_defaults(self):
        """Test ScopeConfig with default values."""
        config = ScopeConfig()
        assert config.allowed == []
        assert config.forbidden == []

    def test_scope_config_with_values(self, sample_scope):
        """Test ScopeConfig with provided values."""
        assert "example.com" in sample_scope.allowed
        assert "prod.example.com" in sample_scope.forbidden

    def test_scope_config_to_dict(self, sample_scope):
        """Test ScopeConfig.to_dict() conversion."""
        d = sample_scope.to_dict()
        assert "allowed" in d
        assert "forbidden" in d

    def test_scope_config_from_dict(self):
        """Test ScopeConfig.from_dict() creation."""
        data = {
            "allowed": ["test.com"],
            "forbidden": ["prod.test.com"],
        }
        config = ScopeConfig.from_dict(data)
        assert config.allowed == ["test.com"]
        assert config.forbidden == ["prod.test.com"]


class TestScopeChecker:
    """Tests for the ScopeChecker class."""

    def test_is_allowed_exact_match(self, sample_scope_checker):
        """Test exact domain match."""
        allowed, _ = sample_scope_checker.is_allowed("example.com")
        assert allowed is True

    def test_is_allowed_wildcard_match(self, sample_scope_checker):
        """Test wildcard subdomain match."""
        allowed, _ = sample_scope_checker.is_allowed("api.example.com")
        assert allowed is True

    def test_is_forbidden_takes_precedence(self, sample_scope_checker):
        """Test forbidden patterns override allowed."""
        allowed, reason = sample_scope_checker.is_allowed("prod.example.com")
        assert allowed is False
        assert "forbidden" in reason

    def test_is_allowed_not_in_list(self, sample_scope_checker):
        """Test host not matching any pattern."""
        allowed, reason = sample_scope_checker.is_allowed("other-domain.com")
        assert allowed is False
        assert "does not match" in reason

    def test_is_allowed_case_insensitive(self, sample_scope_checker):
        """Test case-insensitive matching."""
        allowed, _ = sample_scope_checker.is_allowed("EXAMPLE.COM")
        assert allowed is True

    def test_is_allowed_empty_allowed_list(self):
        """Test behavior with empty allowed list."""
        config = ScopeConfig(allowed=[], forbidden=["bad.com"])
        checker = ScopeChecker(config)

        # Everything except forbidden should be allowed
        allowed, _ = checker.is_allowed("anything.com")
        assert allowed is True

        allowed, _ = checker.is_allowed("bad.com")
        assert allowed is False

    def test_filter_hosts(self, sample_scope_checker):
        """Test filtering a list of hosts."""
        hosts = ["example.com", "api.example.com", "prod.example.com", "other.com"]
        allowed, blocked = sample_scope_checker.filter_hosts(hosts)

        assert "example.com" in allowed
        assert "api.example.com" in allowed
        assert "prod.example.com" in blocked
        assert "other.com" in blocked

    def test_check_and_log(self, sample_scope_checker, tmp_path):
        """Test scope checking with artifact logging."""
        artifact_file = tmp_path / "scope_log.jsonl"

        result = sample_scope_checker.check_and_log("example.com", str(artifact_file))
        assert result is True
        assert artifact_file.exists()

        with open(artifact_file) as f:
            data = json.loads(f.readline())
            assert data["action"] == "allowed"


class TestScopeIO:
    """Tests for scope file I/O functions."""

    def test_load_scope(self, temp_scope_file):
        """Test loading scope from file."""
        config = load_scope(str(temp_scope_file))
        assert "example.com" in config.allowed
        assert "prod.example.com" in config.forbidden

    def test_load_scope_file_not_found(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_scope("nonexistent.json")

    def test_load_scope_safe_file_not_found(self):
        """Test safe loading returns None for missing file."""
        result = load_scope_safe("nonexistent.json")
        assert result is None

    def test_load_scope_safe_valid_file(self, temp_scope_file):
        """Test safe loading with valid file."""
        result = load_scope_safe(str(temp_scope_file))
        assert result is not None
        assert "example.com" in result.allowed

    def test_save_scope(self, tmp_path):
        """Test saving scope to file."""
        config = ScopeConfig(allowed=["test.com"], forbidden=["prod.test.com"])
        scope_file = tmp_path / "new_scope.json"

        save_scope(config, str(scope_file))

        assert scope_file.exists()
        with open(scope_file) as f:
            data = json.load(f)
            assert data["allowed"] == ["test.com"]

    def test_save_scope_creates_directories(self, tmp_path):
        """Test save_scope creates parent directories."""
        config = ScopeConfig(allowed=["test.com"])
        nested_file = tmp_path / "deep" / "nested" / "scope.json"

        save_scope(config, str(nested_file))

        assert nested_file.exists()


class TestCreateScopeChecker:
    """Tests for the create_scope_checker factory function."""

    def test_create_from_lists(self):
        """Test creating checker from explicit lists."""
        checker = create_scope_checker(
            allowed=["test.com"],
            forbidden=["bad.com"],
        )
        allowed, _ = checker.is_allowed("test.com")
        assert allowed is True

    def test_create_from_file(self, temp_scope_file):
        """Test creating checker from config file."""
        checker = create_scope_checker(config_path=str(temp_scope_file))
        allowed, _ = checker.is_allowed("example.com")
        assert allowed is True

    def test_create_empty_allows_all(self):
        """Test creating checker with no config allows all."""
        # This will try default path which doesn't exist
        checker = create_scope_checker()
        allowed, _ = checker.is_allowed("anything.com")
        assert allowed is True
