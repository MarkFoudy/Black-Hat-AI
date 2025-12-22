"""
Sample target data for pipeline demonstrations.

Provides synthetic targets that demonstrate different risk levels
and gate behaviors.
"""

from typing import List


# Primary target list for demonstrations
TARGETS = [
    "admin.example.com",
    "api.example.com",
    "cdn.example.com",
    "staging.example.com",
    "prod.example.com",  # Should be blocked by EnvironmentGate
]


# Extended sample targets with metadata
SAMPLE_TARGETS = [
    {
        "host": "admin.example.com",
        "type": "web",
        "expected_risk": "high",
        "notes": "Administrative interface, likely sensitive",
    },
    {
        "host": "api.example.com",
        "type": "api",
        "expected_risk": "medium",
        "notes": "API endpoint, may expose sensitive data",
    },
    {
        "host": "cdn.example.com",
        "type": "cdn",
        "expected_risk": "low",
        "notes": "Content delivery, static assets",
    },
    {
        "host": "staging.example.com",
        "type": "web",
        "expected_risk": "high",
        "notes": "Staging environment, may have debug enabled",
    },
    {
        "host": "dev.example.com",
        "type": "web",
        "expected_risk": "high",
        "notes": "Development environment",
    },
    {
        "host": "test.example.com",
        "type": "web",
        "expected_risk": "medium",
        "notes": "Test environment",
    },
    {
        "host": "www.example.com",
        "type": "web",
        "expected_risk": "low",
        "notes": "Public website",
    },
    {
        "host": "mail.example.com",
        "type": "mail",
        "expected_risk": "medium",
        "notes": "Mail server",
    },
    {
        "host": "prod.example.com",
        "type": "web",
        "expected_risk": "blocked",
        "notes": "Production - should be blocked by safety gates",
    },
    {
        "host": "payment.example.com",
        "type": "web",
        "expected_risk": "blocked",
        "notes": "Payment processing - should be blocked",
    },
]


def get_targets(
    exclude_blocked: bool = True,
    risk_level: str = None,
) -> List[str]:
    """
    Get a filtered list of target hosts.

    Args:
        exclude_blocked: If True, exclude targets that should be blocked
        risk_level: Filter by risk level ("high", "medium", "low")

    Returns:
        List of target hostnames
    """
    targets = []

    for t in SAMPLE_TARGETS:
        # Skip blocked targets if requested
        if exclude_blocked and t["expected_risk"] == "blocked":
            continue

        # Filter by risk level if specified
        if risk_level and t["expected_risk"] != risk_level:
            continue

        targets.append(t["host"])

    return targets
