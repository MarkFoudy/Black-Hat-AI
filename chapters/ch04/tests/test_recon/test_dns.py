"""
Tests for src/recon/dns.py (Listing 4.3)
"""

import os
import socket
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.recon.dns import candidates, resolve, resolve_batch


class TestCandidates:
    """Tests for the candidates function."""

    def test_candidates_generates_subdomains(self):
        """Test candidates generates expected subdomains."""
        result = candidates("example.com")
        assert "example.com" in result
        assert "www.example.com" in result
        assert "api.example.com" in result

    def test_candidates_returns_sorted(self):
        """Test candidates returns sorted list."""
        result = candidates("example.com")
        assert result == sorted(result)

    def test_candidates_no_duplicates(self):
        """Test candidates has no duplicates."""
        result = candidates("example.com")
        assert len(result) == len(set(result))

    def test_candidates_handles_subdomain_input(self):
        """Test candidates handles input that's already a subdomain."""
        result = candidates("sub.example.com")
        assert "sub.example.com" in result
        assert "www.sub.example.com" in result


class TestResolve:
    """Tests for the resolve function."""

    def test_resolve_returns_tuple(self):
        """Test resolve returns (ips, cname) tuple."""
        with patch('socket.getaddrinfo') as mock_getaddr:
            with patch('socket.gethostbyname_ex') as mock_gethost:
                mock_getaddr.return_value = [
                    (2, 1, 6, '', ('93.184.216.34', 80)),
                ]
                mock_gethost.return_value = ('example.com', [], ['93.184.216.34'])

                ips, cname = resolve("example.com")

                assert isinstance(ips, list)
                assert isinstance(cname, (str, type(None)))

    def test_resolve_extracts_ips(self):
        """Test resolve extracts IP addresses."""
        with patch('socket.getaddrinfo') as mock_getaddr:
            with patch('socket.gethostbyname_ex') as mock_gethost:
                mock_getaddr.return_value = [
                    (2, 1, 6, '', ('93.184.216.34', 80)),
                    (2, 1, 6, '', ('93.184.216.35', 80)),
                ]
                mock_gethost.return_value = ('example.com', [], [])

                ips, _ = resolve("example.com")

                assert '93.184.216.34' in ips
                assert '93.184.216.35' in ips

    def test_resolve_deduplicates_ips(self):
        """Test resolve removes duplicate IPs."""
        with patch('socket.getaddrinfo') as mock_getaddr:
            with patch('socket.gethostbyname_ex') as mock_gethost:
                mock_getaddr.return_value = [
                    (2, 1, 6, '', ('93.184.216.34', 80)),
                    (2, 1, 6, '', ('93.184.216.34', 80)),
                ]
                mock_gethost.return_value = ('example.com', [], [])

                ips, _ = resolve("example.com")

                assert len(ips) == 1

    def test_resolve_handles_gaierror(self):
        """Test resolve handles DNS lookup errors gracefully."""
        with patch('socket.getaddrinfo') as mock_getaddr:
            with patch('socket.gethostbyname_ex') as mock_gethost:
                mock_getaddr.side_effect = socket.gaierror("Name not found")
                mock_gethost.side_effect = socket.gaierror("Name not found")

                ips, cname = resolve("nonexistent.example.com")

                assert ips == []
                assert cname is None

    def test_resolve_returns_cname(self):
        """Test resolve returns canonical name."""
        with patch('socket.getaddrinfo') as mock_getaddr:
            with patch('socket.gethostbyname_ex') as mock_gethost:
                mock_getaddr.return_value = []
                mock_gethost.return_value = ('canonical.example.com', [], [])

                _, cname = resolve("example.com")

                assert cname == 'canonical.example.com'


class TestResolveBatch:
    """Tests for the resolve_batch function."""

    def test_resolve_batch_processes_multiple_hosts(self):
        """Test resolve_batch processes list of hosts."""
        with patch('src.recon.dns.resolve') as mock_resolve:
            mock_resolve.return_value = (['1.2.3.4'], 'example.com')

            hosts = ['a.com', 'b.com', 'c.com']
            results = resolve_batch(hosts)

            assert len(results) == 3
            assert mock_resolve.call_count == 3

    def test_resolve_batch_returns_correct_structure(self):
        """Test resolve_batch returns (host, ips, cname) tuples."""
        with patch('src.recon.dns.resolve') as mock_resolve:
            mock_resolve.return_value = (['1.2.3.4'], 'test.com')

            results = resolve_batch(['test.com'])

            assert len(results) == 1
            host, ips, cname = results[0]
            assert host == 'test.com'
            assert ips == ['1.2.3.4']
            assert cname == 'test.com'
