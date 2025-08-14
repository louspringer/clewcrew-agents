#!/usr/bin/env python3
"""
Test Expert Agent for clewcrew

CRITICAL: This agent analyzes existing test outputs and configuration.
It does NOT run expensive testing tools.
"""

from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

from .base_expert import BaseExpert, HallucinationResult


class TestExpert(BaseExpert):
    """Test expert that analyzes existing test outputs and configuration"""

    async def detect_hallucinations(self, project_path: Path) -> HallucinationResult:
        """Analyze existing test data and provide recommendations"""
        hallucinations = []
        recommendations = []

        # Look for existing test configuration and outputs
        test_data = await self._find_existing_test_data(project_path)
        
        if not test_data:
            recommendations = [
                "No existing test configuration found",
                "Consider setting up pytest with proper configuration",
                "Implement test coverage reporting",
                "Set up automated testing in CI/CD pipeline"
            ]
            return HallucinationResult(
                hallucinations=[],
                confidence=0.3,
                recommendations=recommendations
            )

        # Analyze test configuration
        config_issues = await self._analyze_test_config(project_path)
        hallucinations.extend(config_issues)

        # Analyze test outputs
        output_issues = await self._analyze_test_outputs(project_path)
        hallucinations.extend(output_issues)

        # Analyze coverage reports
        coverage_issues = await self._analyze_coverage_reports(project_path)
        hallucinations.extend(coverage_issues)

        # Generate recommendations based on existing data
        if hallucinations:
            recommendations = [
                "Review and fix test configuration issues",
                "Address failing tests identified in outputs",
                "Improve test coverage based on reports",
                "Ensure tests are properly integrated in CI/CD",
                "Consider adding more comprehensive test suites"
            ]
        else:
            recommendations = [
                "Test configuration appears sound based on existing files",
                "Continue monitoring test performance and coverage",
                "Consider implementing advanced testing strategies",
                "Add performance and load testing if applicable"
            ]

        confidence = self.calculate_confidence(hallucinations)

        return HallucinationResult(
            hallucinations=hallucinations,
            confidence=confidence,
            recommendations=recommendations,
        )

    async def _find_existing_test_data(self, project_path: Path) -> list[Path]:
        """Find existing test configuration and output files"""
        test_files = []
        
        # Test configuration files
        config_files = [
            "pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini",
            ".coveragerc", "coverage.ini"
        ]
        
        for config_file in config_files:
            file_path = project_path / config_file
            if file_path.exists():
                test_files.append(file_path)
        
        # Test output files
        output_files = [
            "coverage.xml", "htmlcov/", ".coverage",
            "test-results.xml", "junit.xml", "test-report.xml"
        ]
        
        for output_file in output_files:
            file_path = project_path / output_file
            if file_path.exists():
                test_files.append(file_path)
        
        # Test directories
        test_dirs = ["tests/", "test/", "tests_*/"]
        for test_dir in test_dirs:
            dir_path = project_path / test_dir
            if dir_path.exists():
                test_files.extend(dir_path.rglob("*.py"))
        
        return test_files

    async def _analyze_test_config(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing test configuration files"""
        issues = []
        
        # Check pytest configuration
        pytest_files = [
            project_path / "pytest.ini",
            project_path / "pyproject.toml"
        ]
        
        for pytest_file in pytest_files:
            if pytest_file.exists():
                try:
                    with open(pytest_file, 'r') as f:
                        content = f.read()
                        if "pytest" in content.lower():
                            # Check for common configuration issues
                            if "testpaths" not in content and "python_files" not in content:
                                issues.append({
                                    "type": "test_config_issue",
                                    "file": str(pytest_file),
                                    "description": "Pytest configuration missing test discovery settings",
                                    "priority": "medium",
                                    "tool": "pytest",
                                    "source": "existing_config"
                                })
                            
                            # Check for coverage configuration
                            if "cov" not in content and "coverage" not in content:
                                issues.append({
                                    "type": "test_config_issue",
                                    "file": str(pytest_file),
                                    "description": "Pytest configuration missing coverage settings",
                                    "priority": "low",
                                    "tool": "pytest",
                                    "source": "existing_config"
                                })
                except Exception as e:
                    self.logger.warning(f"Could not parse {pytest_file}: {e}")
        
        return issues

    async def _analyze_test_outputs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing test output files"""
        issues = []
        
        # Check for test result files
        result_files = [
            project_path / "test-results.xml",
            project_path / "junit.xml",
            project_path / "test-report.xml"
        ]
        
        for result_file in result_files:
            if result_file.exists():
                try:
                    tree = ET.parse(result_file)
                    root = tree.getroot()
                    
                    # Check for test failures
                    failures = root.findall(".//failure") + root.findall(".//error")
                    if failures:
                        issues.append({
                            "type": "test_failure",
                            "file": str(result_file),
                            "description": f"Found {len(failures)} test failures in results",
                            "priority": "high",
                            "tool": "test_results",
                            "source": "existing_output"
                        })
                    
                    # Check for skipped tests
                    skipped = root.findall(".//skipped")
                    if skipped:
                        issues.append({
                            "type": "test_skipped",
                            "file": str(result_file),
                            "description": f"Found {len(skipped)} skipped tests",
                            "priority": "medium",
                            "tool": "test_results",
                            "source": "existing_output"
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Could not parse {result_file}: {e}")
        
        return issues

    async def _analyze_coverage_reports(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing coverage reports"""
        issues = []
        
        # Check coverage XML file
        coverage_xml = project_path / "coverage.xml"
        if coverage_xml.exists():
            try:
                tree = ET.parse(coverage_xml)
                root = tree.getroot()
                
                # Check overall coverage
                coverage_elem = root.find(".//coverage")
                if coverage_elem is not None:
                    line_rate = float(coverage_elem.get("line-rate", "0"))
                    if line_rate < 0.8:
                        issues.append({
                            "type": "coverage_low",
                            "file": str(coverage_xml),
                            "description": f"Test coverage is {line_rate:.1%}, below recommended 80%",
                            "priority": "medium",
                            "tool": "coverage",
                            "source": "existing_output"
                        })
                        
            except Exception as e:
                self.logger.warning(f"Could not parse {coverage_xml}: {e}")
        
        # Check HTML coverage directory
        htmlcov_dir = project_path / "htmlcov"
        if htmlcov_dir.exists():
            index_file = htmlcov_dir / "index.html"
            if index_file.exists():
                try:
                    with open(index_file, 'r') as f:
                        content = f.read()
                        if "coverage" in content.lower():
                            issues.append({
                                "type": "coverage_report",
                                "file": str(index_file),
                                "description": "HTML coverage report available for review",
                                "priority": "low",
                                "tool": "coverage",
                                "source": "existing_output"
                            })
                except Exception as e:
                    self.logger.warning(f"Could not read {index_file}: {e}")
        
        return issues

    async def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Suggest fixes based on existing test data"""
        fixes = []

        for issue in issues:
            if issue["type"] == "test_config_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix test configuration",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_config"
                })
            elif issue["type"] == "test_failure":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix failing tests",
                    "description": "Review and fix the failing tests identified in results",
                    "priority": issue["priority"],
                    "source": "existing_output"
                })
            elif issue["type"] == "coverage_low":
                fixes.append({
                    "issue": issue,
                    "fix": "Improve test coverage",
                    "description": f"Add more tests to reach {issue['description']}",
                    "priority": issue["priority"],
                    "source": "existing_output"
                })

        return fixes
