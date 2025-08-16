#!/usr/bin/env python3
"""
Readability Analysis Module

Analyzes code readability, structure, and maintainability.
"""

import re
from typing import List, Dict, Any
from .base import BaseAnalyzer, FileInfo, AnalysisScore

class ReadabilityAnalyzer(BaseAnalyzer):
    """Analyzes code readability and maintainability"""
    
    def __init__(self):
        super().__init__(
            name="Readability Analysis",
            description="Evaluates code clarity, comments, structure, and naming conventions",
            weight=0.15
        )
    
    @property
    def category(self) -> str:
        return "readability"
    
    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """Analyze code readability"""
        score = 50  # Base score
        notes = []
        details = {}
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        
        for file in ps1_files:
            content = file.content
            lines = content.splitlines()
            
            # Comment analysis
            comment_analysis = self._analyze_comments(lines)
            score += comment_analysis['score']
            notes.extend(comment_analysis['notes'])
            details.update(comment_analysis['details'])
            
            # Documentation analysis
            doc_analysis = self._analyze_documentation(content)
            score += doc_analysis['score']
            notes.extend(doc_analysis['notes'])
            details.update(doc_analysis['details'])
            
            # Variable naming analysis
            naming_analysis = self._analyze_variable_naming(content)
            score += naming_analysis['score']
            notes.extend(naming_analysis['notes'])
            details.update(naming_analysis['details'])
            
            # Code organization analysis
            org_analysis = self._analyze_code_organization(content)
            score += org_analysis['score']
            notes.extend(org_analysis['notes'])
            details.update(org_analysis['details'])
            
            # Indentation analysis
            indent_analysis = self._analyze_indentation(lines)
            score += indent_analysis['score']
            notes.extend(indent_analysis['notes'])
            details.update(indent_analysis['details'])
        
        final_score = min(100, max(0, score))
        return AnalysisScore(score=final_score, notes=notes, details=details)
    
    def _analyze_comments(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze comment quality and density"""
        score = 0
        notes = []
        details = {}
        
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        comment_ratio = comment_lines / len(lines) if lines else 0
        details['comment_ratio'] = comment_ratio
        details['comment_lines'] = comment_lines
        
        if comment_ratio > 0.15:
            score += 15
            notes.append("Excellent commenting (>15% comment ratio)")
        elif comment_ratio > 0.10:
            score += 10
            notes.append("Good commenting (>10% comment ratio)")
        elif comment_ratio > 0.05:
            score += 5
            notes.append("Adequate commenting (>5% comment ratio)")
        else:
            score -= 5
            notes.append("Low comment ratio (<5%)")
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _analyze_documentation(self, content: str) -> Dict[str, Any]:
        """Analyze PowerShell help documentation"""
        score = 0
        notes = []
        details = {}
        
        has_help_block = '<#' in content and '.SYNOPSIS' in content
        details['has_help_block'] = has_help_block
        
        if has_help_block:
            score += 15
            notes.append("Includes PowerShell help documentation")
            
            # Check for comprehensive help
            help_sections = ['.SYNOPSIS', '.DESCRIPTION', '.PARAMETER', '.EXAMPLE', '.NOTES']
            found_sections = sum(1 for section in help_sections if section in content)
            details['help_sections_count'] = found_sections
            
            if found_sections >= 4:
                score += 5
                notes.append("Comprehensive help documentation")
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _analyze_variable_naming(self, content: str) -> Dict[str, Any]:
        """Analyze variable naming conventions"""
        score = 0
        notes = []
        details = {}
        
        var_matches = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', content)
        details['total_variables'] = len(var_matches)
        
        if var_matches:
            short_vars = [v for v in var_matches if len(v) < 3 and v not in ['_', 'f', 'i']]
            meaningful_ratio = 1 - (len(short_vars) / len(var_matches))
            details['meaningful_variable_ratio'] = meaningful_ratio
            details['short_variables'] = short_vars
            
            if meaningful_ratio > 0.8:
                score += 8
                notes.append("Uses descriptive variable names")
            else:
                score -= 5
                notes.append("Contains some unclear variable names")
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _analyze_code_organization(self, content: str) -> Dict[str, Any]:
        """Analyze code organization and structure"""
        score = 0
        notes = []
        details = {}
        
        function_count = len(re.findall(r'function\s+[a-zA-Z-]+', content))
        details['function_count'] = function_count
        
        if function_count > 0:
            score += 10
            notes.append(f"Well-organized with {function_count} functions")
        
        # Check for logical grouping with comments
        section_comments = len(re.findall(r'#\s*[A-Z][^#]*[A-Z]', content))
        details['section_comments'] = section_comments
        
        if section_comments > 2:
            score += 5
            notes.append("Good logical sectioning with comments")
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _analyze_indentation(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze indentation consistency"""
        score = 0
        notes = []
        details = {}
        
        indented_lines = [line for line in lines if line.startswith('    ') or line.startswith('\t')]
        indentation_ratio = len(indented_lines) / len(lines) if lines else 0
        details['indentation_ratio'] = indentation_ratio
        
        if indentation_ratio > 0.3:
            score += 5
            notes.append("Good code indentation")
        
        # Check for consistent indentation style
        space_indented = len([line for line in lines if line.startswith('    ')])
        tab_indented = len([line for line in lines if line.startswith('\t')])
        
        if space_indented > 0 and tab_indented > 0:
            score -= 3
            notes.append("Inconsistent indentation style (mixed spaces and tabs)")
            details['mixed_indentation'] = True
        else:
            details['mixed_indentation'] = False
        
        return {'score': score, 'notes': notes, 'details': details}
