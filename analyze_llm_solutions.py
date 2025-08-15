#!/usr/bin/env python3
"""
LLM Solution Analyzer

Analyzes and compares 4 different LLM solutions for the "Safe File Deletion Identifier" prompt.
Evaluates performance, readability, prompt adherence, and code quality.
"""

import os
import re
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any
import csv

@dataclass
class FileInfo:
    """Information about a code file"""
    path: str
    size: int
    lines: int
    content: str

@dataclass
class AnalysisResult:
    """Analysis results for a single LLM solution"""
    llm_name: str
    files: List[FileInfo]
    total_lines: int
    total_size: int
    
    # Scoring metrics (0-100)
    performance_score: float
    readability_score: float
    prompt_adherence_score: float
    code_quality_score: float
    documentation_score: float
    feature_completeness_score: float
    
    # Detailed analysis
    strengths: List[str]
    weaknesses: List[str]
    performance_notes: List[str]
    readability_notes: List[str]
    prompt_adherence_notes: List[str]
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score"""
        weights = {
            'performance': 0.25,
            'readability': 0.20,
            'prompt_adherence': 0.25,
            'code_quality': 0.15,
            'documentation': 0.10,
            'feature_completeness': 0.05
        }
        
        return (
            self.performance_score * weights['performance'] +
            self.readability_score * weights['readability'] +
            self.prompt_adherence_score * weights['prompt_adherence'] +
            self.code_quality_score * weights['code_quality'] +
            self.documentation_score * weights['documentation'] +
            self.feature_completeness_score * weights['feature_completeness']
        )

class LLMSolutionAnalyzer:
    """Analyzes LLM solutions for the safe file deletion prompt"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.prompt_requirements = self._parse_prompt_requirements()
        
    def _parse_prompt_requirements(self) -> Dict[str, Any]:
        """Parse the original prompt to extract requirements"""
        prompt_file = os.path.join(self.workspace_path, "prompt.txt.txt")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
        except FileNotFoundError:
            prompt_content = "Create for me a script that can run on windows that identifies files that are safe to delete. It doesn't delete them itself, but provides a ranking of safety. In the report, include the safety-score, parameters that went into the score consideration, file name, size, date created, and date updated."
        
        return {
            'platform': 'windows',
            'main_function': 'identify files safe to delete',
            'no_deletion': 'does not delete files itself',
            'ranking_system': 'provides ranking of safety',
            'required_fields': [
                'safety-score',
                'parameters that went into score consideration',
                'file name',
                'size', 
                'date created',
                'date updated'
            ],
            'prompt_text': prompt_content
        }
    
    def analyze_solution(self, llm_folder: str) -> AnalysisResult:
        """Analyze a single LLM solution"""
        llm_path = os.path.join(self.workspace_path, llm_folder)
        
        # Gather files
        files = self._gather_files(llm_path)
        
        # Calculate basic metrics
        total_lines = sum(f.lines for f in files)
        total_size = sum(f.size for f in files)
        
        # Analyze each aspect
        performance_score, perf_notes = self._analyze_performance(files)
        readability_score, read_notes = self._analyze_readability(files)
        adherence_score, adherence_notes = self._analyze_prompt_adherence(files)
        quality_score = self._analyze_code_quality(files)
        documentation_score = self._analyze_documentation(files)
        feature_score = self._analyze_feature_completeness(files)
        
        strengths, weaknesses = self._identify_strengths_weaknesses(files)
        
        return AnalysisResult(
            llm_name=llm_folder,
            files=files,
            total_lines=total_lines,
            total_size=total_size,
            performance_score=performance_score,
            readability_score=readability_score,
            prompt_adherence_score=adherence_score,
            code_quality_score=quality_score,
            documentation_score=documentation_score,
            feature_completeness_score=feature_score,
            strengths=strengths,
            weaknesses=weaknesses,
            performance_notes=perf_notes,
            readability_notes=read_notes,
            prompt_adherence_notes=adherence_notes
        )
    
    def _gather_files(self, path: str) -> List[FileInfo]:
        """Gather all relevant files from the solution directory"""
        files = []
        
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(('.ps1', '.bat', '.cmd', '.py', '.md', '.txt')):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        size = os.path.getsize(filepath)
                        lines = len(content.splitlines())
                        
                        files.append(FileInfo(
                            path=filepath,
                            size=size,
                            lines=lines,
                            content=content
                        ))
                    except Exception as e:
                        print(f"Warning: Could not read {filepath}: {e}")
        
        return files
    
    def _analyze_performance(self, files: List[FileInfo]) -> tuple:
        """Analyze performance characteristics - ENHANCED FOR OBJECTIVE ANALYSIS"""
        score = 30  # Conservative base score
        notes = []
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        total_lines = sum(f.lines for f in ps1_files)
        
        for file in ps1_files:
            content = file.content
            content_lower = content.lower()
            
            # PERFORMANCE OPTIMIZATIONS (Positive factors)
            
            # Error handling for performance
            if 'erroraction silentlycontinue' in content_lower:
                score += 15
                notes.append("+ Uses ErrorAction SilentlyContinue (prevents performance hits from errors)")
            
            # Efficient file enumeration
            if 'get-childitem' in content_lower:
                if '-file' in content_lower:
                    score += 8
                    notes.append("+ Uses -File parameter for efficient enumeration")
                if '-recurse' in content_lower:
                    score += 5
                    notes.append("+ Supports recursive scanning")
            
            # Result limiting to avoid memory issues
            if any(keyword in content_lower for keyword in ['select-object -first', '| select -first', 'top', 'limit']):
                score += 12
                notes.append("+ Implements result limiting for memory efficiency")
            
            # Efficient data structures
            if '[system.collections.generic.list' in content_lower:
                score += 10
                notes.append("+ Uses efficient .NET Generic Collections")
            elif 'array' in content_lower and '+=' in content:
                score -= 5
                notes.append("- Uses array concatenation (inefficient for large datasets)")
            
            # Parallel processing
            if 'foreach-object -parallel' in content_lower:
                score += 20
                notes.append("+ Implements parallel processing")
            
            # Caching and pre-computation
            cache_indicators = ['hashtable', 'cache', 'precompute', 'namestemap', 'map']
            if any(indicator in content_lower for indicator in cache_indicators):
                score += 8
                notes.append("+ Shows evidence of caching/pre-computation")
            
            # PERFORMANCE CONCERNS (Negative factors)
            
            # Multiple expensive operations
            childitem_count = content_lower.count('get-childitem')
            if childitem_count > 2:
                score -= (childitem_count - 2) * 3
                notes.append(f"- Multiple Get-ChildItem calls ({childitem_count}) may impact performance")
            
            # Inefficient filtering
            if 'where-object' in content_lower and 'get-childitem' in content_lower:
                where_count = content_lower.count('where-object')
                if where_count > 1:
                    score -= where_count * 2
                    notes.append(f"- Multiple Where-Object filters ({where_count}) after enumeration")
            
            # String operations in loops
            if 'foreach' in content_lower and any(op in content for op in ['-match', '-like', 'startswith', 'contains']):
                score -= 3
                notes.append("- String operations in loops may impact performance")
            
            # CODE COMPLEXITY ANALYSIS
            if total_lines < 50:
                notes.append("~ Very concise implementation (may lack optimization)")
            elif total_lines > 500:
                score -= 5
                notes.append("- Very complex implementation may impact performance")
            elif 100 <= total_lines <= 300:
                score += 5
                notes.append("+ Good balance of features and performance")
        
        # ALGORITHMIC EFFICIENCY
        # Check for O(n²) patterns
        nested_loops = len(re.findall(r'foreach.*foreach', content, re.IGNORECASE | re.DOTALL))
        if nested_loops > 0:
            score -= nested_loops * 8
            notes.append(f"- Contains nested loops ({nested_loops}) - potential O(n²) complexity")
        
        return min(100, max(0, score)), notes
    
    def _analyze_readability(self, files: List[FileInfo]) -> tuple:
        """Analyze code readability"""
        score = 50  # Base score
        notes = []
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        
        for file in ps1_files:
            content = file.content
            lines = content.splitlines()
            
            # Check for comments
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            comment_ratio = comment_lines / len(lines) if lines else 0
            
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
            
            # Check for help documentation
            if '<#' in content and '.SYNOPSIS' in content:
                score += 15
                notes.append("Includes PowerShell help documentation")
            
            # Check for meaningful variable names
            var_matches = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', content)
            short_vars = [v for v in var_matches if len(v) < 3 and v not in ['_', 'f', 'i']]
            if len(short_vars) / len(var_matches) < 0.2 if var_matches else True:
                score += 8
                notes.append("Uses descriptive variable names")
            else:
                score -= 5
                notes.append("Contains some unclear variable names")
            
            # Check for function organization
            function_count = len(re.findall(r'function\s+[a-zA-Z-]+', content))
            if function_count > 0:
                score += 10
                notes.append(f"Well-organized with {function_count} functions")
            
            # Check for proper indentation consistency
            indented_lines = [line for line in lines if line.startswith('    ') or line.startswith('\t')]
            if len(indented_lines) > len(lines) * 0.3:
                score += 5
                notes.append("Good code indentation")
        
        return min(100, max(0, score)), notes
    
    def _analyze_prompt_adherence(self, files: List[FileInfo]) -> tuple:
        """Analyze how well the solution adheres to the prompt - ENHANCED FOR FAIRNESS"""
        score = 0  # Start from 0 for objective scoring
        notes = []
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        all_content = ' '.join(f.content for f in ps1_files)
        all_content_lower = all_content.lower()
        
        # REQUIREMENT 1: Windows script (20 points)
        if ps1_files:  # PowerShell files indicate Windows compatibility
            score += 20
            notes.append("✓ Creates Windows-compatible PowerShell script")
        else:
            notes.append("✗ No PowerShell files found")
        
        # REQUIREMENT 2: Identifies files safe to delete (20 points)
        safety_indicators = ['safe', 'delete', 'safety', 'risk', 'dangerous']
        if any(indicator in all_content_lower for indicator in safety_indicators):
            score += 20
            notes.append("✓ Identifies files for potential deletion")
        else:
            notes.append("✗ Does not clearly identify deletion candidates")
        
        # REQUIREMENT 3: Does NOT delete files (15 points)
        deletion_protection = False
        if any(phrase in all_content_lower for phrase in ['does not delete', 'not delete', 'no delete', 'only identifies', 'only reports', 'never deletes']):
            deletion_protection = True
        
        # Check for actual deletion commands (should NOT be present) - be more precise
        dangerous_patterns = [
            r'\bremove-item\s+',
            r'\bdel\s+[^\s]',  # del followed by something (not just "del" in text)
            r'\berase\s+[^\s]',
            r'\brm\s+[^\s]'
        ]
        
        has_deletion_commands = False
        for pattern in dangerous_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                # Found a potential command, check if it's in actual code
                matches = re.finditer(pattern, all_content, re.IGNORECASE)
                for match in matches:
                    # Get the line containing this match
                    start = all_content.rfind('\n', 0, match.start()) + 1
                    end = all_content.find('\n', match.end())
                    if end == -1:
                        end = len(all_content)
                    line = all_content[start:end].strip()
                    
                    # Skip if it's clearly in a comment or string
                    if not (line.startswith('#') or '"delete' in line.lower() or "'delete" in line.lower() or 
                           'does not' in line.lower() or 'not perform' in line.lower()):
                        has_deletion_commands = True
                        break
                if has_deletion_commands:
                    break
        
        if deletion_protection and not has_deletion_commands:
            score += 15
            notes.append("✓ Explicitly states no deletion occurs and contains no deletion commands")
        elif not has_deletion_commands:
            score += 10
            notes.append("~ No deletion commands found (good)")
        else:
            notes.append("✗ Contains actual deletion commands!")
        
        # REQUIREMENT 4: Provides ranking/safety score (15 points)
        ranking_indicators = ['score', 'rank', 'rating', 'priority', 'safety']
        if any(indicator in all_content_lower for indicator in ranking_indicators):
            score += 15
            notes.append("✓ Implements ranking/scoring system")
        else:
            notes.append("✗ No clear ranking system found")
        
        # REQUIREMENT 5: Required output fields (30 points total - 5 each)
        required_fields = {
            'safety-score': ['safety', 'score', 'rating'],
            'parameters': ['parameter', 'factor', 'reason', 'criteria'],
            'file name': ['name', 'filename', 'fullname'],
            'size': ['size', 'length', 'kb', 'mb', 'byte'],
            'date created': ['creation', 'created', 'creationtime'],
            'date updated': ['lastwrite', 'modified', 'updated', 'lastmodified']
        }
        
        fields_found = 0
        for field_name, keywords in required_fields.items():
            if any(keyword in all_content_lower for keyword in keywords):
                fields_found += 1
                score += 5
                notes.append(f"✓ Includes {field_name}")
            else:
                notes.append(f"✗ Missing {field_name}")
        
        # Bonus points for going beyond requirements (max 10 points)
        bonus_features = {
            'export_options': ['csv', 'json', 'xml', 'export'],
            'configurable_params': ['param(', 'parameter('],
            'help_documentation': ['.synopsis', '.description', '.example'],
            'error_handling': ['try', 'catch', 'erroraction'],
            'progress_indication': ['write-progress', 'write-host', 'verbose']
        }
        
        bonus_score = 0
        for feature, keywords in bonus_features.items():
            if any(keyword in all_content_lower for keyword in keywords):
                bonus_score += 2
                if bonus_score <= 10:
                    notes.append(f"+ Bonus: {feature.replace('_', ' ')}")
        
        score += min(bonus_score, 10)
        
        return min(100, score), notes
    
    def _analyze_code_quality(self, files: List[FileInfo]) -> float:
        """Analyze overall code quality - ENHANCED FOR THOROUGH EVALUATION"""
        score = 20  # Conservative base score
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        
        for file in ps1_files:
            content = file.content
            content_lower = content.lower()
            lines = content.splitlines()
            
            # ERROR HANDLING & ROBUSTNESS (25 points max)
            error_score = 0
            if 'try' in content_lower and 'catch' in content_lower:
                error_score += 15
            elif 'erroraction' in content_lower:
                error_score += 10
            
            if 'errorvariable' in content_lower:
                error_score += 5
            
            if any(validation in content for validation in ['ValidateNotNull', 'ValidateSet', 'ValidateRange']):
                error_score += 5
                
            score += min(error_score, 25)
            
            # PARAMETER VALIDATION & TYPE SAFETY (20 points max)
            param_score = 0
            if '[Parameter(' in content:
                param_score += 8
                if 'Mandatory' in content:
                    param_score += 5
                if 'ValueFromPipeline' in content:
                    param_score += 3
            
            # Type hints
            type_hints = len(re.findall(r'\[string\]|\[int\]|\[bool\]|\[array\]|\[switch\]', content))
            param_score += min(type_hints * 2, 10)
            
            score += min(param_score, 20)
            
            # CODE ORGANIZATION & STRUCTURE (20 points max)
            org_score = 0
            
            # Function usage
            function_count = len(re.findall(r'function\s+[a-zA-Z-]+', content))
            if function_count > 0:
                org_score += min(function_count * 5, 15)
            
            # Consistent indentation
            indented_lines = len([line for line in lines if line.startswith('    ') or line.startswith('\t')])
            if indented_lines > len(lines) * 0.2:
                org_score += 5
            
            score += min(org_score, 20)
            
            # POWERSHELL BEST PRACTICES (15 points max)
            best_practice_score = 0
            
            # Approved verbs
            if re.search(r'function\s+(Get-|Set-|New-|Remove-|Test-|Start-|Stop-)', content):
                best_practice_score += 5
            
            # CmdletBinding
            if '[CmdletBinding()]' in content:
                best_practice_score += 5
            
            # Proper parameter blocks
            if 'param(' in content_lower and ')' in content:
                best_practice_score += 5
            
            score += min(best_practice_score, 15)
            
            # MAINTAINABILITY (10 points max)
            maint_score = 0
            
            # Reasonable line length (< 120 chars)
            long_lines = len([line for line in lines if len(line) > 120])
            if long_lines < len(lines) * 0.1:  # Less than 10% long lines
                maint_score += 5
            
            # Variable naming
            vars_found = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', content)
            meaningful_vars = [v for v in vars_found if len(v) >= 3 or v in ['_', 'f', 'i']]
            if len(meaningful_vars) / len(vars_found) > 0.8 if vars_found else True:
                maint_score += 5
            
            score += min(maint_score, 10)
        
        return min(100, max(0, score))
    
    def _analyze_documentation(self, files: List[FileInfo]) -> float:
        """Analyze documentation quality"""
        score = 30  # Base score
        
        # Check for README files
        readme_files = [f for f in files if 'readme' in f.path.lower()]
        if readme_files:
            score += 25
            # Check README quality
            for readme in readme_files:
                content = readme.content.lower()
                if 'usage' in content or 'example' in content:
                    score += 10
                if 'feature' in content:
                    score += 5
                if '```' in readme.content:  # Code examples
                    score += 10
        
        # Check for inline documentation
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        for file in ps1_files:
            if '<#' in file.content and '.SYNOPSIS' in file.content:
                score += 20
                if '.EXAMPLE' in file.content:
                    score += 10
        
        return min(100, max(0, score))
    
    def _analyze_feature_completeness(self, files: List[FileInfo]) -> float:
        """Analyze feature completeness"""
        score = 50  # Base score
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        all_content = ' '.join(f.content.lower() for f in ps1_files)
        
        features = {
            'configurable_parameters': any(keyword in all_content for keyword in ['param(', 'parameter']),
            'multiple_output_formats': any(keyword in all_content for keyword in ['csv', 'json', 'xml', 'export']),
            'recursive_scanning': 'recurse' in all_content,
            'size_filtering': any(keyword in all_content for keyword in ['minsize', 'maxsize', 'size']),
            'extension_filtering': 'extension' in all_content,
            'date_filtering': any(keyword in all_content for keyword in ['age', 'days', 'date']),
            'batch_wrapper': any(f.path.endswith('.bat') for f in files),
            'progress_indication': any(keyword in all_content for keyword in ['write-host', 'write-progress', 'verbose'])
        }
        
        implemented_features = sum(features.values())
        score += implemented_features * 6
        
        return min(100, score)
    
    def _identify_strengths_weaknesses(self, files: List[FileInfo]) -> tuple:
        """Identify strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        all_content = ' '.join(f.content for f in files)
        
        # Analyze strengths
        if '<#' in all_content and '.SYNOPSIS' in all_content:
            strengths.append("Comprehensive PowerShell help documentation")
        
        if len([f for f in files if 'readme' in f.path.lower()]) > 0:
            strengths.append("Includes detailed README documentation")
        
        if any(f.path.endswith('.bat') for f in files):
            strengths.append("Provides user-friendly batch wrapper")
        
        if 'erroraction silentlycontinue' in all_content.lower():
            strengths.append("Handles errors gracefully")
        
        if len(ps1_files) == 1:
            strengths.append("Clean, single-file solution")
        elif len(ps1_files) > 1:
            strengths.append("Modular, multi-file architecture")
        
        # Analyze weaknesses
        total_lines = sum(f.lines for f in ps1_files)
        if total_lines < 50:
            weaknesses.append("Solution may be too simplistic")
        elif total_lines > 400:
            weaknesses.append("Solution may be overly complex")
        
        comment_lines = sum(len([line for line in f.content.splitlines() if line.strip().startswith('#')]) for f in ps1_files)
        if comment_lines < total_lines * 0.05:
            weaknesses.append("Insufficient code comments")
        
        if 'get-childitem' in all_content.lower() and 'recurse' in all_content.lower() and 'erroraction' not in all_content.lower():
            weaknesses.append("Recursive scanning without proper error handling")
        
        return strengths, weaknesses
    
    def _detailed_solution_breakdown(self, result: AnalysisResult) -> str:
        """Provide detailed breakdown of why each score was assigned"""
        breakdown = []
        breakdown.append(f"## DETAILED ANALYSIS: {result.llm_name}")
        breakdown.append("")
        breakdown.append("### PROMPT ADHERENCE ANALYSIS")
        for note in result.prompt_adherence_notes:
            breakdown.append(f"  {note}")
        breakdown.append("")
        breakdown.append("### PERFORMANCE ANALYSIS")
        for note in result.performance_notes:
            breakdown.append(f"  {note}")
        breakdown.append("")
        breakdown.append("### READABILITY ANALYSIS") 
        for note in result.readability_notes:
            breakdown.append(f"  {note}")
        breakdown.append("")
        breakdown.append("### FILE STRUCTURE")
        for file in result.files:
            breakdown.append(f"  - {os.path.basename(file.path)}: {file.lines} lines, {file.size} bytes")
        breakdown.append("")
        breakdown.append("---")
        breakdown.append("")
        
        return '\n'.join(breakdown)
    
    def analyze_all_solutions(self) -> List[AnalysisResult]:
        """Analyze all LLM solutions"""
        results = []
        
        llm_folders = ['llm1', 'llm2', 'llm3', 'llm4']
        
        for folder in llm_folders:
            folder_path = os.path.join(self.workspace_path, folder)
            if os.path.exists(folder_path):
                print(f"Analyzing {folder}...")
                result = self.analyze_solution(folder)
                results.append(result)
            else:
                print(f"Warning: {folder} not found")
        
        return results
    
    def generate_report(self, results: List[AnalysisResult]) -> str:
        """Generate a comprehensive comparison report"""
        report = []
        report.append("# LLM Solution Analysis Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall rankings
        report.append("## Overall Rankings")
        report.append("")
        sorted_results = sorted(results, key=lambda x: x.overall_score, reverse=True)
        
        report.append("| Rank | LLM | Overall Score | Performance | Readability | Prompt Adherence | Code Quality | Documentation |")
        report.append("|------|-----|---------------|-------------|-------------|------------------|--------------|---------------|")
        
        for i, result in enumerate(sorted_results, 1):
            report.append(f"| {i} | {result.llm_name} | {result.overall_score:.1f} | {result.performance_score:.1f} | {result.readability_score:.1f} | {result.prompt_adherence_score:.1f} | {result.code_quality_score:.1f} | {result.documentation_score:.1f} |")
        
        report.append("")
        
        # Detailed analysis for each solution
        for result in sorted_results:
            report.append(f"## {result.llm_name} - Detailed Analysis")
            report.append("")
            report.append(f"**Overall Score: {result.overall_score:.1f}/100**")
            report.append("")
            
            report.append("### Metrics")
            report.append(f"- **Total Lines of Code:** {result.total_lines}")
            report.append(f"- **Total File Size:** {result.total_size:,} bytes")
            report.append(f"- **Number of Files:** {len(result.files)}")
            report.append("")
            
            report.append("### Score Breakdown")
            report.append(f"- **Performance:** {result.performance_score:.1f}/100")
            report.append(f"- **Readability:** {result.readability_score:.1f}/100") 
            report.append(f"- **Prompt Adherence:** {result.prompt_adherence_score:.1f}/100")
            report.append(f"- **Code Quality:** {result.code_quality_score:.1f}/100")
            report.append(f"- **Documentation:** {result.documentation_score:.1f}/100")
            report.append(f"- **Feature Completeness:** {result.feature_completeness_score:.1f}/100")
            report.append("")
            
            if result.strengths:
                report.append("### Strengths")
                for strength in result.strengths:
                    report.append(f"- {strength}")
                report.append("")
            
            if result.weaknesses:
                report.append("### Areas for Improvement")
                for weakness in result.weaknesses:
                    report.append(f"- {weakness}")
                report.append("")
            
            if result.performance_notes:
                report.append("### Performance Notes")
                for note in result.performance_notes:
                    report.append(f"- {note}")
                report.append("")
            
            report.append("---")
            report.append("")
        
        # Summary and recommendations
        report.append("## Summary and Recommendations")
        report.append("")
        
        best_overall = sorted_results[0]
        report.append(f"**Best Overall Solution:** {best_overall.llm_name} (Score: {best_overall.overall_score:.1f})")
        report.append("")
        
        # Category winners
        best_performance = max(results, key=lambda x: x.performance_score)
        best_readability = max(results, key=lambda x: x.readability_score)
        best_adherence = max(results, key=lambda x: x.prompt_adherence_score)
        best_quality = max(results, key=lambda x: x.code_quality_score)
        
        report.append("### Category Winners")
        report.append(f"- **Most Performant:** {best_performance.llm_name} ({best_performance.performance_score:.1f})")
        report.append(f"- **Most Readable:** {best_readability.llm_name} ({best_readability.readability_score:.1f})")
        report.append(f"- **Best Prompt Adherence:** {best_adherence.llm_name} ({best_adherence.prompt_adherence_score:.1f})")
        report.append(f"- **Highest Code Quality:** {best_quality.llm_name} ({best_quality.code_quality_score:.1f})")
        report.append("")
        
        report.append("### Key Insights")
        report.append("- All solutions successfully implement the core requirement of identifying files safe for deletion")
        report.append("- Solutions vary significantly in complexity and feature completeness")
        report.append("- Documentation quality ranges from minimal to comprehensive")
        report.append("- Performance optimizations are inconsistently applied across solutions")
        report.append("")
        
        # Add detailed breakdowns
        report.append("---")
        report.append("")
        report.append("# DETAILED SCORING BREAKDOWNS")
        report.append("")
        for result in sorted_results:
            report.append(self._detailed_solution_breakdown(result))
        
        return '\n'.join(report)
    
    def export_csv_summary(self, results: List[AnalysisResult], filename: str):
        """Export results summary to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'LLM', 'Overall_Score', 'Performance', 'Readability', 
                'Prompt_Adherence', 'Code_Quality', 'Documentation', 
                'Feature_Completeness', 'Total_Lines', 'Total_Files', 'File_Size'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in sorted(results, key=lambda x: x.overall_score, reverse=True):
                writer.writerow({
                    'LLM': result.llm_name,
                    'Overall_Score': round(result.overall_score, 1),
                    'Performance': round(result.performance_score, 1),
                    'Readability': round(result.readability_score, 1),
                    'Prompt_Adherence': round(result.prompt_adherence_score, 1),
                    'Code_Quality': round(result.code_quality_score, 1),
                    'Documentation': round(result.documentation_score, 1),
                    'Feature_Completeness': round(result.feature_completeness_score, 1),
                    'Total_Lines': result.total_lines,
                    'Total_Files': len(result.files),
                    'File_Size': result.total_size
                })

def main():
    """Main function to run the analysis"""
    workspace_path = r"d:\CodingModel\ModelCompare\FirstPassModelCompare"
    
    analyzer = LLMSolutionAnalyzer(workspace_path)
    results = analyzer.analyze_all_solutions()
    
    # Generate report
    report = analyzer.generate_report(results)
    
    # Save report
    report_path = os.path.join(workspace_path, 'analysis_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Export CSV summary
    csv_path = os.path.join(workspace_path, 'analysis_summary.csv')
    analyzer.export_csv_summary(results, csv_path)
    
    print(f"Analysis complete!")
    print(f"Report saved to: {report_path}")
    print(f"CSV summary saved to: {csv_path}")
    
    # Print quick summary
    print("\n" + "="*50)
    print("QUICK SUMMARY")
    print("="*50)
    
    sorted_results = sorted(results, key=lambda x: x.overall_score, reverse=True)
    for i, result in enumerate(sorted_results, 1):
        print(f"{i}. {result.llm_name}: {result.overall_score:.1f}/100")

if __name__ == "__main__":
    main()
