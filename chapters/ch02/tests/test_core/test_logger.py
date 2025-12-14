"""Tests for ArtifactLogger."""

import pytest
import json
import os
import tempfile
import shutil
from src.core.logger import ArtifactLogger


class TestArtifactLogger:
    """Test ArtifactLogger functionality."""

    def setup_method(self):
        """Create temporary directory for test logs."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_logger_creation(self):
        """Test logger initialization."""
        logger = ArtifactLogger(run_dir=self.test_dir)
        assert logger.run_id is not None
        assert os.path.exists(self.test_dir)
        logger.close()

    def test_write_single_record(self):
        """Test writing a single record."""
        logger = ArtifactLogger(run_dir=self.test_dir)
        record = {"action": "ping", "target": "example.com", "result": "success"}
        logger.write(record)
        logger.close()

        # Read back and verify
        log_file = f"{self.test_dir}/{logger.run_id}.jsonl"
        assert os.path.exists(log_file)

        with open(log_file, "r") as f:
            line = f.readline()
            data = json.loads(line)
            assert data["action"] == "ping"
            assert data["target"] == "example.com"

    def test_write_multiple_records(self):
        """Test writing multiple records."""
        logger = ArtifactLogger(run_dir=self.test_dir)

        records = [
            {"step": 1, "action": "scan"},
            {"step": 2, "action": "enumerate"},
            {"step": 3, "action": "exploit"},
        ]

        for record in records:
            logger.write(record)

        logger.close()

        # Read all records
        log_file = f"{self.test_dir}/{logger.run_id}.jsonl"
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 3

            for i, line in enumerate(lines):
                data = json.loads(line)
                assert data["step"] == i + 1

    def test_context_manager(self):
        """Test logger as context manager."""
        record = {"test": "context_manager"}

        with ArtifactLogger(run_dir=self.test_dir) as logger:
            logger.write(record)
            run_id = logger.run_id

        # Verify file was closed and written
        log_file = f"{self.test_dir}/{run_id}.jsonl"
        assert os.path.exists(log_file)

        with open(log_file, "r") as f:
            data = json.loads(f.readline())
            assert data["test"] == "context_manager"
