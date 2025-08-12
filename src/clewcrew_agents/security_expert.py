#!/usr/bin/env python3
"""
Security Expert Agent for clewcrew
"""

import re
from pathlib import Path
from typing import List, Dict, Any

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
            recommendations=recommendations
        )

    def _find_line_number(self, content: str, pattern: str) -> int:
        """Find the line number where a pattern occurs"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return i
        return 0

    async def suggest_fixes(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest fixes for security issues"""
        fixes = []
        
        for issue in issues:
            if issue["type"] == "security_vulnerability":
                fixes.append({
                    "issue": issue,
                    "fix": "Replace hardcoded credential with environment variable",
                    "example": f"# Replace: {issue['pattern']}\n# With: os.getenv('CREDENTIAL_KEY')",
                    "priority": "high"
                })
            elif issue["type"] == "subprocess_vulnerability":
                fixes.append({
                    "issue": issue,
                    "fix": "Replace subprocess call with native Python operation",
                    "example": "# Replace subprocess.call with native Python libraries",
                    "priority": "critical"
                })
        
        return fixes

    def calculate_risk_score(self, issues: List[Dict[str, Any]]) -> float:
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
