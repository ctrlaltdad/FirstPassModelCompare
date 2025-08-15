#!/usr/bin/env python3
"""
LLM Analysis System - Complete Modular Framework

This script demonstrates the full capabilities of the modular LLM analysis system
and shows how to extend it with new analysis modules.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modular_analyzer import ModularLLMAnalyzer
from dashboard_generator import DashboardGenerator
from analysis.base import BaseAnalyzer, AnalysisScore, FileInfo

class SecurityAnalyzer(BaseAnalyzer):
    """Example of how to add a new security analysis module"""
    
    def __init__(self):
        super().__init__(
            name="Security Analysis",
            description="Evaluates security practices, input validation, and potential vulnerabilities",
            weight=0.10  # 10% weight
        )
    
    def _search_pattern(self, content: str, pattern: str) -> bool:
        """Helper method to search for regex patterns in content"""
        import re
        return bool(re.search(pattern, content, re.IGNORECASE | re.MULTILINE))
    
    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """Analyze security aspects of the PowerShell solution"""
        
        total_score = 0
        max_score = 0
        notes = []
        details = {}
        
        # Combine all PowerShell content
        ps_content = ""
        for file in files:
            if file.path.endswith('.ps1'):
                ps_content += file.content + "\n"
        
        if not ps_content:
            return AnalysisScore(0, ["No PowerShell files found"])
        
        # Check for input validation (20 points)
        max_score += 20
        input_validation_patterns = [
            r'\$PSBoundParameters',
            r'\[Parameter\(',
            r'\[ValidateScript\(',
            r'\[ValidateSet\(',
            r'\[ValidateNotNull\(',
            r'if.*-not.*\$',
            r'Test-Path',
            r'param\s*\('
        ]
        
        validation_found = sum(1 for pattern in input_validation_patterns 
                             if self._search_pattern(ps_content, pattern))
        
        if validation_found >= 4:
            total_score += 20
            notes.append("✓ Comprehensive input validation implemented")
        elif validation_found >= 2:
            total_score += 15
            notes.append("✓ Basic input validation present")
        elif validation_found >= 1:
            total_score += 10
            notes.append("⚠ Minimal input validation")
        else:
            notes.append("✗ No input validation detected")
        
        details['input_validation_patterns'] = validation_found
        
        # Check for error handling (20 points)
        max_score += 20
        error_handling_patterns = [
            r'try\s*{',
            r'catch\s*{',
            r'finally\s*{',
            r'ErrorAction',
            r'ErrorVariable',
            r'\$Error\[',
            r'throw\s+',
            r'Write-Error'
        ]
        
        error_handling_found = sum(1 for pattern in error_handling_patterns 
                                 if self._search_pattern(ps_content, pattern))
        
        if error_handling_found >= 4:
            total_score += 20
            notes.append("✓ Robust error handling implemented")
        elif error_handling_found >= 2:
            total_score += 15
            notes.append("✓ Basic error handling present")
        elif error_handling_found >= 1:
            total_score += 10
            notes.append("⚠ Minimal error handling")
        else:
            notes.append("✗ No error handling detected")
        
        details['error_handling_patterns'] = error_handling_found
        
        # Check for dangerous operations (20 points)
        max_score += 20
        dangerous_patterns = [
            r'Remove-Item.*-Force',
            r'Delete\(',
            r'rm\s+-rf',
            r'Format-Volume',
            r'Clear-Host',
            r'Invoke-Expression',
            r'iex\s+',
            r'cmd\s*/c'
        ]
        
        dangerous_found = sum(1 for pattern in dangerous_patterns 
                            if self._search_pattern(ps_content, pattern))
        
        if dangerous_found == 0:
            total_score += 20
            notes.append("✓ No dangerous operations detected")
        elif dangerous_found <= 2:
            total_score += 10
            notes.append("⚠ Some potentially dangerous operations present")
        else:
            notes.append("✗ Multiple dangerous operations detected")
        
        details['dangerous_operations'] = dangerous_found
        
        # Check for privilege escalation prevention (20 points)
        max_score += 20
        privilege_patterns = [
            r'#Requires -RunAsAdministrator',
            r'Test-IsAdmin',
            r'IsInRole.*Administrator',
            r'\[Security\.Principal\.WindowsIdentity\]',
            r'UAC',
            r'elevation'
        ]
        
        privilege_found = sum(1 for pattern in privilege_patterns 
                            if self._search_pattern(ps_content, pattern))
        
        if privilege_found >= 2:
            total_score += 20
            notes.append("✓ Privilege awareness implemented")
        elif privilege_found >= 1:
            total_score += 10
            notes.append("⚠ Basic privilege checking")
        else:
            total_score += 5  # Bonus for not requiring admin
            notes.append("⚠ No explicit privilege management")
        
        details['privilege_patterns'] = privilege_found
        
        # Check for secure coding practices (20 points)
        max_score += 20
        secure_patterns = [
            r'ConvertTo-SecureString',
            r'Credential',
            r'SecureString',
            r'ConfirmPreference',
            r'WhatIf',
            r'SupportsShouldProcess',
            r'PSCmdlet\.ShouldProcess'
        ]
        
        secure_found = sum(1 for pattern in secure_patterns 
                         if self._search_pattern(ps_content, pattern))
        
        if secure_found >= 3:
            total_score += 20
            notes.append("✓ Strong security practices")
        elif secure_found >= 2:
            total_score += 15
            notes.append("✓ Good security practices")
        elif secure_found >= 1:
            total_score += 10
            notes.append("⚠ Some security practices")
        else:
            notes.append("⚠ Limited security practices")
        
        details['secure_coding_patterns'] = secure_found
        
        # Calculate final score
        final_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        details.update({
            'total_score': total_score,
            'max_score': max_score,
            'security_score': final_score
        })
        
        return AnalysisScore(final_score, notes, details)

def demonstrate_modular_system():
    """Demonstrate the complete modular analysis system"""
    
    print("🤖 LLM Analysis System - Modular Framework Demo")
    print("=" * 60)
    print()
    
    workspace_path = r"d:\CodingModel\ModelCompare\FirstPassModelCompare"
    
    # Create analyzer
    analyzer = ModularLLMAnalyzer(workspace_path)
    
    print("📋 Current Analysis Modules:")
    for info in analyzer.registry.list_analyzers():
        status = "✓" if info['enabled'] else "✗"
        print(f"  {status} {info['name']} (Weight: {info['weight']:.0%})")
    print()
    
    # Demonstrate adding a new analyzer
    print("🔒 Adding Security Analysis Module...")
    security_analyzer = SecurityAnalyzer()
    analyzer.registry.register(security_analyzer)
    print(f"  ✓ {security_analyzer.name} added")
    print()
    
    print("📊 Updated Analysis Modules:")
    for info in analyzer.registry.list_analyzers():
        status = "✓" if info['enabled'] else "✗"
        print(f"  {status} {info['name']} (Weight: {info['weight']:.0%})")
    print()
    
    # Run analysis with new module
    print("🔍 Running Enhanced Analysis...")
    results = analyzer.analyze_all_solutions()
    print()
    
    # Generate enhanced reports
    print("📄 Generating Enhanced Reports...")
    
    # Markdown report
    report = analyzer.generate_report(results)
    report_path = os.path.join(workspace_path, 'enhanced_analysis_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  ✓ Enhanced report: {report_path}")
    
    # CSV summary
    csv_path = os.path.join(workspace_path, 'enhanced_analysis_summary.csv')
    analyzer.export_csv_summary(results, csv_path)
    print(f"  ✓ Enhanced CSV: {csv_path}")
    
    # JSON details
    json_path = os.path.join(workspace_path, 'enhanced_analysis_detailed.json')
    analyzer.export_detailed_json(results, json_path)
    print(f"  ✓ Enhanced JSON: {json_path}")
    
    # Interactive dashboard
    dashboard_generator = DashboardGenerator()
    dashboard_path = os.path.join(workspace_path, 'enhanced_analysis_dashboard.html')
    dashboard_generator.generate_dashboard({"results": [
        {
            "llm_name": r.llm_name,
            "overall_score": r.overall_score,
            "files": [{"path": f.path, "lines": f.lines, "size": f.size} for f in r.files],
            "analysis_scores": {name: {"score": score.score, "notes": score.notes} 
                             for name, score in r.analysis_scores.items()}
        } for r in results
    ]}, dashboard_path)
    print(f"  ✓ Enhanced dashboard: {dashboard_path}")
    print()
    
    # Show final rankings
    print("🏆 Enhanced Analysis Results:")
    print("=" * 40)
    
    sorted_results = sorted(results, key=lambda x: x.overall_score, reverse=True)
    for i, result in enumerate(sorted_results, 1):
        print(f"{i}. {result.llm_name}: {result.overall_score:.1f}/100")
        
        # Show category breakdown
        for category, score in result.analysis_scores.items():
            category_short = category.replace(' Analysis', '')
            print(f"   • {category_short}: {score.score:.1f}")
        print()
    
    # Show what other modules could be added
    print("🚀 Potential Additional Modules:")
    potential_modules = [
        ("Runtime Performance", "Actual execution time and resource usage profiling"),
        ("Maintainability", "Code complexity, cyclomatic complexity, and refactoring ease"),
        ("Scalability", "Ability to handle large datasets and concurrent operations"),
        ("Compliance", "Adherence to organizational coding standards and policies"),
        ("Accessibility", "User interface design and accessibility compliance"),
        ("Internationalization", "Support for multiple languages and locales"),
        ("Testing Coverage", "Unit tests, integration tests, and test quality"),
        ("Documentation Quality", "API documentation, inline comments, and examples")
    ]
    
    for name, description in potential_modules:
        print(f"  • {name}: {description}")
    print()
    
    print("✨ Modular System Benefits:")
    print("  • Easy to add new analysis dimensions")
    print("  • Configurable weights for different priorities")
    print("  • Consistent scoring methodology across modules")
    print("  • Extensible plugin architecture")
    print("  • Automatic report and dashboard generation")
    print("  • JSON export for integration with other tools")

def show_architecture_overview():
    """Show the modular architecture structure"""
    
    print("\n🏗️  Modular Architecture Overview")
    print("=" * 50)
    print()
    
    print("📦 Core Components:")
    print("  • analysis/base.py - Abstract base classes and registry")
    print("  • modular_analyzer.py - Main analysis orchestrator")
    print("  • dashboard_generator.py - Interactive dashboard generator")
    print()
    
    print("🔌 Analysis Modules:")
    modules = [
        ("performance.py", "Algorithmic efficiency and optimization"),
        ("readability.py", "Code clarity and maintainability"),
        ("prompt_adherence.py", "Requirements compliance"),
        ("code_quality.py", "Best practices and error handling"),
        ("documentation.py", "Documentation quality and completeness"),
        ("SecurityAnalyzer", "Security practices (demo)")
    ]
    
    for module, description in modules:
        print(f"  • {module} - {description}")
    print()
    
    print("📊 Output Formats:")
    print("  • Markdown reports with detailed analysis")
    print("  • CSV summaries for spreadsheet analysis")
    print("  • JSON data for programmatic access")
    print("  • Interactive HTML dashboards with charts")
    print()
    
    print("🎯 Extension Points:")
    print("  • Add new analyzers by extending BaseAnalyzer")
    print("  • Configure weights for different analysis priorities")
    print("  • Enable/disable modules based on requirements")
    print("  • Custom scoring algorithms for specific domains")

if __name__ == "__main__":
    demonstrate_modular_system()
    show_architecture_overview()
