#!/usr/bin/env python3
"""
Code Quality Expert Agent for clewcrew

CRITICAL: This agent analyzes existing tool outputs and logs.
It does NOT run expensive tools like flake8, black, or mypy.
"""

import json
from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, HallucinationResult


class CodeQualityExpert(BaseExpert):
    """Code quality expert that analyzes existing tool outputs and logs"""

    async def detect_hallucinations(self, project_path: Path) -> HallucinationResult:
        """Analyze existing code quality data and provide recommendations"""
        hallucinations = []
        recommendations = []

        # Look for existing tool output files
        tool_outputs = await self._find_existing_tool_outputs(project_path)
        
        if not tool_outputs:
            recommendations = [
                "No existing code quality tool outputs found",
                "Consider running quality tools and saving outputs for analysis",
                "Set up CI/CD pipeline to capture tool outputs",
                "Use pre-commit hooks to generate quality reports"
            ]
            return HallucinationResult(
                hallucinations=[],
                confidence=0.5,
                recommendations=recommendations
            )

        # Analyze existing flake8 outputs
        flake8_issues = await self._analyze_existing_flake8_outputs(project_path)
        hallucinations.extend(flake8_issues)

        # Analyze existing black outputs
        black_issues = await self._analyze_existing_black_outputs(project_path)
        hallucinations.extend(black_issues)

        # Analyze existing mypy outputs
        mypy_issues = await self._analyze_existing_mypy_outputs(project_path)
        hallucinations.extend(mypy_issues)

        # Analyze existing CI/CD logs
        ci_issues = await self._analyze_existing_ci_logs(project_path)
        hallucinations.extend(ci_issues)

        # Generate recommendations based on existing data
        if hallucinations:
            recommendations = [
                "Address code quality issues found in existing tool outputs",
                "Review and fix flake8 violations",
                "Run black formatter to fix formatting issues",
                "Add proper type annotations based on mypy findings",
                "Consider implementing pre-commit hooks for automated quality checks",
                "Set up quality gates in CI/CD pipeline"
            ]
        else:
            recommendations = [
                "Code quality checks passed based on existing tool outputs",
                "Continue monitoring with automated quality checks",
                "Consider adding more comprehensive quality analysis tools"
            ]

        confidence = self.calculate_confidence(hallucinations)

        return HallucinationResult(
            hallucinations=hallucinations,
            confidence=confidence,
            recommendations=recommendations,
        )

    async def _find_existing_tool_outputs(self, project_path: Path) -> list[Path]:
        """Find existing tool output files without running tools"""
        output_files = []
        
        # Use actual tool configuration from project
        tool_outputs = [
            "pyproject.toml",  # Contains black, mypy, pytest, ruff config
            ".ruff.toml",      # Ruff configuration
            "pytest.ini",      # Pytest configuration
            "setup.cfg",       # Alternative config location
            ".flake8",         # Flake8 configuration
            "tox.ini",         # Tox configuration
            "coverage.xml",    # Coverage reports
            "htmlcov/",        # Coverage HTML output
            "logs/",           # Log files directory
            ".github/workflows/",  # GitHub Actions workflows
            ".gitlab-ci.yml",      # GitLab CI configuration
        ]
        
        for output_file in tool_outputs:
            file_path = project_path / output_file
            if file_path.exists():
                output_files.append(file_path)
        
        # Look for CI/CD artifacts
        ci_dirs = [".github", ".gitlab-ci", ".circleci", "ci", "jenkins"]
        for ci_dir in ci_dirs:
            ci_path = project_path / ci_dir
            if ci_path.exists():
                output_files.extend(ci_path.rglob("*.yml"))
                output_files.extend(ci_path.rglob("*.yaml"))
                output_files.extend(ci_path.rglob("*.json"))
        
        return output_files

    async def _analyze_existing_flake8_outputs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing flake8 output files"""
        issues = []
        
        # Look for flake8 output files
        flake8_files = [
            project_path / "flake8_report.json",
            project_path / "flake8_report.txt",
            project_path / ".flake8"
        ]
        
        for flake8_file in flake8_files:
            if flake8_file.exists():
                try:
                    if flake8_file.suffix == ".json":
                        with open(flake8_file, 'r') as f:
                            data = json.load(f)
                            for issue in data:
                                issues.append({
                                    "type": "code_quality_issue",
                                    "file": issue.get("filename", "unknown"),
                                    "line": issue.get("line_number", 0),
                                    "column": issue.get("column_number", 0),
                                    "code": issue.get("code", ""),
                                    "description": issue.get("text", ""),
                                    "priority": "medium",
                                    "tool": "flake8",
                                    "source": "existing_output"
                                })
                    else:
                        # Parse text output
                        with open(flake8_file, 'r') as f:
                            for line in f:
                                if ':' in line:
                                    parts = line.strip().split(':')
                                    if len(parts) >= 4:
                                        issues.append({
                                            "type": "code_quality_issue",
                                            "file": parts[0],
                                            "line": int(parts[1]) if parts[1].isdigit() else 0,
                                            "column": int(parts[2]) if parts[2].isdigit() else 0,
                                            "code": parts[3].split()[0] if len(parts[3].split()) > 0 else "",
                                            "description": ':'.join(parts[3:]).strip(),
                                            "priority": "medium",
                                            "tool": "flake8",
                                            "source": "existing_output"
                                        })
                except Exception as e:
                    self.logger.warning(f"Could not parse {flake8_file}: {e}")
        
        return issues

    async def _analyze_existing_black_outputs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing black output files"""
        issues = []
        
        # Look for black output files
        black_files = [
            project_path / "black_report.txt",
            project_path / "pyproject.toml"
        ]
        
        for black_file in black_files:
            if black_file.exists():
                try:
                    with open(black_file, 'r') as f:
                        content = f.read()
                        if "black" in content.lower():
                            # Check if black is configured
                            if "line-length" in content or "target-version" in content:
                                issues.append({
                                    "type": "formatting_config",
                                    "file": str(black_file),
                                    "description": "Black formatter configuration found",
                                    "priority": "low",
                                    "tool": "black",
                                    "source": "existing_config"
                                })
                except Exception as e:
                    self.logger.warning(f"Could not parse {black_file}: {e}")
        
        return issues

    async def _analyze_existing_mypy_outputs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing mypy output files"""
        issues = []
        
        # Look for mypy output files
        mypy_files = [
            project_path / "mypy_report.txt",
            project_path / "pyproject.toml",
            project_path / "setup.cfg"
        ]
        
        for mypy_file in mypy_files:
            if mypy_file.exists():
                try:
                    with open(mypy_file, 'r') as f:
                        content = f.read()
                        if "mypy" in content.lower():
                            # Check if mypy is configured
                            if "warn_return_any" in content or "disallow_untyped_defs" in content:
                                issues.append({
                                    "type": "type_checking_config",
                                    "file": str(mypy_file),
                                    "description": "MyPy type checker configuration found",
                                    "priority": "low",
                                    "tool": "mypy",
                                    "source": "existing_config"
                                })
                except Exception as e:
                    self.logger.warning(f"Could not parse {mypy_file}: {e}")
        
        return issues

    async def _analyze_existing_ci_logs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing CI/CD logs for quality information"""
        issues = []
        
        # Look for CI/CD configuration files
        ci_dirs = [".github", ".gitlab-ci", ".circleci", "ci", "jenkins"]
        
        for ci_dir in ci_dirs:
            ci_path = project_path / ci_dir
            if ci_path.exists():
                for config_file in ci_path.rglob("*.yml"):
                    try:
                        with open(config_file, 'r') as f:
                            content = f.read()
                            if "flake8" in content or "black" in content or "mypy" in content:
                                issues.append({
                                    "type": "ci_quality_integration",
                                    "file": str(config_file),
                                    "description": "Quality tools integrated in CI/CD pipeline",
                                    "priority": "low",
                                    "tool": "ci_cd",
                                    "source": "existing_config"
                                })
                    except Exception as e:
                        self.logger.warning(f"Could not parse {config_file}: {e}")
        
        return issues

    async def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Suggest fixes based on existing tool outputs"""
        fixes = []

        for issue in issues:
            if issue["type"] == "code_quality_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix code quality issue",
                    "description": f"Address {issue['code']}: {issue['description']}",
                    "priority": "medium",
                    "source": "existing_tool_output"
                })
            elif issue["type"] == "formatting_config":
                fixes.append({
                    "issue": issue,
                    "fix": "Configure Black formatter",
                    "description": "Set up Black formatting rules in pyproject.toml",
                    "priority": "low",
                    "source": "existing_config"
                })
            elif issue["type"] == "type_checking_config":
                fixes.append({
                    "issue": issue,
                    "fix": "Configure MyPy type checker",
                    "description": "Set up MyPy type checking rules",
                    "priority": "low",
                    "source": "existing_config"
                })

        return fixes
