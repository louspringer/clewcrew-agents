#!/usr/bin/env python3
"""
Security Expert Agent for clewcrew
"""

import re
from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, HallucinationResult


class SecurityExpert(BaseExpert):
    """Security expert for detecting security hallucinations"""

    async def detect_hallucinations(self, project_path: Path) -> HallucinationResult:
        """Detect security-related hallucinations"""
        hallucinations = []
        recommendations = []

        # Check for hardcoded credentials
        credential_patterns = [
            r"sk-[a-zA-Z0-9]{48}",
            r"pk_[a-zA-Z0-9]{48}",
            r"AKIA[a-zA-Z0-9]{16}",
            r"ghp_[a-zA-Z0-9]{36}",
            r"gho_[a-zA-Z0-9]{36}",
        ]

        # Check for subprocess security vulnerabilities
        subprocess_patterns = [
            r"import subprocess",
            r"subprocess\.run",
            r"subprocess\.Popen",
            r"subprocess\.call",
            r"os\.system",
            r"os\.popen",
        ]

        # Check for security issues
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Check for hardcoded credentials
                for pattern in credential_patterns:
                    if re.search(pattern, content):
                        hallucinations.append(
                            {
                                "type": "security_vulnerability",
                                "file": str(py_file),
                                "pattern": pattern,
                                "priority": "high",
                                "description": f"Potential hardcoded credential found: {pattern}",
                                "line": self._find_line_number(content, pattern),
                            },
                        )

                # Check for subprocess vulnerabilities
                for pattern in subprocess_patterns:
                    if re.search(pattern, content):
                        hallucinations.append(
                            {
                                "type": "subprocess_vulnerability",
                                "file": str(py_file),
                                "pattern": pattern,
                                "priority": "critical",
                                "description": f"Subprocess usage detected: {pattern} - Security risk for command injection",
                                "line": self._find_line_number(content, pattern),
                            },
                        )

            except Exception as e:
                self.logger.warning(f"Could not read {py_file}: {e}")

        # Generate recommendations
        if hallucinations:
            recommendations = [
                "Use environment variables for credentials",
                "Implement secret management",
                "Replace subprocess calls with native Python operations",
                "Use Go/Rust for performance-critical shell operations",
                "Implement gRPC shell service for secure command execution",
            ]
        else:
            recommendations = [
                "No security issues detected",
                "Continue monitoring for security vulnerabilities",
                "Implement automated security scanning in CI/CD",
            ]

        confidence = self.calculate_confidence(hallucinations)

        return HallucinationResult(
            hallucinations=hallucinations,
            confidence=confidence,
            recommendations=recommendations,
        )

    def _find_line_number(self, content: str, pattern: str) -> int:
        """Find the line number where a pattern occurs"""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return i
        return 0

    async def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Suggest fixes for security issues"""
        fixes = []

        for issue in issues:
            if issue["type"] == "security_vulnerability":
                fixes.append(
                    {
                        "issue": issue,
                        "fix": "Replace hardcoded credential with environment variable",
                        "example": f"# Replace: {issue['pattern']}\n# With: os.getenv('CREDENTIAL_KEY')",
                        "priority": "high",
                    }
                )
            elif issue["type"] == "subprocess_vulnerability":
                fixes.append(
                    {
                        "issue": issue,
                        "fix": "Replace subprocess call with native Python operation",
                        "example": "# Replace subprocess.call with native Python libraries",
                        "priority": "critical",
                    }
                )

        return fixes

    def calculate_risk_score(self, issues: list[dict[str, Any]]) -> float:
        """Calculate overall risk score for security issues"""
        if not issues:
            return 0.0

        total_score = 0.0
        for issue in issues:
            if issue.get("priority") == "critical":
                total_score += 10.0
            elif issue.get("priority") == "high":
                total_score += 5.0
            elif issue.get("priority") == "medium":
                total_score += 2.0
            else:
                total_score += 1.0

        return min(10.0, total_score)

    # Quality Integration Methods
    async def generate_quality_metrics(self, project_path: Path) -> dict[str, Any]:
        """
        Generate security quality metrics for integration with quality system.
        
        Args:
            project_path: Path to the project to analyze
            
        Returns:
            Dictionary containing security quality metrics
        """
        # Run security analysis
        result = await self.detect_hallucinations(project_path)
        
        # Calculate security quality score
        if not result.hallucinations:
            quality_score = 100.0
        else:
            # Start with perfect score and penalize for issues
            quality_score = 100.0
            
            for hallucination in result.hallucinations:
                if hallucination.get("priority") == "critical":
                    quality_score -= 25.0  # Critical issues are very expensive
                elif hallucination.get("priority") == "high":
                    quality_score -= 15.0  # High priority issues are costly
                else:
                    quality_score -= 5.0   # Other issues have moderate cost
            
            # Ensure score doesn't go below 0
            quality_score = max(0.0, quality_score)
        
        return {
            "quality_score": quality_score,
            "issues_found": len(result.hallucinations),
            "critical_issues": len([h for h in result.hallucinations if h.get("priority") == "critical"]),
            "high_issues": len([h for h in result.hallucinations if h.get("priority") == "high"]),
            "security_issues": result.hallucinations,
            "recommendations": result.recommendations,
            "confidence": result.confidence,
            "risk_score": self.calculate_risk_score(result.hallucinations)
        }

    async def provide_quality_recommendations(self, project_path: Path) -> list[str]:
        """
        Provide security quality improvement recommendations.
        
        Args:
            project_path: Path to the project to analyze
            
        Returns:
            List of actionable security quality recommendations
        """
        result = await self.detect_hallucinations(project_path)
        return result.recommendations

    async def assess_quality_impact(self, changes: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Assess the impact of proposed changes on security quality.
        
        Args:
            changes: List of proposed changes
            
        Returns:
            Dictionary containing security impact assessment
        """
        # Analyze changes for security implications
        security_risks = []
        risk_level = "low"
        
        for change in changes:
            change_content = change.get("content", "")
            
            # Check for potential security issues in changes
            if any(pattern in change_content.lower() for pattern in ["password", "secret", "key", "token"]):
                security_risks.append("Potential credential exposure in changes")
                risk_level = "high"
            
            if any(pattern in change_content.lower() for pattern in ["subprocess", "os.system", "eval", "exec"]):
                security_risks.append("Potential command injection risk in changes")
                risk_level = "critical"
        
        return {
            "quality_impact": "security_assessment",
            "risk_level": risk_level,
            "security_risks": security_risks,
            "recommendations": [
                "Review all changes for security implications",
                "Implement security code review process",
                "Use automated security scanning tools"
            ]
        }

    def get_quality_metric_name(self) -> str:
        """Get the name of the security quality metric."""
        return "security"

    def get_quality_metric_weight(self) -> float:
        """Get the weight of the security quality metric."""
        return 3.0  # Security is highest priority
