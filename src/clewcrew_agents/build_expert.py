#!/usr/bin/env python3
"""
Build Expert Agent for clewcrew

CRITICAL: This agent analyzes existing build configuration and logs.
It does NOT run expensive build tools.
"""

from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, HallucinationResult


class BuildExpert(BaseExpert):
    """Build expert that analyzes existing build configuration and logs"""

    async def detect_hallucinations(self, project_path: Path) -> HallucinationResult:
        """Analyze existing build data and provide recommendations"""
        hallucinations = []
        recommendations = []

        # Look for existing build configuration and logs
        build_data = await self._find_existing_build_data(project_path)
        
        if not build_data:
            recommendations = [
                "No existing build configuration found",
                "Consider setting up proper build tools (poetry, pip, etc.)",
                "Implement automated build pipelines",
                "Set up build artifact management"
            ]
            return HallucinationResult(
                hallucinations=[],
                confidence=0.3,
                recommendations=recommendations
            )

        # Analyze build configuration
        config_issues = await self._analyze_build_config(project_path)
        hallucinations.extend(config_issues)

        # Analyze build logs
        log_issues = await self._analyze_build_logs(project_path)
        hallucinations.extend(log_issues)

        # Generate recommendations based on existing data
        if hallucinations:
            recommendations = [
                "Review and fix build configuration issues",
                "Address build failures identified in logs",
                "Improve build automation and pipelines",
                "Consider implementing build caching strategies"
            ]
        else:
            recommendations = [
                "Build configuration appears sound based on existing files",
                "Continue monitoring build performance",
                "Consider implementing advanced build strategies",
                "Add build metrics and monitoring"
            ]

        confidence = self.calculate_confidence(hallucinations)

        return HallucinationResult(
            hallucinations=hallucinations,
            confidence=confidence,
            recommendations=recommendations,
        )

    async def _find_existing_build_data(self, project_path: Path) -> list[Path]:
        """Find existing build configuration and log files"""
        build_files = []
        
        # Build configuration files
        config_files = [
            "pyproject.toml", "setup.py", "setup.cfg", "build.py",
            "Makefile", "dockerfile", "Dockerfile"
        ]
        
        for config_file in config_files:
            file_path = project_path / config_file
            if file_path.exists():
                build_files.append(file_path)
        
        # Build output directories
        output_dirs = ["build/", "dist/", "*.egg-info/", "target/"]
        for output_dir in output_dirs:
            dir_path = project_path / output_dir
            if dir_path.exists():
                build_files.append(dir_path)
        
        return build_files

    async def _analyze_build_config(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing build configuration files"""
        issues = []
        
        # Check pyproject.toml
        pyproject_file = project_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                    if "build-system" not in content:
                        issues.append({
                            "type": "build_config_issue",
                            "file": str(pyproject_file),
                            "description": "Missing build-system configuration",
                            "priority": "medium",
                            "tool": "build_config",
                            "source": "existing_config"
                        })
            except Exception as e:
                self.logger.warning(f"Could not read {pyproject_file}: {e}")
        
        return issues

    async def _analyze_build_logs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing build logs"""
        issues = []
        
        # Look for build log files
        log_files = ["build.log", "make.log", "docker.log"]
        for log_file in log_files:
            log_path = project_path / log_file
            if log_path.exists():
                try:
                    with open(log_path, 'r') as f:
                        content = f.read()
                        if "error" in content.lower() or "failed" in content.lower():
                            issues.append({
                                "type": "build_failure",
                                "file": str(log_path),
                                "description": "Build log contains error or failure messages",
                                "priority": "high",
                                "tool": "build_logs",
                                "source": "existing_logs"
                            })
                except Exception as e:
                    self.logger.warning(f"Could not read {log_path}: {e}")
        
        return issues

    async def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Suggest fixes based on existing build data"""
        fixes = []

        for issue in issues:
            if issue["type"] == "build_config_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix build configuration",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_config"
                })
            elif issue["type"] == "build_failure":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix build failures",
                    "description": "Review and fix the build failures identified in logs",
                    "priority": issue["priority"],
                    "source": "existing_logs"
                })

        return fixes
