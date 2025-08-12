# 🤖 clewcrew-agents

**Expert agent framework for the clewcrew portfolio.**

clewcrew-agents provides AI-powered expert agents for different domains including security, code quality, testing, build, architecture, and model validation. Each agent specializes in detecting specific types of hallucinations in code.

## 🚀 Quick Start

### Installation

```bash
# Install with pip
pip install clewcrew-agents

# Install with UV
uv add clewcrew-agents
```

### Basic Usage

```python
from clewcrew_agents import SecurityExpert, BaseExpert

# Initialize a security expert
security_expert = SecurityExpert()

# Detect security hallucinations
result = await security_expert.detect_hallucinations("/path/to/project")

# Check results
print(f"Found {len(result.hallucinations)} security issues")
print(f"Confidence: {result.confidence}")
print(f"Recommendations: {result.recommendations}")

# Get fix suggestions
fixes = await security_expert.suggest_fixes(result.hallucinations)
for fix in fixes:
    print(f"Fix: {fix['fix']}")
    print(f"Priority: {fix['priority']}")
```

## 🏗️ Architecture

### Core Components

- **BaseExpert**: Abstract base class for all expert agents
- **HallucinationResult**: Standardized result format for all agents
- **SecurityExpert**: Specialized agent for security vulnerability detection

### Agent Capabilities

Each expert agent provides:

- **Hallucination Detection**: Domain-specific issue identification
- **Confidence Scoring**: Reliability assessment of findings
- **Recommendations**: Actionable advice for issue resolution
- **Fix Suggestions**: Specific solutions for detected problems
- **Risk Assessment**: Priority and severity evaluation

## 🔧 Dependencies

- **clewcrew-common**: Shared utilities and patterns
- **clewcrew-framework**: Base classes and abstractions
- **pydantic**: Data validation and settings management

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/clewcrew_agents --cov-report=html
```

## 📚 Documentation

- [API Reference](https://github.com/louspringer/clewcrew-agents#readme)
- [Agent Development Guide](https://github.com/louspringer/clewcrew-agents#agent-development)
- [Examples](https://github.com/louspringer/clewcrew-agents#examples)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/louspringer/clewcrew-agents/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to deploy expert agents for the clewcrew revolution!** 🤖✨
