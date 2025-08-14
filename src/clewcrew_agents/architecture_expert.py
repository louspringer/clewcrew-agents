#!/usr/bin/env python3
"""
Architecture Expert Agent for clewcrew

CRITICAL: This agent analyzes existing architecture documentation and code structure.
It does NOT run expensive analysis tools.
"""

from pathlib import Path
from typing import Any

from .base_expert import BaseExpert, HallucinationResult


class ArchitectureExpert(BaseExpert):
    """Architecture expert that analyzes existing documentation and code structure"""

    async def detect_hallucinations(self, project_path: Path) -> HallucinationResult:
        """Analyze existing architecture data and provide recommendations"""
        hallucinations = []
        recommendations = []

        # Look for existing architecture documentation and structure
        arch_data = await self._find_existing_architecture_data(project_path)
        
        if not arch_data:
            recommendations = [
                "No existing architecture documentation found",
                "Consider creating architecture decision records (ADRs)",
                "Document system components and their relationships",
                "Create dependency diagrams and system maps"
            ]
            return HallucinationResult(
                hallucinations=[],
                confidence=0.3,
                recommendations=recommendations
            )

        # Analyze architecture documentation
        doc_issues = await self._analyze_architecture_docs(project_path)
        hallucinations.extend(doc_issues)

        # Analyze code structure
        structure_issues = await self._analyze_code_structure(project_path)
        hallucinations.extend(structure_issues)

        # Analyze dependency configuration
        dependency_issues = await self._analyze_dependencies(project_path)
        hallucinations.extend(dependency_issues)

        # Generate recommendations based on existing data
        if hallucinations:
            recommendations = [
                "Review and improve architecture documentation",
                "Address structural issues in code organization",
                "Update dependency management and versioning",
                "Consider implementing architectural patterns",
                "Document system boundaries and interfaces"
            ]
        else:
            recommendations = [
                "Architecture appears well-documented based on existing files",
                "Continue monitoring architectural decisions",
                "Consider implementing advanced architectural patterns",
                "Add performance and scalability documentation"
            ]

        confidence = self.calculate_confidence(hallucinations)

        return HallucinationResult(
            hallucinations=hallucinations,
            confidence=confidence,
            recommendations=recommendations,
        )

    async def _find_existing_architecture_data(self, project_path: Path) -> list[Path]:
        """Find existing architecture documentation and structure files"""
        arch_files = []
        
        # Architecture documentation
        doc_files = [
            "README.md", "ARCHITECTURE.md", "DESIGN.md", "docs/",
            "adr/", "decisions/", "architecture/", "design/"
        ]
        
        for doc_file in doc_files:
            file_path = project_path / doc_file
            if file_path.exists():
                if file_path.is_dir():
                    arch_files.extend(file_path.rglob("*.md"))
                else:
                    arch_files.append(file_path)
        
        # Code structure files
        structure_files = [
            "pyproject.toml", "setup.py", "requirements.txt",
            "src/", "lib/", "app/", "core/"
        ]
        
        for structure_file in structure_files:
            file_path = project_path / structure_file
            if file_path.exists():
                if file_path.is_dir():
                    arch_files.extend(file_path.rglob("*.py"))
                else:
                    arch_files.append(file_path)
        
        return arch_files

    async def _analyze_architecture_docs(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing architecture documentation"""
        issues = []
        
        # Check for README
        readme_file = project_path / "README.md"
        if readme_file.exists():
            try:
                with open(readme_file, 'r') as f:
                    content = f.read()
                    if "architecture" not in content.lower() and "design" not in content.lower():
                        issues.append({
                            "type": "documentation_issue",
                            "file": str(readme_file),
                            "description": "README missing architecture/design section",
                            "priority": "medium",
                            "tool": "documentation",
                            "source": "existing_docs"
                        })
            except Exception as e:
                self.logger.warning(f"Could not read {readme_file}: {e}")
        
        # Check for architecture docs directory
        docs_dir = project_path / "docs"
        if docs_dir.exists():
            arch_docs = list(docs_dir.rglob("*architecture*"))
            arch_docs.extend(docs_dir.rglob("*design*"))
            if not arch_docs:
                issues.append({
                    "type": "documentation_issue",
                    "file": str(docs_dir),
                    "description": "Docs directory missing architecture/design documentation",
                    "priority": "medium",
                    "tool": "documentation",
                    "source": "existing_docs"
                })
        
        return issues

    async def _analyze_code_structure(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing code structure"""
        issues = []
        
        # Check for src directory structure
        src_dir = project_path / "src"
        if src_dir.exists():
            # Check for proper package structure
            py_files = list(src_dir.rglob("*.py"))
            if py_files:
                # Check for __init__.py files
                init_files = list(src_dir.rglob("__init__.py"))
                if len(init_files) < len(set(f.parent for f in py_files)):
                    issues.append({
                        "type": "structure_issue",
                        "file": str(src_dir),
                        "description": "Some Python packages missing __init__.py files",
                        "priority": "medium",
                        "tool": "code_structure",
                        "source": "existing_structure"
                    })
        else:
            # Check for flat structure
            py_files = list(project_path.rglob("*.py"))
            if len(py_files) > 10:  # Arbitrary threshold
                issues.append({
                    "type": "structure_issue",
                    "file": str(project_path),
                    "description": "Consider organizing code into src/ directory structure",
                    "priority": "low",
                    "tool": "code_structure",
                    "source": "existing_structure"
                })
        
        return issues

    async def _analyze_dependencies(self, project_path: Path) -> list[dict[str, Any]]:
        """Analyze existing dependency configuration"""
        issues = []
        
        # Check pyproject.toml
        pyproject_file = project_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                    if "dependencies" in content:
                        # Check for version pinning
                        if ">=" in content and "==" not in content:
                            issues.append({
                                "type": "dependency_issue",
                                "file": str(pyproject_file),
                                "description": "Consider pinning dependency versions for reproducibility",
                                "priority": "medium",
                                "tool": "dependency_management",
                                "source": "existing_config"
                            })
            except Exception as e:
                self.logger.warning(f"Could not read {pyproject_file}: {e}")
        
        # Check requirements.txt
        requirements_file = project_path / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    content = f.read()
                    if ">=" in content and "==" not in content:
                        issues.append({
                            "type": "dependency_issue",
                            "file": str(requirements_file),
                            "description": "Consider pinning dependency versions for reproducibility",
                            "priority": "medium",
                            "tool": "dependency_management",
                            "source": "existing_config"
                        })
            except Exception as e:
                self.logger.warning(f"Could not read {requirements_file}: {e}")
        
        return issues

    async def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Suggest fixes based on existing architecture data"""
        fixes = []

        for issue in issues:
            if issue["type"] == "documentation_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Improve architecture documentation",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_docs"
                })
            elif issue["type"] == "structure_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Improve code structure",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_structure"
                })
            elif issue["type"] == "dependency_issue":
                fixes.append({
                    "issue": issue,
                    "fix": "Fix dependency management",
                    "description": issue["description"],
                    "priority": issue["priority"],
                    "source": "existing_config"
                })

        return fixes
