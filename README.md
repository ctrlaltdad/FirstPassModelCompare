# Modular LLM Solution Analyzer

A comprehensive, extensible framework for comparing and an## 📊 Example Results

Based on analysis with 7-dimensional scoring (your results will vary based on your LLM solutions):

| Rank | LLM | Score | Key Strengths |
|------|-----|-------|---------------|
| 🥇 1 | LLM1 | 83.6 | Excellent security & requirements compliance |
| 🥈 2 | LLM4 | 83.1 | Outstanding code quality & comprehensive documentation |
| 🥉 3 | LLM3 | 81.9 | Perfect readability & documentation |
| 4 | LLM2 | 75.9 | Strong requirements traceability & security |

*Rankings change based on your weight preferences - use the interactive controls to explore different scenarios!*enerated code solutions using a plugin-based architecture with interactive weight controls and real-time analysis.

## 🚀 Getting Started

### Step 1: Prepare Your LLM Solutions
1. **Create LLM folders**: Create up to 4 folders named `llm1`, `llm2`, `llm3`, `llm4`
2. **Add your solutions**: Place each LLM's generated files in their respective folder:
   - Code files (.ps1, .py, .js, etc.)
   - Documentation files (README.md, help files)
   - Any supporting files (batch scripts, config files)
3. **Update the prompt**: Edit the prompt in your analysis files to match what you provided to the LLMs

### Step 2: Run the Analysis
```bash
python modular_analyzer.py
```

### Step 3: View Results
- Interactive dashboard opens automatically in your browser
- Adjust weights in real-time to explore different analysis scenarios
- Export reports in multiple formats (CSV, JSON, Markdown)

### Example Structure:
```
your-project/
├── llm1/           # llm1's solution
│   ├── script.py
│   └── README.md
├── llm2/           # llm2's solution
│   ├── app.js
│   └── docs.md
├── llm3/           # llm3's solution
│   └── solution.py
└── llm4/           # llm4's solution
    ├── main.py
    └── requirements.txt
```

## 🎯 What It Does

This modular analyzer evaluates up to 4 different LLM solutions across **7 configurable analysis dimensions**:

- **Requirements Traceability Analysis** (25% weight) - Requirements compliance and completeness tracking
- **Performance Analysis** (20% weight) - Algorithm efficiency, optimization techniques, complexity analysis  
- **Readability Analysis** (15% weight) - Code clarity, comments, structure, naming conventions
- **Security Analysis** (15% weight) - Input validation, dangerous operations, security practices
- **Adaptability Analysis** (10% weight) - Solution flexibility, configurability, and extensibility
- **Code Quality Analysis** (10% weight) - Error handling, best practices, type safety
- **Documentation Analysis** (5% weight) - README quality, inline docs, help systems

## ✨ Key Features

### 🎛️ **Interactive Weight Controls**
- **Smart Redistribution**: Weights automatically balance to exactly 100% when adjusted
- **Real-time Updates**: Charts, rankings, and scores update instantly as you change weights
- **Preset Configurations**: 6 built-in weight presets for different analysis scenarios:
  - **Balanced**: Equal emphasis across all criteria
  - **Security First**: Prioritizes security and requirements compliance
  - **Performance Focus**: Emphasizes speed and adaptability  
  - **Enterprise**: Documentation and requirements heavy
  - **Agile Development**: Adaptability and code quality focused
  - **Maintenance**: Readability and documentation priority

### 🎨 **Enhanced User Experience**
- **Collapsible Advanced Controls**: Weight controls start collapsed for cleaner interface
- **Modal Guidance System**: Interactive help with tips and preset explanations
- **Visual Feedback**: Smooth animations and color-coded analysis sections
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🎮 Quick Start

### Simple One-Command Analysis
```bash
python modular_analyzer.py
```

This will:
- ✅ Analyze all LLM solutions in your workspace
- ✅ Generate comprehensive reports with interactive dashboard
- ✅ Open results in browser with real-time weight controls
- ✅ Provide smart weight redistribution and preset configurations

## 📁 Generated Files

Each analysis run creates:

1. **`analysis_dashboard.html`** - Interactive web dashboard with charts and detailed breakdowns
2. **`analysis_report.md`** - Comprehensive markdown report with modular scoring
3. **`analysis_summary.csv`** - CSV data for spreadsheet analysis
4. **`analysis_detailed.json`** - Structured data for programmatic access

## 🎯 Current Results Summary

Based on the latest modular analysis with 7-dimensional scoring:

| Rank | LLM | Score | Key Strengths |
|------|-----|-------|---------------|
| 🥇 1 | LLM1 | 83.6 | Excellent security (100.0) & requirements compliance (99.5) |
| 🥈 2 | LLM4 | 83.1 | Outstanding code quality (95.0) & comprehensive documentation (100.0) |
| � 3 | LLM3 | 81.9 | Perfect readability (100.0) & documentation (100.0) |
| 4 | LLM2 | 75.9 | Strong requirements traceability (98.9) & security (94.0) |

