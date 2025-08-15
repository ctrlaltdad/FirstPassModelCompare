#!/usr/bin/env python3
"""
Code Quality Analysis Module

Analyzes code quality, best practices, and maintainability.
"""

import re
from typing import List, Dict, Any
from .base import BaseAnalyzer, FileInfo, AnalysisScore

class CodeQualityAnalyzer(BaseAnalyzer):
    """Analyzes code quality and best practices"""
    
    def __init__(self):
        super().__init__(
            name="Code Quality Analysis",
            description="Evaluates error handling, type safety, and PowerShell best practices",
            weight=0.15
        )
    
    @property
    def category(self) -> str:
        return "quality"
    
    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """Analyze code quality"""
        score = 20  # Conservative base score
        notes = []
        details = {}
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        
        for file in ps1_files:
            content = file.content
            content_lower = content.lower()
            lines = content.splitlines()
            
            # Error handling & robustness
            error_score = self._analyze_error_handling(content, content_lower)
            score += error_score['score']
            notes.extend(error_score['notes'])
            details.update(error_score['details'])
            
            # Parameter validation & type safety
            param_score = self._analyze_parameter_validation(content)
            score += param_score['score']
            notes.extend(param_score['notes'])
            details.update(param_score['details'])
            
            # Code organization & structure
            org_score = self._analyze_code_organization(content, lines)
            score += org_score['score']
            notes.extend(org_score['notes'])
            details.update(org_score['details'])
            
            # PowerShell best practices
            best_practice_score = self._analyze_powershell_practices(content, content_lower)
            score += best_practice_score['score']
            notes.extend(best_practice_score['notes'])
            details.update(best_practice_score['details'])
            
            # Maintainability
            maint_score = self._analyze_maintainability(content, lines)
            score += maint_score['score']
            notes.extend(maint_score['notes'])
            details.update(maint_score['details'])
        
        final_score = min(100, max(0, score))
        return AnalysisScore(score=final_score, notes=notes, details=details)
    
    def _analyze_error_handling(self, content: str, content_lower: str) -> Dict[str, Any]:
        """Analyze error handling and robustness (25 points max)"""
        score = 0
        notes = []
        details = {}
        
        # Try-catch blocks
        if 'try' in content_lower and 'catch' in content_lower:
            score += 15
            notes.append("+ Implements try-catch error handling")
            details['has_try_catch'] = True
        elif 'erroraction' in content_lower:
            score += 10
            notes.append("+ Uses ErrorAction for error handling")
            details['has_error_action'] = True
        
        # Error variable tracking
        if 'errorvariable' in content_lower:
            score += 5
            notes.append("+ Uses ErrorVariable for error tracking")
            details['has_error_variable'] = True
        
        # Parameter validation
        validation_patterns = ['ValidateNotNull', 'ValidateSet', 'ValidateRange', 'ValidateScript']
        found_validation = [pattern for pattern in validation_patterns if pattern in content]
        if found_validation:
            score += 5
            notes.append(f"+ Uses parameter validation: {', '.join(found_validation)}")
            details['validation_attributes'] = found_validation
        
        details['error_handling_score'] = min(score, 25)
        return {'score': min(score, 25), 'notes': notes, 'details': details}
    
    def _analyze_parameter_validation(self, content: str) -> Dict[str, Any]:
        """Analyze parameter validation and type safety (20 points max)"""
        score = 0
        notes = []
        details = {}
        
        # Parameter attributes
        if '[Parameter(' in content:
            score += 8
            notes.append("+ Uses Parameter attributes")
            details['has_parameter_attributes'] = True
            
            if 'Mandatory' in content:
                score += 5
                notes.append("+ Has mandatory parameters")
                details['has_mandatory_params'] = True
                
            if 'ValueFromPipeline' in content:
                score += 3
                notes.append("+ Supports pipeline input")
                details['supports_pipeline'] = True
        
        # Type hints
        type_patterns = [r'\[string\]', r'\[int\]', r'\[bool\]', r'\[array\]', r'\[switch\]']
        type_hints = sum(len(re.findall(pattern, content)) for pattern in type_patterns)
        details['type_hints_count'] = type_hints
        
        if type_hints > 0:
            type_score = min(type_hints * 2, 10)
            score += type_score
            notes.append(f"+ Uses type hints ({type_hints} found)")
            details['has_type_hints'] = True
        
        details['param_validation_score'] = min(score, 20)
        return {'score': min(score, 20), 'notes': notes, 'details': details}
    
    def _analyze_code_organization(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze code organization and structure (20 points max)"""
        score = 0
        notes = []
        details = {}
        
        # Function usage
        function_count = len(re.findall(r'function\s+[a-zA-Z-]+', content))
        details['function_count'] = function_count
        
        if function_count > 0:
            func_score = min(function_count * 5, 15)
            score += func_score
            notes.append(f"+ Well-organized with {function_count} functions")
        
        # Consistent indentation
        indented_lines = len([line for line in lines if line.startswith('    ') or line.startswith('\t')])
        if indented_lines > len(lines) * 0.2:
            score += 5
            notes.append("+ Consistent code indentation")
            details['has_consistent_indentation'] = True
        
        details['organization_score'] = min(score, 20)
        return {'score': min(score, 20), 'notes': notes, 'details': details}
    
    def _analyze_powershell_practices(self, content: str, content_lower: str) -> Dict[str, Any]:
        """Analyze PowerShell best practices (15 points max)"""
        score = 0
        notes = []
        details = {}
        
        # Approved verbs
        approved_verbs = ['Get-', 'Set-', 'New-', 'Remove-', 'Test-', 'Start-', 'Stop-']
        if re.search(r'function\s+(' + '|'.join(approved_verbs) + ')', content):
            score += 5
            notes.append("+ Uses approved PowerShell verbs")
            details['uses_approved_verbs'] = True
        
        # CmdletBinding
        if '[CmdletBinding()]' in content:
            score += 5
            notes.append("+ Uses CmdletBinding for advanced functions")
            details['has_cmdletbinding'] = True
        
        # Proper parameter blocks
        if 'param(' in content_lower and ')' in content:
            score += 5
            notes.append("+ Uses proper parameter block")
            details['has_param_block'] = True
        
        details['powershell_practices_score'] = min(score, 15)
        return {'score': min(score, 15), 'notes': notes, 'details': details}
    
    def _analyze_maintainability(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """Analyze maintainability factors (10 points max)"""
        score = 0
        notes = []
        details = {}
        
        # Reasonable line length (< 120 chars)
        long_lines = len([line for line in lines if len(line) > 120])
        long_line_ratio = long_lines / len(lines) if lines else 0
        details['long_line_ratio'] = long_line_ratio
        
        if long_line_ratio < 0.1:  # Less than 10% long lines
            score += 5
            notes.append("+ Reasonable line lengths (<10% over 120 chars)")
        
        # Variable naming quality
        vars_found = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', content)
        if vars_found:
            meaningful_vars = [v for v in vars_found if len(v) >= 3 or v in ['_', 'f', 'i']]
            meaningful_ratio = len(meaningful_vars) / len(vars_found)
            details['meaningful_variable_ratio'] = meaningful_ratio
            
            if meaningful_ratio > 0.8:
                score += 5
                notes.append("+ Good variable naming practices")
        
        details['maintainability_score'] = min(score, 10)
        return {'score': min(score, 10), 'notes': notes, 'details': details}
