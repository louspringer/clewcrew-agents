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

    # Quality Integration Methods
    async def generate_quality_metrics(self, project_path: Path) -> dict[str, Any]:
        """
        Generate build quality metrics for integration with quality system.
        
        Args:
            project_path: Path to the project to analyze
            
        Returns:
            Dictionary containing build quality metrics
        """
        result = await self.detect_hallucinations(project_path)
        
        # Calculate build quality score based on existing data
        build_data = await self._find_existing_build_data(project_path)
        
        if not build_data:
            # No build infrastructure
            quality_score = 0.0
        elif not result.hallucinations:
            # Build configured and working
            quality_score = 88.0
        elif len(result.hallucinations) <= 3:
            # Minor build issues
            quality_score = 72.0
        elif len(result.hallucinations) <= 7:
            # Moderate build issues
            quality_score = 52.0
        else:
            # Major build issues
            quality_score = 22.0
        
        return {
            "quality_score": quality_score,
            "issues_found": len(result.hallucinations),
            "build_files_found": len(build_data),
            "recommendations": result.recommendations,
            "confidence": result.confidence,
            "total_issues": len(result.hallucinations)
        }

    async def provide_quality_recommendations(self, project_path: Path) -> list[str]:
        """
        Provide build quality improvement recommendations.
        
        Args:
            project_path: Path to the project to analyze
            
        Returns:
            List of quality improvement recommendations
        """
        result = await self.detect_hallucinations(project_path)
        return result.recommendations

    async def assess_quality_impact(self, changes: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Assess the impact of proposed changes on build quality.
        
        Args:
            changes: List of proposed changes
            
        Returns:
            Dictionary containing quality impact assessment
        """
        # Analyze changes for build quality risks
        build_quality_risks = []
        risk_level = "low"
        
        for change in changes:
            change_type = change.get("type", "unknown")
            if change_type in ["build_config_change", "dependency_change", "tool_change"]:
                build_quality_risks.append(f"Risk: {change_type} may affect build stability")
                risk_level = "medium"
            elif change_type in ["build_improvement", "tool_improvement"]:
                build_quality_risks.append(f"Benefit: {change_type} improves build quality")
        
        if build_quality_risks:
            risk_level = "high"
        
        return {
            "quality_impact": "build_quality_assessment",
            "risk_level": risk_level,
            "build_quality_risks": build_quality_risks,
            "recommendations": [
                "Review changes for build pipeline impact",
                "Ensure build configuration remains stable",
                "Test build changes in isolated environment",
                "Maintain build automation and monitoring"
            ]
        }

    def get_quality_metric_name(self) -> str:
        """Get the name of the build quality metric."""
        return "build_quality"

    def get_quality_metric_weight(self) -> float:
        """Get the weight of the build quality metric."""
        return 1.2

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
