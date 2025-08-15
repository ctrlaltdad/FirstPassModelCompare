#!/usr/bin/env python3
"""
Documentation Analysis Module

Analyzes documentation quality and completeness.
"""

import os
from typing import List, Dict, Any
from .base import BaseAnalyzer, FileInfo, AnalysisScore

class DocumentationAnalyzer(BaseAnalyzer):
    """Analyzes documentation quality and completeness"""
    
    def __init__(self):
        super().__init__(
            name="Documentation Analysis",
            description="Evaluates README files, inline documentation, and help system quality",
            weight=0.10
        )
    
    @property
    def category(self) -> str:
        return "documentation"
    
    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """Analyze documentation quality"""
        score = 30  # Base score
        notes = []
        details = {}
        
        # Analyze README files
        readme_score = self._analyze_readme_files(files)
        score += readme_score['score']
        notes.extend(readme_score['notes'])
        details.update(readme_score['details'])
        
        # Analyze inline documentation
        inline_score = self._analyze_inline_documentation(files)
        score += inline_score['score']
        notes.extend(inline_score['notes'])
        details.update(inline_score['details'])
        
        # Analyze help system
        help_score = self._analyze_help_system(files)
        score += help_score['score']
        notes.extend(help_score['notes'])
        details.update(help_score['details'])
        
        final_score = min(100, max(0, score))
        return AnalysisScore(score=final_score, notes=notes, details=details)
    
    def _analyze_readme_files(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Analyze README file quality (40 points max)"""
        score = 0
        notes = []
        details = {}
        
        readme_files = [f for f in files if 'readme' in f.path.lower()]
        details['readme_count'] = len(readme_files)
        
        if readme_files:
            score += 25
            notes.append("+ Includes README documentation")
            
            # Analyze README content quality
            for readme in readme_files:
                content = readme.content.lower()
                
                # Check for essential sections
                essential_sections = {
                    'usage': ['usage', 'how to use', 'getting started'],
                    'examples': ['example', 'sample', 'demo'],
                    'features': ['feature', 'capability', 'what it does'],
                    'installation': ['install', 'setup', 'requirements'],
                    'parameters': ['parameter', 'option', 'argument']
                }
                
                found_sections = []
                for section_name, keywords in essential_sections.items():
                    if any(keyword in content for keyword in keywords):
                        found_sections.append(section_name)
                        score += 2
                
                details['readme_sections_found'] = found_sections
                
                if found_sections:
                    notes.append(f"+ README contains: {', '.join(found_sections)}")
                
                # Check for code examples
                if '```' in readme.content:  # Markdown code blocks
                    score += 5
                    notes.append("+ README includes code examples")
                    details['has_code_examples'] = True
                
                # Check for comprehensive documentation
                if len(readme.content) > 1000:  # Substantial documentation
                    score += 3
                    notes.append("+ Comprehensive README documentation")
                    details['comprehensive_readme'] = True
        else:
            notes.append("- No README documentation found")
            details['has_readme'] = False
        
        details['readme_analysis_score'] = min(score, 40)
        return {'score': min(score, 40), 'notes': notes, 'details': details}
    
    def _analyze_inline_documentation(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Analyze inline documentation in code files (30 points max)"""
        score = 0
        notes = []
        details = {}
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        
        if not ps1_files:
            details['inline_analysis_score'] = 0
            return {'score': 0, 'notes': ['- No PowerShell files to analyze'], 'details': details}
        
        total_comment_density = 0
        files_with_headers = 0
        
        for file in ps1_files:
            lines = file.content.splitlines()
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            comment_density = comment_lines / len(lines) if lines else 0
            total_comment_density += comment_density
            
            # Check for file header comments
            if lines and lines[0].strip().startswith('#'):
                files_with_headers += 1
        
        avg_comment_density = total_comment_density / len(ps1_files)
        details['average_comment_density'] = avg_comment_density
        details['files_with_headers'] = files_with_headers
        
        # Score based on comment density
        if avg_comment_density > 0.15:
            score += 15
            notes.append("+ Excellent inline commenting (>15% average)")
        elif avg_comment_density > 0.10:
            score += 10
            notes.append("+ Good inline commenting (>10% average)")
        elif avg_comment_density > 0.05:
            score += 5
            notes.append("+ Adequate inline commenting (>5% average)")
        else:
            notes.append("- Low inline commenting density")
        
        # Score based on file headers
        if files_with_headers == len(ps1_files):
            score += 10
            notes.append("+ All files have header comments")
        elif files_with_headers > 0:
            score += 5
            notes.append(f"+ {files_with_headers}/{len(ps1_files)} files have header comments")
        
        # Check for section comments
        section_comments = 0
        for file in ps1_files:
            section_comments += len([line for line in file.content.splitlines() 
                                   if line.strip().startswith('#') and len(line.strip()) > 10])
        
        details['section_comments'] = section_comments
        if section_comments > len(ps1_files) * 3:  # More than 3 section comments per file on average
            score += 5
            notes.append("+ Good use of section comments")
        
        details['inline_analysis_score'] = min(score, 30)
        return {'score': min(score, 30), 'notes': notes, 'details': details}
    
    def _analyze_help_system(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Analyze PowerShell help system (30 points max)"""
        score = 0
        notes = []
        details = {}
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        
        if not ps1_files:
            details['help_analysis_score'] = 0
            return {'score': 0, 'notes': ['- No PowerShell files to analyze'], 'details': details}
        
        files_with_help = 0
        comprehensive_help_files = 0
        
        for file in ps1_files:
            content = file.content
            
            # Check for PowerShell help block
            if '<#' in content and '.SYNOPSIS' in content:
                files_with_help += 1
                
                # Check for comprehensive help sections
                help_sections = ['.SYNOPSIS', '.DESCRIPTION', '.PARAMETER', '.EXAMPLE', '.NOTES', '.LINK']
                found_help_sections = [section for section in help_sections if section in content]
                
                if len(found_help_sections) >= 4:
                    comprehensive_help_files += 1
        
        details['files_with_help'] = files_with_help
        details['comprehensive_help_files'] = comprehensive_help_files
        details['total_ps1_files'] = len(ps1_files)
        
        # Score based on help coverage
        help_coverage = files_with_help / len(ps1_files)
        details['help_coverage'] = help_coverage
        
        if help_coverage == 1.0:
            score += 20
            notes.append("+ All PowerShell files have help documentation")
        elif help_coverage >= 0.5:
            score += 15
            notes.append(f"+ {files_with_help}/{len(ps1_files)} files have help documentation")
        elif files_with_help > 0:
            score += 10
            notes.append(f"+ {files_with_help}/{len(ps1_files)} files have help documentation")
        else:
            notes.append("- No PowerShell help documentation found")
        
        # Score based on comprehensive help
        if comprehensive_help_files > 0:
            score += 10
            notes.append(f"+ {comprehensive_help_files} files have comprehensive help (4+ sections)")
        
        details['help_analysis_score'] = min(score, 30)
        return {'score': min(score, 30), 'notes': notes, 'details': details}
