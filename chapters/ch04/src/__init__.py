"""
Chapter 4: Passive Reconnaissance Agents

A modular, auditable passive reconnaissance pipeline that demonstrates
AI agent patterns for offensive security.

Core components:
- src.core: Artifact dataclass and JSONL utilities
- src.recon: Reconnaissance modules (DNS, HTTP, WAF, TLS, etc.)
- src.safety: Scope enforcement and safety gates

Example usage:
    from src.recon import ReconPipeline, PipelineConfig

    config = PipelineConfig(include_tls=True)
    pipeline = ReconPipeline(config)
    result = pipeline.run("example.com")
"""

__version__ = "0.1.0"
