# Modular LLM Solution Analyzer

A comprehensive, extensible framework for comparing and analyzing AI-generated code solutions using a plugin-based architecture.

## 🎯 What It Does

This modular analyzer evaluates 4 different LLM solutions for the "Safe File Deletion Identifier" prompt across multiple configurable dimensions:

- **Performance Analysis** (25% weight) - Algorithm efficiency, optimization techniques, complexity analysis
- **Readability Analysis** (20% weight) - Code clarity, comments, structure, naming conventions
- **Prompt Adherence Analysis** (25% weight) - Requirements compliance and completeness
- **Code Quality Analysis** (15% weight) - Error handling, best practices, type safety
- **Documentation Analysis** (10% weight) - README quality, inline docs, help systems
- **Security Analysis** (10% weight) - Input validation, dangerous operations, security practices *(extensible example)*

## 🚀 Quick Start

### Interactive Menu
```bash
```

### Direct Commands
```bash
# Standard modular analysis
python modular_analyzer.py

# Enhanced analysis with security module demonstration
python demo_modular_system.py

# Generate dashboard from existing analysis
python dashboard_generator.py
```

## 📁 Generated Files

Each analysis run creates:

1. **`enhanced_analysis_dashboard.html`** - Interactive web dashboard with charts and detailed breakdowns
2. **`enhanced_analysis_report.md`** - Comprehensive markdown report with modular scoring
3. **`enhanced_analysis_summary.csv`** - CSV data for spreadsheet analysis
4. **`enhanced_analysis_detailed.json`** - Structured data for programmatic access

## 🎯 Current Results Summary

Based on the latest modular analysis:

| Rank | LLM | Score | Key Strengths |
|------|-----|-------|---------------|
| 🥇 1 | LLM4 | 84.8 | Excellent code quality (95.0) & comprehensive documentation |
| 🥈 2 | LLM3 | 80.5 | Perfect readability (100.0) & documentation |
| 🥉 3 | LLM1 | 80.3 | Best performance optimization (74.0) |
| 4 | LLM2 | 73.0 | Simple, functional implementation |

## 🏗️ Modular Architecture

The system uses a plugin-based architecture for easy extensibility:

### Core Components
- **`analysis/base.py`** - Abstract base classes and registry system
- **`modular_analyzer.py`** - Main orchestrator using plugin architecture  
- **`dashboard_generator.py`** - Interactive HTML dashboard generator
- **`demo_modular_system.py`** - Complete demonstration with extensibility examples

### Analysis Modules (Plugins)
- **`analysis/performance.py`** - Algorithmic efficiency evaluation
- **`analysis/readability.py`** - Code clarity and maintainability assessment
- **`analysis/prompt_adherence.py`** - Requirements compliance checking
- **`analysis/code_quality.py`** - Best practices and error handling analysis
- **`analysis/documentation.py`** - Documentation quality evaluation
- **Security Analysis** - Extensible example for security practices

## 🔧 How It Works

The modular analyzer:

1. **Discovers analysis modules** using the plugin registry system
2. **Reads all solution files** (.ps1, .bat, .md, etc.) from each LLM folder
3. **Runs each enabled analyzer** with configurable weights
4. **Aggregates scores** using weighted methodology
5. **Generates multiple output formats** (Markdown, CSV, JSON, HTML)
6. **Creates interactive dashboards** with Chart.js visualizations

## 📊 Scoring Methodology

- **Objective criteria**: Each module uses specific, measurable factors
- **Plugin consistency**: All analyzers implement the same `BaseAnalyzer` interface
- **Configurable weights**: Adjust importance of different analysis dimensions
- **Detailed explanations**: Every score includes reasoning and supporting evidence
- **Extensible scoring**: Easy to add new analysis types without changing core code

## 🎮 Interactive Dashboard Features

- **Multi-dimensional comparison** with radar charts and bar graphs
- **Detailed breakdowns** for each analysis module
- **Category-specific rankings** showing strengths and weaknesses
- **Code metrics visualization** (lines, files, complexity)
- **Expandable details** for deep-dive analysis
- **Responsive design** works on desktop and mobile

## 🚀 Extending the System

Adding new analysis modules is simple:

```python
from analysis.base import BaseAnalyzer, AnalysisScore

class YourAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(
            name="Your Analysis",
            description="What your analyzer does",
            weight=0.15  # 15% of total score
        )
    
    def analyze(self, files, llm_name, prompt_requirements):
        # Your analysis logic here
        return AnalysisScore(score=85.0, notes=["Your analysis results"])

# Register and run
analyzer = ModularLLMAnalyzer(workspace_path)
analyzer.registry.register(YourAnalyzer())
results = analyzer.analyze_all_solutions()
```

## 📈 Potential Extensions

The modular architecture enables easy addition of:
- **Runtime Performance** - Actual execution benchmarking
- **Security Analysis** - Vulnerability and safety assessment  
- **Maintainability** - Code complexity and refactoring metrics
- **Testing Coverage** - Unit test quality and coverage analysis
- **Compliance** - Organizational standard adherence

The analyzer is designed to be fair, objective, and easily extensible for different types of code comparison tasks.