*Rankings may change based on your weight preferences - use the interactive controls to explore different scenarios!*

## 🏗️ Modular Architecture

The system uses a plugin-based architecture for easy extensibility:

### Core Components
- **`analysis/base.py`** - Abstract base classes and registry system
- **`modular_analyzer.py`** - Main orchestrator using plugin architecture  
- **`dashboard_generator.py`** - Interactive HTML dashboard generator with real-time controls

### Analysis Modules (Plugins)
- **`analysis/performance.py`** - Algorithmic efficiency evaluation
- **`analysis/readability.py`** - Code clarity and maintainability assessment
- **`analysis/requirements_traceability.py`** - Requirements compliance and traceability matrix
- **`analysis/code_quality.py`** - Best practices and error handling analysis
- **`analysis/documentation.py`** - Documentation quality evaluation
- **`analysis/security.py`** - Security practices and vulnerability assessment
- **`analysis/adaptability.py`** - Solution flexibility and configurability analysis

## 🔧 How It Works

The modular analyzer:

1. **Discovers analysis modules** using the plugin registry system
2. **Reads all solution files** (.ps1, .bat, .md, etc.) from each LLM folder
3. **Runs each enabled analyzer** with configurable weights
4. **Aggregates scores** using weighted methodology
5. **Generates multiple output formats** (Markdown, CSV, JSON, HTML)
6. **Creates interactive dashboards** with Chart.js visualizations

## 📊 Scoring Methodology

- **Objective criteria**: Each module uses specific, measurable factors with detailed rubrics
- **Plugin consistency**: All analyzers implement the same `BaseAnalyzer` interface
- **Interactive weight adjustment**: Real-time customization with automatic redistribution
- **Smart weight management**: Ensures weights always total exactly 100%
- **Detailed explanations**: Every score includes reasoning and supporting evidence
- **Extensible scoring**: Easy to add new analysis types without changing core code
- **Live recalculation**: Rankings and metrics update instantly when weights change

## 🎮 Interactive Dashboard Features

### 📊 **Real-time Analysis Controls**
- **Interactive Weight Sliders**: Adjust importance of each analysis dimension with live updates
- **Smart Weight Distribution**: Automatic proportional redistribution ensuring 100% total
- **Preset Weight Configurations**: Quick-apply common analysis scenarios
- **Modal Help System**: Comprehensive guidance for weight selection strategies

### 📈 **Visual Analytics**
- **Multi-dimensional comparison** with radar charts and bar graphs
- **Live Score Updates**: Rankings, highest/average scores update instantly with weight changes
- **Color-coded Analysis Sections** for easy identification of strengths/weaknesses
- **Category-specific Rankings** showing detailed performance breakdown
- **Code Metrics Visualization** (lines, files, complexity)

### 🎨 **User Experience**
- **Collapsible Advanced Controls**: Clean interface with progressive disclosure
- **Expandable Detail Sections** for deep-dive analysis
- **Smooth Animations** with visual feedback for all interactions
- **Responsive Design** optimized for desktop and mobile
- **Advanced Badge System** clearly marking sophisticated features

## 🚀 Extending the System

Adding new analysis modules is simple:

```python
from analysis.base import BaseAnalyzer, AnalysisScore

class YourCustomAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(
            name="Your Custom Analysis",
            description="Description of what your analyzer evaluates",
            weight=0.15  # 15% of total score
        )
    
    def analyze(self, files, llm_name, prompt_requirements):
        # Your custom analysis logic here
        score = 85.0  # Calculate your score
        notes = ["Your analysis findings and reasoning"]
        return AnalysisScore(score=score, notes=notes)

# Usage example:
workspace_path = r"your\workspace\path"
analyzer = ModularLLMAnalyzer(workspace_path)
analyzer.registry.register(YourCustomAnalyzer())
results = analyzer.analyze_all_solutions()
```

## 📈 Potential Extensions

The modular architecture enables easy addition of:
- **Runtime Performance** - Actual execution benchmarking with timing analysis
- **Advanced Security Analysis** - Vulnerability scanning and threat modeling
- **Maintainability Metrics** - Code complexity, cyclomatic complexity, and refactoring indicators
- **Testing Coverage** - Unit test quality, coverage analysis, and test completeness
- **Compliance Analysis** - Organizational standard adherence and regulatory compliance
- **Cross-platform Compatibility** - Multi-OS testing and environment analysis
- **Memory Usage Analysis** - Resource consumption and optimization opportunities

### 🎛️ **Weight Configuration Guide**

Use different weight presets based on your analysis goals:

- **Balanced** (Default): Equal weight for comprehensive analysis
- **Security First**: When security and compliance are paramount
- **Performance Focus**: For high-performance applications requiring speed
- **Enterprise**: Documentation-heavy environments with strict requirements
- **Agile Development**: Fast iteration with emphasis on adaptability
- **Maintenance**: Long-term code maintenance and readability priority

The analyzer is designed to be fair, objective, and easily extensible for different types of code comparison tasks with real-time customization capabilities.
