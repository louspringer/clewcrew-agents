"""
clewcrew-agents: Expert agent framework for the clewcrew portfolio

This package provides expert agents for different domains:
- Security analysis
- Code quality assessment
- DevOps and CI/CD analysis
- Testing and coverage analysis
- Architecture review
- Build system analysis
- Model and ML analysis
- MCP (Model Context Protocol) analysis

All agents follow the principle of analyzing existing data and outputs
rather than running expensive tools themselves.
"""

from .base_expert import BaseExpert, HallucinationResult
from .security_expert import SecurityExpert
from .code_quality_expert import CodeQualityExpert
from .devops_expert import DevOpsExpert
from .test_expert import TestExpert
from .architecture_expert import ArchitectureExpert
from .build_expert import BuildExpert
from .model_expert import ModelExpert
from .mcp_expert import MCPExpert

__all__ = [
    "BaseExpert",
    "HallucinationResult",
    "SecurityExpert",
    "CodeQualityExpert",
    "DevOpsExpert",
    "TestExpert",
    "ArchitectureExpert",
    "BuildExpert",
    "ModelExpert",
    "MCPExpert",
]

__version__ = "0.1.0"
