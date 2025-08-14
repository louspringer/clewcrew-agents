"""
Tests for the SecurityExpert agent.
"""

import pytest

from clewcrew_agents.security_expert import SecurityExpert


class TestSecurityExpert:
    """Test the SecurityExpert class."""

    @pytest.fixture
    def security_expert(self):
        """Create a test security expert."""
        return SecurityExpert()

    def test_security_expert_initialization(self, security_expert):
        """Test security expert initialization."""
        assert security_expert.component_name == "SecurityExpert"
        assert security_expert.logger is not None

    @pytest.mark.asyncio
    async def test_detect_hallucinations_no_issues(self, security_expert, tmp_path):
        """Test hallucination detection with no security issues."""
        # Create a simple Python file with no security issues
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
import os
import json

def main():
    api_key = os.getenv('API_KEY')
    print("Hello, World!")
"""
        )

        result = await security_expert.detect_hallucinations(tmp_path)

        assert result.hallucinations == []
        assert result.confidence == 0.9
        assert "No security issues detected" in result.recommendations

    @pytest.mark.asyncio
    async def test_detect_hallucinations_with_credentials(
        self, security_expert, tmp_path
    ):
        """Test hallucination detection with hardcoded credentials."""
        # Create a Python file with hardcoded credentials
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
import os

def main():
    api_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef"
    print("Using API key:", api_key)
"""
        )

        result = await security_expert.detect_hallucinations(tmp_path)

        assert len(result.hallucinations) == 1
        assert result.hallucinations[0]["type"] == "security_vulnerability"
        assert result.hallucinations[0]["priority"] == "high"
        assert "sk-" in result.hallucinations[0]["pattern"]
        assert result.confidence < 0.9  # Should be lower due to security issues

    @pytest.mark.asyncio
    async def test_detect_hallucinations_with_subprocess(
        self, security_expert, tmp_path
    ):
        """Test hallucination detection with subprocess usage."""
        # Create a Python file with subprocess usage
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """
import subprocess

def main():
    result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
    print(result.stdout)
"""
        )

        result = await security_expert.detect_hallucinations(tmp_path)

        assert len(result.hallucinations) == 1
        assert result.hallucinations[0]["type"] == "subprocess_vulnerability"
        assert result.hallucinations[0]["priority"] == "critical"
        assert "subprocess" in result.hallucinations[0]["pattern"]

    def test_calculate_risk_score(self, security_expert):
        """Test risk score calculation."""
        # Test with no issues
        no_issues = []
        assert security_expert.calculate_risk_score(no_issues) == 0.0

        # Test with low priority issues
        low_issues = [{"priority": "low"}]
        assert security_expert.calculate_risk_score(low_issues) == 1.0

        # Test with high priority issues
        high_issues = [{"priority": "high"}]
        assert security_expert.calculate_risk_score(high_issues) == 5.0

        # Test with critical priority issues
        critical_issues = [{"priority": "critical"}]
        assert security_expert.calculate_risk_score(critical_issues) == 10.0

    @pytest.mark.asyncio
    async def test_suggest_fixes(self, security_expert):
        """Test fix suggestions."""
        issues = [
            {
                "type": "security_vulnerability",
                "pattern": "sk-1234567890abcdef",
                "priority": "high",
            },
            {
                "type": "subprocess_vulnerability",
                "pattern": "subprocess.run",
                "priority": "critical",
            },
        ]

        fixes = await security_expert.suggest_fixes(issues)

        assert len(fixes) == 2
        assert (
            fixes[0]["fix"] == "Replace hardcoded credential with environment variable"
        )
        assert fixes[1]["fix"] == "Replace subprocess call with native Python operation"
        assert fixes[0]["priority"] == "high"
        assert fixes[1]["priority"] == "critical"


if __name__ == "__main__":
    pytest.main([__file__])
