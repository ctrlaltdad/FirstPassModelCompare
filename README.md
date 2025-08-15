# LLM Solution Analyzer

An automated tool for comparing and analyzing LLM-generated code solutions across multiple criteria.

## 🎯 What It Does

This analyzer evaluates 4 different LLM solutions for the "Safe File Deletion Identifier" prompt across:

- **Performance** (25% weight) - Algorithm efficiency, optimization techniques
- **Readability** (20% weight) - Code clarity, comments, structure  
- **Prompt Adherence** (25% weight) - How well it follows the original requirements
- **Code Quality** (15% weight) - Error handling, best practices, maintainability
- **Documentation** (10% weight) - README files, inline docs, examples
- **Feature Completeness** (5% weight) - Extra features beyond requirements

## 🚀 Quick Start

### Option 1: Run Analysis + View Results
```bash
view_results.bat
```
This will run the analysis and automatically open the interactive dashboard.

### Option 2: Run Analysis Only
```bash
python analyze_llm_solutions.py
```

### Option 3: View Last Results
Just open `analysis_dashboard.html` in your browser.

## 📁 Generated Files

Each analysis run creates:

1. **`analysis_dashboard.html`** - Interactive web dashboard with charts and rankings
2. **`analysis_report.md`** - Detailed markdown report with scoring breakdowns
3. **`analysis_summary.csv`** - CSV data suitable for spreadsheet analysis

## 🎯 Current Results Summary

Based on the latest analysis:

| Rank | LLM | Score | Strength |
|------|-----|-------|----------|
| 🥇 1 | LLM4 | 87.9 | Best Overall & Code Quality |
| 🥈 2 | LLM3 | 83.6 | Best Documentation & Readability |
| 🥉 3 | LLM1 | 81.9 | Best Performance |
| 4 | LLM2 | 73.5 | Most Concise |

## 🔧 How It Works

The analyzer:

1. **Reads all solution files** (.ps1, .bat, .md, etc.) from each LLM folder
2. **Analyzes prompt adherence** by checking for all required fields and functionality
3. **Evaluates performance** by detecting optimization patterns and potential bottlenecks
4. **Assesses code quality** through error handling, type safety, and best practices
5. **Measures readability** via commenting, structure, and naming conventions
6. **Scores documentation** based on README quality and inline help
7. **Generates comprehensive reports** with detailed scoring explanations

## 📊 Scoring Methodology

- **Objective criteria**: Each metric uses specific, measurable factors
- **No bias**: Starts from baseline scores and adds/subtracts based on evidence
- **Weighted scoring**: Different aspects weighted by importance for production use
- **Detailed explanations**: Every score includes the reasoning behind it

## 🎮 Interactive Dashboard Features

- **Live rankings** with overall scores
- **Radar chart** comparing all solutions across all metrics
- **Performance comparison** bar charts
- **Code metrics** visualization (lines of code, file count)
- **Category winners** highlighting what each solution does best
- **Detailed recommendations** for different use cases

## 🔄 Customization

To modify the analysis:

1. **Adjust weights** in the `overall_score` property
2. **Add new criteria** by extending the analysis methods
3. **Change scoring ranges** in individual analysis functions
4. **Modify dashboard styling** in the `generate_dashboard` method

The analyzer is designed to be fair, objective, and easily extensible for different types of code comparison tasks.
