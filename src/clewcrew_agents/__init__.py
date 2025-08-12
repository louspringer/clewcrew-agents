"""
clewcrew-agents

Expert agent framework for the clewcrew portfolio.
This package provides AI-powered expert agents for different domains including
security, code quality, testing, build, architecture, and model validation.
"""

__version__ = "0.1.0"
__author__ = "Lou Springer"
__email__ = "lou@example.com"

from .base_expert import BaseExpert, HallucinationResult
from .security_expert import SecurityExpert

__all__ = [
    "BaseExpert",
    "HallucinationResult",
    "SecurityExpert",
]
