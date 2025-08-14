#!/usr/bin/env python3
"""
DevOps Expert Agent for clewcrew

CRITICAL: This agent analyzes existing CI/CD logs and configuration files.
It does NOT run expensive deployment or infrastructure tools.
"""

import yaml
from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, HallucinationResult


class DevOpsExpert(BaseExpert):
    """DevOps expert that analyzes existing CI/CD logs and configuration"""

    async def detect_hallucinations(self, project_path: Path) -> HallucinationResult:
        """Analyze existing DevOps data and provide recommendations"""
        hallucinations = []
        recommendations = []

        # Look for existing CI/CD configuration and logs
        ci_cd_data = await self._find_existing_ci_cd_data(project_path)
        
        if not ci_cd_data:
            recommendations = [
                "No existing CI/CD configuration found",
                "Consider setting up GitHub Actions, GitLab CI, or similar",
                "Implement automated testing and deployment pipelines",
                "Set up infrastructure as code with Terraform or CloudFormation"
            ]
            return HallucinationResult(
                hallucinations=[],
                confidence=0.3,
                recommendations=recommendations
            )

        # Analyze CI/CD configuration files
        ci_config_issues = await self._analyze_ci_cd_config(project_path)
        hallucinations.extend(ci_config_issues)

        # Analyze deployment configuration
        deployment_issues = await self._analyze_deployment_config(project_path)
        hallucinations.extend(deployment_issues)

        # Analyze infrastructure configuration
        infrastructure_issues = await self._analyze_infrastructure_config(project_path)
        hallucinations.extend(infrastructure_issues)

        # Analyze existing logs for issues
        log_issues = await self._analyze_existing_logs(project_path)
        hallucinations.extend(log_issues)

        # Generate recommendations based on existing data
        if hallucinations:
            recommendations = [
                "Review and fix CI/CD configuration issues",
                "Ensure deployment pipelines are properly configured",
                "Validate infrastructure as code configurations",
                "Implement proper logging and monitoring",
                "Set up automated testing and quality gates"
            ]
        else:
            recommendations = [
                "DevOps configuration appears sound based on existing files",
                "Continue monitoring CI/CD pipeline performance",
                "Consider implementing advanced deployment strategies",
                "Add comprehensive monitoring and alerting"
            ]

        confidence = self.calculate_confidence(hallucinations)

        return HallucinationResult(
            hallucinations=hallucinations,
            confidence=confidence,
            recommendations=recommendations,
        )

    async def _find_existing_ci_cd_data(self, project_path: Path) -> list[Path]:
        """Find existing CI/CD configuration and log files"""
        ci_cd_files = []
        
        # Common CI/CD directories
        ci_dirs = [".github", ".gitlab-ci", ".circleci", "ci", "jenkins", ".azure"]
        
        for ci_dir in ci_dirs:
            ci_path = project_path / ci_dir
            if ci_path.exists():
                ci_cd_files.extend(ci_path.rglob("*.yml"))
                ci_cd_files.extend(ci_path.rglob("*.yaml"))
                ci_cd_files.extend(ci_path.rglob("*.json"))
                ci_cd_files.extend(ci_path.rglob("*.xml"))
        
        # Look for infrastructure files
        infra_files = [
            "docker-compose.yml", "docker-compose.yaml",
            "Dockerfile", "dockerfile",
            "terraform.tf", "terraform.tfvars",
            "cloudformation.yaml", "cloudformation.yml",
            "kubernetes.yaml", "k8s.yaml",
            "helm-chart.yaml", "values.yaml"
        ]
        
        for infra_file in infra_files:
            file_path = project_path / infra_file
            if file_path.exists():
                ci_cd_files.append(file_path)
        
        return ci_cd_files

    async def _analyze_ci_cd_config(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing CI/CD configuration files"""
        issues = []
        
        # GitHub Actions
        github_dir = project_path / ".github" / "workflows"
        if github_dir.exists():
            for workflow_file in github_dir.rglob("*.yml"):
                try:
                    with open(workflow_file, 'r') as f:
                        workflow = yaml.safe_load(f)
                        if workflow:
                            # Check for common issues
                            if "on" not in workflow:
                                issues.append({
                                    "type": "ci_config_issue",
                                    "file": str(workflow_file),
                                    "description": "Missing trigger configuration in GitHub Actions workflow",
                                    "priority": "high",
                                    "tool": "github_actions",
                                    "source": "existing_config"
                                })
                            
                            # Check for security issues
                            if "permissions" in workflow:
                                perms = workflow["permissions"]
                                if perms.get("contents") == "write":
                                    issues.append({
                                        "type": "security_issue",
                                        "file": str(workflow_file),
                                        "description": "Workflow has write permissions to repository contents",
                                        "priority": "medium",
                                        "tool": "github_actions",
                                        "source": "existing_config"
                                    })
                except Exception as e:
                    self.logger.warning(f"Could not parse {workflow_file}: {e}")
        
        # GitLab CI
        gitlab_file = project_path / ".gitlab-ci.yml"
        if gitlab_file.exists():
            try:
                with open(gitlab_file, 'r') as f:
                    gitlab_config = yaml.safe_load(f)
                    if gitlab_config:
                        # Check for basic structure
                        if "stages" not in gitlab_config:
                            issues.append({
                                "type": "ci_config_issue",
                                "file": str(gitlab_file),
                                "description": "Missing stages configuration in GitLab CI",
                                "priority": "medium",
                                "tool": "gitlab_ci",
                                "source": "existing_config"
                            })
            except Exception as e:
                self.logger.warning(f"Could not parse {gitlab_file}: {e}")
        
        return issues

    async def _analyze_deployment_config(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing deployment configuration files"""
        issues = []
        
        # Docker Compose
        docker_compose_files = [
            project_path / "docker-compose.yml",
            project_path / "docker-compose.yaml"
        ]
        
        for compose_file in docker_compose_files:
            if compose_file.exists():
                try:
                    with open(compose_file, 'r') as f:
                        compose_config = yaml.safe_load(f)
                        if compose_config:
                            # Check for security issues
                            services = compose_config.get("services", {})
                            for service_name, service_config in services.items():
                                if service_config.get("privileged"):
                                    issues.append({
                                        "type": "security_issue",
                                        "file": str(compose_file),
                                        "description": f"Service '{service_name}' runs in privileged mode",
                                        "priority": "high",
                                        "tool": "docker_compose",
                                        "source": "existing_config"
                                    })
                except Exception as e:
                    self.logger.warning(f"Could not parse {compose_file}: {e}")
        
        # Kubernetes
        k8s_files = [
            project_path / "kubernetes.yaml",
            project_path / "k8s.yaml"
        ]
        
        for k8s_file in k8s_files:
            if k8s_file.exists():
                try:
                    with open(k8s_file, 'r') as f:
                        k8s_config = yaml.safe_load(f)
                        if k8s_config:
                            # Check for resource limits
                            if "spec" in k8s_config:
                                spec = k8s_config["spec"]
                                if "template" in spec:
                                    template = spec["template"]
                                    if "spec" in template:
                                        pod_spec = template["spec"]
                                        containers = pod_spec.get("containers", [])
                                        for container in containers:
                                            if "resources" not in container:
                                                issues.append({
                                                    "type": "deployment_issue",
                                                    "file": str(k8s_file),
                                                    "description": f"Container '{container.get('name', 'unknown')}' missing resource limits",
                                                    "priority": "medium",
                                                    "tool": "kubernetes",
                                                    "source": "existing_config"
                                                })
                except Exception as e:
                    self.logger.warning(f"Could not parse {k8s_file}: {e}")
        
        return issues

    async def _analyze_infrastructure_config(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing infrastructure configuration files"""
        issues = []
        
        # Terraform
        terraform_files = [
            project_path / "terraform.tf",
            project_path / "terraform.tfvars"
        ]
        
        for tf_file in terraform_files:
            if tf_file.exists():
                try:
                    with open(tf_file, 'r') as f:
                        content = f.read()
                        # Check for common issues
                        if "provider" in content and "region" not in content:
                            issues.append({
                                "type": "infrastructure_issue",
                                "file": str(tf_file),
                                "description": "Terraform configuration missing region specification",
                                "priority": "medium",
                                "tool": "terraform",
                                "source": "existing_config"
                            })
                except Exception as e:
                    self.logger.warning(f"Could not parse {tf_file}: {e}")
        
        # CloudFormation
        cloudformation_files = [
            project_path / "cloudformation.yaml",
            project_path / "cloudformation.yml"
        ]
        
        for cf_file in cloudformation_files:
            if cf_file.exists():
                try:
                    with open(cf_file, 'r') as f:
                        cf_config = yaml.safe_load(f)
                        if cf_config:
                            # Check for basic structure
                            if "Resources" not in cf_config:
                                issues.append({
                                    "type": "infrastructure_issue",
                                    "file": str(cf_file),
                                    "description": "CloudFormation template missing Resources section",
                                    "priority": "high",
                                    "tool": "cloudformation",
                                    "source": "existing_config"
                                })
                except Exception as e:
                    self.logger.warning(f"Could not parse {cf_file}: {e}")
        
        return issues

    async def _analyze_existing_logs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing log files for issues"""
        issues = []
        
        # Look for log files
        log_files = [
            "deployment.log", "ci.log", "build.log",
            "error.log", "app.log", "server.log"
        ]
        
        for log_file in log_files:
            log_path = project_path / log_file
            if log_path.exists():
                try:
                    with open(log_path, 'r') as f:
                        content = f.read()
                        # Check for common error patterns
                        if "error" in content.lower() or "failed" in content.lower():
                            issues.append({
                                "type": "log_analysis",
                                "file": str(log_path),
                                "description": "Log file contains error or failure messages",
                                "priority": "medium",
                                "tool": "log_analysis",
                                "source": "existing_logs"
                            })
                except Exception as e:
                    self.logger.warning(f"Could not read {log_path}: {e}")
        
        return issues

    async def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Suggest fixes based on existing configuration and logs"""
        fixes = []

        for issue in issues:
            if issue["type"] == "ci_config_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix CI/CD configuration",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_config"
                })
            elif issue["type"] == "security_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Address security concern",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_config"
                })
            elif issue["type"] == "deployment_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix deployment configuration",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_config"
                })

        return fixes
