#!/usr/bin/env python3
"""
Model Expert Agent for clewcrew

CRITICAL: This agent analyzes existing model configuration and outputs.
It does NOT run expensive model training or inference tools.
"""

from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, HallucinationResult


class ModelExpert(BaseExpert):
    """Model expert that analyzes existing model configuration and outputs"""

    async def detect_hallucinations(self, project_path: Path) -> HallucinationResult:
        """Analyze existing model data and provide recommendations"""
        hallucinations = []
        recommendations = []

        # Look for existing model configuration and outputs
        model_data = await self._find_existing_model_data(project_path)
        
        if not model_data:
            recommendations = [
                "No existing model configuration found",
                "Consider documenting model architecture and parameters",
                "Implement model versioning and tracking",
                "Set up model performance monitoring"
            ]
            return HallucinationResult(
                hallucinations=[],
                confidence=0.3,
                recommendations=recommendations
            )

        # Analyze model configuration
        config_issues = await self._analyze_model_config(project_path)
        hallucinations.extend(config_issues)

        # Analyze model outputs
        output_issues = await self._analyze_model_outputs(project_path)
        hallucinations.extend(output_issues)

        # Generate recommendations based on existing data
        if hallucinations:
            recommendations = [
                "Review and fix model configuration issues",
                "Address model performance issues identified in outputs",
                "Improve model documentation and versioning",
                "Consider implementing model monitoring and alerting"
            ]
        else:
            recommendations = [
                "Model configuration appears sound based on existing files",
                "Continue monitoring model performance",
                "Consider implementing advanced model strategies",
                "Add comprehensive model evaluation metrics"
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
        Generate model quality metrics for integration with quality system.
        
        Args:
            project_path: Path to the project to analyze
            
        Returns:
            Dictionary containing model quality metrics
        """
        result = await self.detect_hallucinations(project_path)
        
        # Calculate model quality score based on existing data
        model_data = await self._find_existing_model_data(project_path)
        
        if not model_data:
            # No model infrastructure
            quality_score = 0.0
        elif not result.hallucinations:
            # Model configured and working
            quality_score = 92.0
        elif len(result.hallucinations) <= 3:
            # Minor model issues
            quality_score = 78.0
        elif len(result.hallucinations) <= 7:
            # Moderate model issues
            quality_score = 58.0
        else:
            # Major model issues
            quality_score = 28.0
        
        return {
            "quality_score": quality_score,
            "issues_found": len(result.hallucinations),
            "model_files_found": len(model_data),
            "recommendations": result.recommendations,
            "confidence": result.confidence,
            "total_issues": len(result.hallucinations)
        }

    async def provide_quality_recommendations(self, project_path: Path) -> list[str]:
        """
        Provide model quality improvement recommendations.
        
        Args:
            project_path: Path to the project to analyze
            
        Returns:
            List of quality improvement recommendations
        """
        result = await self.detect_hallucinations(project_path)
        return result.recommendations

    async def assess_quality_impact(self, changes: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Assess the impact of proposed changes on model quality.
        
        Args:
            changes: List of proposed changes
            
        Returns:
            Dictionary containing quality impact assessment
        """
        # Analyze changes for model quality risks
        model_quality_risks = []
        risk_level = "low"
        
        for change in changes:
            change_type = change.get("type", "unknown")
            if change_type in ["model_config_change", "hyperparameter_change", "architecture_change"]:
                model_quality_risks.append(f"Risk: {change_type} may affect model performance")
                risk_level = "medium"
            elif change_type in ["model_improvement", "config_improvement"]:
                model_quality_risks.append(f"Benefit: {change_type} improves model quality")
        
        if model_quality_risks:
            risk_level = "high"
        
        return {
            "quality_impact": "model_quality_assessment",
            "risk_level": risk_level,
            "model_quality_risks": model_quality_risks,
            "recommendations": [
                "Review changes for model performance impact",
                "Ensure model configuration remains stable",
                "Test model changes with validation data",
                "Maintain model monitoring and evaluation"
            ]
        }

    def get_quality_metric_name(self) -> str:
        """Get the name of the model quality metric."""
        return "model_quality"

    def get_quality_metric_weight(self) -> float:
        """Get the weight of the model quality metric."""
        return 1.3

    async def _find_existing_model_data(self, project_path: Path) -> list[Path]:
        """Find existing model configuration and output files"""
        model_files = []
        
        # Model configuration files
        config_files = [
            "model_config.json", "model.yaml", "config.yaml",
            "hyperparameters.json", "model_params.json"
        ]
        
        for config_file in config_files:
            file_path = project_path / config_file
            if file_path.exists():
                model_files.append(file_path)
        
        # Model output directories
        output_dirs = ["models/", "checkpoints/", "outputs/", "results/"]
        for output_dir in output_dirs:
            dir_path = project_path / output_dir
            if dir_path.exists():
                model_files.append(dir_path)
        
        return model_files

    async def _analyze_model_config(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing model configuration files"""
        issues = []
        
        # Check for model configuration files
        config_files = [
            project_path / "model_config.json",
            project_path / "config.yaml"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()
                        if "model" in content.lower():
                            # Check for basic configuration
                            if "version" not in content:
                                issues.append({
                                    "type": "model_config_issue",
                                    "file": str(config_file),
                                    "description": "Model configuration missing version information",
                                    "priority": "medium",
                                    "tool": "model_config",
                                    "source": "existing_config"
                                })
                except Exception as e:
                    self.logger.warning(f"Could not read {config_file}: {e}")
        
        return issues

    async def _analyze_model_outputs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing model outputs"""
        issues = []
        
        # Look for model output files
        output_files = ["model.log", "training.log", "evaluation.log"]
        for output_file in output_files:
            log_path = project_path / output_file
            if log_path.exists():
                try:
                    with open(log_path, 'r') as f:
                        content = f.read()
                        if "error" in content.lower() or "failed" in content.lower():
                            issues.append({
                                "type": "model_failure",
                                "file": str(log_path),
                                "description": "Model log contains error or failure messages",
                                "priority": "high",
                                "tool": "model_logs",
                                "source": "existing_logs"
                            })
                except Exception as e:
                    self.logger.warning(f"Could not read {log_path}: {e}")
        
        return issues

    async def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Suggest fixes based on existing model data"""
        fixes = []

        for issue in issues:
            if issue["type"] == "model_config_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix model configuration",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_config"
                })
            elif issue["type"] == "model_failure":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix model failures",
                    "description": "Review and fix the model failures identified in logs",
                    "priority": issue["priority"],
                    "source": "existing_logs"
                })

        return fixes
