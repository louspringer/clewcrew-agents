#!/usr/bin/env python3
"""
MCP Expert Agent for clewcrew

CRITICAL: This agent analyzes existing MCP configuration and logs.
It does NOT run expensive MCP tools.
"""

from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, HallucinationResult


class MCPExpert(BaseExpert):
    """MCP expert that analyzes existing MCP configuration and logs"""

    async def detect_hallucinations(self, project_path: Path) -> HallucinationResult:
        """Analyze existing MCP data and provide recommendations"""
        hallucinations = []
        recommendations = []

        # Look for existing MCP configuration and logs
        mcp_data = await self._find_existing_mcp_data(project_path)
        
        if not mcp_data:
            recommendations = [
                "No existing MCP configuration found",
                "Consider setting up MCP server configuration",
                "Implement MCP client integration",
                "Set up MCP logging and monitoring"
            ]
            return HallucinationResult(
                hallucinations=[],
                confidence=0.3,
                recommendations=recommendations
            )

        # Analyze MCP configuration
        config_issues = await self._analyze_mcp_config(project_path)
        hallucinations.extend(config_issues)

        # Analyze MCP logs
        log_issues = await self._analyze_mcp_logs(project_path)
        hallucinations.extend(log_issues)

        # Generate recommendations based on existing data
        if hallucinations:
            recommendations = [
                "Review and fix MCP configuration issues",
                "Address MCP connection issues identified in logs",
                "Improve MCP error handling and logging",
                "Consider implementing MCP health checks"
            ]
        else:
            recommendations = [
                "MCP configuration appears sound based on existing files",
                "Continue monitoring MCP performance",
                "Consider implementing advanced MCP strategies",
                "Add comprehensive MCP monitoring and alerting"
            ]

        confidence = self.calculate_confidence(hallucinations)

        return HallucinationResult(
            hallucinations=hallucinations,
            confidence=confidence,
            recommendations=recommendations,
        )

    async def _find_existing_mcp_data(self, project_path: Path) -> list[Path]:
        """Find existing MCP configuration and log files"""
        mcp_files = []
        
        # MCP configuration files
        config_files = [
            "mcp_config.json", "mcp.yaml", "mcp.toml",
            ".mcp", "mcp_server.json", "mcp_client.json"
        ]
        
        for config_file in config_files:
            file_path = project_path / config_file
            if file_path.exists():
                mcp_files.append(file_path)
        
        # MCP log directories
        log_dirs = ["logs/", "mcp_logs/", ".mcp_logs/"]
        for log_dir in log_dirs:
            dir_path = project_path / log_dir
            if dir_path.exists():
                mcp_files.append(dir_path)
        
        return mcp_files

    async def _analyze_mcp_config(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing MCP configuration files"""
        issues = []
        
        # Check for MCP configuration files
        config_files = [
            project_path / "mcp_config.json",
            project_path / "mcp.yaml"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()
                        if "mcp" in content.lower():
                            # Check for basic configuration
                            if "server" not in content and "client" not in content:
                                issues.append({
                                    "type": "mcp_config_issue",
                                    "file": str(config_file),
                                    "description": "MCP configuration missing server/client specification",
                                    "priority": "medium",
                                    "tool": "mcp_config",
                                    "source": "existing_config"
                                })
                except Exception as e:
                    self.logger.warning(f"Could not read {config_file}: {e}")
        
        return issues

    async def _analyze_mcp_logs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing MCP logs"""
        issues = []
        
        # Look for MCP log files
        log_files = ["mcp.log", "mcp_server.log", "mcp_client.log"]
        for log_file in log_files:
            log_path = project_path / log_file
            if log_path.exists():
                try:
                    with open(log_path, 'r') as f:
                        content = f.read()
                        if "error" in content.lower() or "failed" in content.lower():
                            issues.append({
                                "type": "mcp_failure",
                                "file": str(log_path),
                                "description": "MCP log contains error or failure messages",
                                "priority": "high",
                                "tool": "mcp_logs",
                                "source": "existing_logs"
                            })
                except Exception as e:
                    self.logger.warning(f"Could not read {log_path}: {e}")
        
        return issues

    async def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Suggest fixes based on existing MCP data"""
        fixes = []

        for issue in issues:
            if issue["type"] == "mcp_config_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix MCP configuration",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_config"
                })
            elif issue["type"] == "mcp_failure":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix MCP failures",
                    "description": "Review and fix the MCP failures identified in logs",
                    "priority": issue["priority"],
                    "source": "existing_logs"
                })

        return fixes
