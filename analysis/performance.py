#!/usr/bin/env python3
"""
Performance Analysis Module

Analyzes performance characteristics of PowerShell solutions.
"""

import re
from typing import List, Dict, Any
from .base import BaseAnalyzer, FileInfo, AnalysisScore

class PerformanceAnalyzer(BaseAnalyzer):
    """Analyzes performance characteristics of code solutions"""
    
    def __init__(self):
        super().__init__(
            name="Performance Analysis",
            description="Evaluates algorithmic efficiency, optimization techniques, and performance patterns",
            weight=0.25
        )
    
    @property
    def category(self) -> str:
        return "performance"
    
    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """Analyze performance characteristics"""
        # Scoring components (out of 100 total)
        base_score = 50  # Start at 50 (average performance)
        optimization_score = 0    # Max +30 points
        concern_penalty = 0       # Max -20 points
        complexity_bonus = 0      # Max +10 points
        algorithm_penalty = 0     # Max -30 points
        
        notes = []
        details = {}
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        total_lines = sum(f.lines for f in ps1_files)
        details['total_lines'] = total_lines
        
        for file in ps1_files:
            content = file.content
            content_lower = content.lower()
            
            # PERFORMANCE OPTIMIZATIONS (Positive factors)
            optimizations = self._check_optimizations(content, content_lower)
            optimization_score += optimizations['score']
            notes.extend(optimizations['notes'])
            details.update(optimizations['details'])
            
            # PERFORMANCE CONCERNS (Negative factors)
            concerns = self._check_performance_concerns(content, content_lower)
            concern_penalty += concerns['score']
            notes.extend(concerns['notes'])
            details.update(concerns['details'])
            
            # CODE COMPLEXITY ANALYSIS
            complexity = self._analyze_complexity(content, total_lines)
            complexity_bonus += complexity['score']
            notes.extend(complexity['notes'])
            details.update(complexity['details'])
        
        # ALGORITHMIC EFFICIENCY
        algorithm_score = self._analyze_algorithmic_efficiency(content)
        algorithm_penalty += abs(algorithm_score['score'])  # Convert to positive penalty
        notes.extend(algorithm_score['notes'])
        details.update(algorithm_score['details'])
        
        # Calculate final score (normalized to 0-100)
        final_score = base_score + min(optimization_score, 30) - min(concern_penalty, 20) + min(complexity_bonus, 10) - min(algorithm_penalty, 30)
        final_score = min(100, max(0, final_score))
        
        return AnalysisScore(score=final_score, notes=notes, details=details)
    
    def _check_optimizations(self, content: str, content_lower: str) -> Dict[str, Any]:
        """Check for performance optimizations"""
        score = 0
        notes = []
        details = {}
        
        # Error handling for performance
        if 'erroraction silentlycontinue' in content_lower:
            score += 15
            notes.append("+ Uses ErrorAction SilentlyContinue (prevents performance hits from errors)")
            details['has_error_action'] = True
        
        # Efficient file enumeration
        if 'get-childitem' in content_lower:
            if '-file' in content_lower:
                score += 8
                notes.append("+ Uses -File parameter for efficient enumeration")
                details['uses_file_parameter'] = True
            if '-recurse' in content_lower:
                score += 5
                notes.append("+ Supports recursive scanning")
                details['supports_recursion'] = True
        
        # Result limiting to avoid memory issues
        if any(keyword in content_lower for keyword in ['select-object -first', '| select -first', 'top', 'limit']):
            score += 12
            notes.append("+ Implements result limiting for memory efficiency")
            details['has_result_limiting'] = True
        
        # Efficient data structures
        if '[system.collections.generic.list' in content_lower:
            score += 10
            notes.append("+ Uses efficient .NET Generic Collections")
            details['uses_generic_collections'] = True
        elif 'array' in content_lower and '+=' in content:
            score -= 5
            notes.append("- Uses array concatenation (inefficient for large datasets)")
            details['uses_array_concatenation'] = True
        
        # Parallel processing
        if 'foreach-object -parallel' in content_lower:
            score += 20
            notes.append("+ Implements parallel processing")
            details['has_parallel_processing'] = True
        
        # Caching and pre-computation
        cache_indicators = ['hashtable', 'cache', 'precompute', 'namestemap', 'map']
        if any(indicator in content_lower for indicator in cache_indicators):
            score += 8
            notes.append("+ Shows evidence of caching/pre-computation")
            details['has_caching'] = True
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _check_performance_concerns(self, content: str, content_lower: str) -> Dict[str, Any]:
        """Check for performance concerns"""
        score = 0
        notes = []
        details = {}
        
        # Multiple expensive operations
        childitem_count = content_lower.count('get-childitem')
        if childitem_count > 2:
            score += (childitem_count - 2) * 3
            notes.append(f"- Multiple Get-ChildItem calls ({childitem_count}) may impact performance")
            details['multiple_childitem_calls'] = childitem_count
        
        # Inefficient filtering
        if 'where-object' in content_lower and 'get-childitem' in content_lower:
            where_count = content_lower.count('where-object')
            if where_count > 1:
                score += where_count * 2
                notes.append(f"- Multiple Where-Object filters ({where_count}) after enumeration")
                details['multiple_where_filters'] = where_count
        
        # String operations in loops
        if 'foreach' in content_lower and any(op in content for op in ['-match', '-like', 'startswith', 'contains']):
            score += 3
            notes.append("- String operations in loops may impact performance")
            details['string_ops_in_loops'] = True
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _analyze_complexity(self, content: str, total_lines: int) -> Dict[str, Any]:
        """Analyze code complexity"""
        score = 0
        notes = []
        details = {}
        
        if total_lines < 50:
            notes.append("~ Very concise implementation (may lack optimization)")
            details['complexity_level'] = 'very_simple'
        elif total_lines > 500:
            score -= 5
            notes.append("- Very complex implementation may impact performance")
            details['complexity_level'] = 'very_complex'
        elif 100 <= total_lines <= 300:
            score += 5
            notes.append("+ Good balance of features and performance")
            details['complexity_level'] = 'balanced'
        
        details['total_lines'] = total_lines
        return {'score': score, 'notes': notes, 'details': details}
    
    def _analyze_algorithmic_efficiency(self, content: str) -> Dict[str, Any]:
        """Analyze algorithmic efficiency"""
        score = 0
        notes = []
        details = {}
        
        # Check for O(n²) patterns
        nested_loops = len(re.findall(r'foreach.*foreach', content, re.IGNORECASE | re.DOTALL))
        if nested_loops > 0:
            score -= nested_loops * 8
            notes.append(f"- Contains nested loops ({nested_loops}) - potential O(n²) complexity")
            details['nested_loops'] = nested_loops
        
        details['algorithmic_complexity'] = 'O(n²)' if nested_loops > 0 else 'O(n)'
        return {'score': score, 'notes': notes, 'details': details}
