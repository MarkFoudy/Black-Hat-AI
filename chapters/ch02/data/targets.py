"""
Sample target data for examples.

This module provides sample hostnames and IPs for demonstration purposes.
DO NOT use in production environments.
"""

# Sample targets for reconnaissance and testing
targets = [
    "example.com",
    "test.example.com",
    "dev-api.example.com",
    "staging-db.example.com",
    "admin.example.com",
    "no-such-host.local",
    "10.0.1.100",
    "192.168.1.1",
]

# High-value targets (for prioritization examples)
high_value_targets = [
    "admin.example.com",
    "api.example.com",
    "auth.example.com",
]

# Sample target metadata
target_metadata = {
    "example.com": {
        "priority": "high",
        "type": "production",
        "ports": [80, 443],
    },
    "test.example.com": {
        "priority": "low",
        "type": "testing",
        "ports": [80, 443, 8080],
    },
    "admin.example.com": {
        "priority": "critical",
        "type": "admin-interface",
        "ports": [443],
    },
}
