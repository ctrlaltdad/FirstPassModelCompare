#!/usr/bin/env python3
"""
Security Analysis Module

Evaluates PowerShell scripts for common security vulnerabilities and best practices.
"""

import re
from typing import List, Dict, Any
from analysis.base import BaseAnalyzer, AnalysisScore, FileInfo

class SecurityAnalyzer(BaseAnalyzer):
    """Analyzes PowerShell scripts for security vulnerabilities and best practices"""
    
    def __init__(self):
        super().__init__(
            name="Security Analysis",
            description="Evaluates security vulnerabilities, input validation, and safe coding practices",
            weight=0.20  # 20% weight - security is critical
        )
        
        # Define security vulnerability patterns
        self.critical_vulnerabilities = {
            'code_injection': [
                r'Invoke-Expression\s*\$',  # Dynamic code execution with variables
                r'iex\s*\$',  # Short form of Invoke-Expression
                r'&\s*\$\w+',  # Call operator with variables (more specific)
                r'^\s*\.\s*\$',  # Dot sourcing with variables at start of line
            ],
            'command_injection': [
                r'cmd\s*/c\s*\$',  # cmd.exe with variables
                r'Start-Process.*\$.*-ArgumentList',  # Process start with variable args
                r'System\.Diagnostics\.Process.*\$',  # .NET process with variables
            ],
            'path_traversal': [
                r'\.\./|\.\.\\',  # Directory traversal patterns
                r'\.\.[\\/]',  # Various path traversal
            ],
            'credential_exposure': [
                r'password\s*=\s*["\'].*["\']',  # Hardcoded passwords
                r'ConvertTo-SecureString.*-AsPlainText',  # Plain text to secure string
                r'credential.*=.*Get-Credential.*-Password',  # Credential handling
            ]
        }
        
        self.high_risk_patterns = {
            'unsafe_file_operations': [
                r'Remove-Item.*-Recurse.*-Force',  # Dangerous file deletion
                r'rm\s.*-rf',  # Unix-style dangerous deletion
                r'del\s.*\/s',  # Windows dangerous deletion
                r'Get-ChildItem.*\|\s*Remove-Item',  # Piped deletions
            ],
            'network_security': [
                r'Invoke-WebRequest.*-Uri\s*\$',  # Dynamic URLs
                r'wget\s*\$',  # wget with variables
                r'curl\s*\$',  # curl with variables
                r'-UseBasicParsing',  # Bypassing security
            ],
            'execution_policy': [
                r'Set-ExecutionPolicy.*Unrestricted',  # Dangerous execution policy
                r'ExecutionPolicy.*Bypass',  # Bypassing execution policy
                r'-ExecutionPolicy\s+Unrestricted',  # Parameter bypass
            ],
            'registry_access': [
                r'Set-ItemProperty.*HKLM',  # System registry modification
                r'New-ItemProperty.*HKCU.*-Force',  # Forced registry changes
                r'Remove-ItemProperty.*HKEY',  # Registry deletion
            ]
        }
        
        self.medium_risk_patterns = {
            'input_validation': [
                r'param\s*\([^)]*\)\s*(?!.*\[ValidateScript)',  # Parameters without validation
                r'Read-Host(?!.*-AsSecureString)',  # Unprotected input
                r'\$args\[\d+\]',  # Direct argument access
            ],
            'error_handling': [
                r'-ErrorAction\s+SilentlyContinue(?!.*try)',  # Hiding errors without try-catch
                r'Out-Null.*2>&1',  # Suppressing all output
            ],
            'privilege_escalation': [
                r'Start-Process.*-Verb\s+RunAs',  # Elevation requests
                r'UAC',  # UAC references
                r'Administrator',  # Admin references
            ]
        }
        
        self.good_practices = {
            'input_validation': [
                r'\[ValidateScript\(',  # Script validation
                r'\[ValidateSet\(',  # Set validation
                r'\[ValidatePattern\(',  # Pattern validation
                r'\[ValidateNotNullOrEmpty\(',  # Null/empty validation
                r'\[ValidateLength\(',  # Length validation
                r'\[ValidateRange\(',  # Range validation
            ],
            'secure_coding': [
                r'ConvertTo-SecureString',  # Secure string usage
                r'Get-Credential',  # Proper credential handling
                r'-AsSecureString',  # Secure string parameters
                r'try\s*\{.*catch',  # Proper error handling
                r'-WhatIf',  # What-if support
                r'-Confirm',  # Confirmation support
            ],
            'safe_file_operations': [
                r'-ErrorAction\s+Stop',  # Stopping on errors
                r'Test-Path',  # Path validation
                r'-LiteralPath',  # Literal path usage
                r'Resolve-Path',  # Path resolution
            ],
            'logging_auditing': [
                r'Write-Verbose',  # Verbose logging
                r'Write-Warning',  # Warning messages
                r'Write-Error',  # Error logging
                r'Write-Information',  # Information logging
                r'Write-Debug',  # Debug logging
            ]
        }

    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """Perform security analysis on the files"""
        
        # Combine all PowerShell content
        all_content = ""
        ps_files = [f for f in files if f.path.endswith('.ps1')]
        
        for file in ps_files:
            all_content += file.content + "\n"
        
        if not all_content.strip():
            return AnalysisScore(0, ["No PowerShell files found for security analysis"], {})
        
        # Perform security analysis
        security_issues = self._find_security_issues(all_content)
        good_practices_found = self._find_good_practices(all_content)
        
        # Calculate security score
        score = self._calculate_security_score(security_issues, good_practices_found, len(ps_files))
        
        # Generate analysis notes
        notes = self._generate_security_notes(security_issues, good_practices_found)
        
        # Detailed analysis results
        details = {
            'security_issues': security_issues,
            'good_practices': good_practices_found,
            'files_analyzed': len(ps_files),
            'total_content_length': len(all_content),
            'security_score_breakdown': self._get_score_breakdown(security_issues, good_practices_found)
        }
        
        return AnalysisScore(score, notes, details)
    
    def _find_security_issues(self, content: str) -> Dict[str, List[str]]:
        """Find security vulnerabilities in the content"""
        issues = {}
        
        # Check critical vulnerabilities
        for category, patterns in self.critical_vulnerabilities.items():
            matches = []
            for pattern in patterns:
                matches.extend(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            if matches:
                issues[f"CRITICAL_{category}"] = matches
        
        # Check high risk patterns
        for category, patterns in self.high_risk_patterns.items():
            matches = []
            for pattern in patterns:
                matches.extend(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            if matches:
                issues[f"HIGH_{category}"] = matches
        
        # Check medium risk patterns
        for category, patterns in self.medium_risk_patterns.items():
            matches = []
            for pattern in patterns:
                matches.extend(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            if matches:
                issues[f"MEDIUM_{category}"] = matches
        
        return issues
    
    def _find_good_practices(self, content: str) -> Dict[str, List[str]]:
        """Find good security practices in the content"""
        practices = {}
        
        for category, patterns in self.good_practices.items():
            matches = []
            for pattern in patterns:
                matches.extend(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            if matches:
                practices[category] = matches
        
        return practices
    
    def _calculate_security_score(self, issues: Dict[str, List[str]], practices: Dict[str, List[str]], file_count: int) -> float:
        """Calculate the overall security score"""
        base_score = 100.0
        
        # Deduct points for security issues (adjusted for less harsh scoring)
        for issue_type, matches in issues.items():
            if issue_type.startswith('CRITICAL_'):
                base_score -= len(matches) * 15  # Critical issues: -15 points each (reduced from 25)
            elif issue_type.startswith('HIGH_'):
                base_score -= len(matches) * 10  # High risk: -10 points each (reduced from 15)
            elif issue_type.startswith('MEDIUM_'):
                base_score -= len(matches) * 3   # Medium risk: -3 points each (reduced from 5)
        
        # Add points for good practices (up to 30 bonus points)
        practice_bonus = 0
        for practice_type, matches in practices.items():
            practice_bonus += min(len(matches) * 3, 8)  # Max 8 points per practice type
        
        practice_bonus = min(practice_bonus, 30)  # Cap at 30 bonus points
        
        # Apply file count bonus (more files analyzed = more thorough)
        file_bonus = min(file_count * 3, 15)
        
        final_score = base_score + practice_bonus + file_bonus
        
        return max(0, min(100, final_score))  # Ensure score is between 0-100
    
    def _generate_security_notes(self, issues: Dict[str, List[str]], practices: Dict[str, List[str]]) -> List[str]:
        """Generate human-readable security analysis notes"""
        notes = []
        
        # Report critical issues
        critical_count = sum(len(matches) for issue_type, matches in issues.items() if issue_type.startswith('CRITICAL_'))
        if critical_count > 0:
            notes.append(f"🚨 {critical_count} CRITICAL security vulnerabilities found")
        else:
            notes.append("✓ No critical security vulnerabilities detected")
        
        # Report high risk issues
        high_count = sum(len(matches) for issue_type, matches in issues.items() if issue_type.startswith('HIGH_'))
        if high_count > 0:
            notes.append(f"⚠️ {high_count} HIGH risk security issues found")
        else:
            notes.append("✓ No high-risk security issues detected")
        
        # Report medium risk issues
        medium_count = sum(len(matches) for issue_type, matches in issues.items() if issue_type.startswith('MEDIUM_'))
        if medium_count > 0:
            notes.append(f"⚡ {medium_count} MEDIUM risk security issues found")
        
        # Report good practices
        practice_count = sum(len(matches) for matches in practices.values())
        if practice_count > 10:
            notes.append(f"✅ Excellent security practices ({practice_count} detected)")
        elif practice_count > 5:
            notes.append(f"✓ Good security practices ({practice_count} detected)")
        elif practice_count > 0:
            notes.append(f"⚪ Some security practices found ({practice_count} detected)")
        else:
            notes.append("❌ No security best practices detected")
        
        # Specific issue details
        for issue_type, matches in issues.items():
            if matches:
                risk_level = issue_type.split('_')[0]
                category = '_'.join(issue_type.split('_')[1:])
                notes.append(f"- {risk_level}: {category.replace('_', ' ').title()} ({len(matches)} instances)")
        
        # Specific practice details
        for practice_type, matches in practices.items():
            if matches:
                notes.append(f"+ {practice_type.replace('_', ' ').title()}: {len(matches)} instances")
        
        return notes
    
    def _get_score_breakdown(self, issues: Dict[str, List[str]], practices: Dict[str, List[str]]) -> Dict[str, Any]:
        """Get detailed score breakdown"""
        return {
            'critical_issues': sum(len(matches) for issue_type, matches in issues.items() if issue_type.startswith('CRITICAL_')),
            'high_risk_issues': sum(len(matches) for issue_type, matches in issues.items() if issue_type.startswith('HIGH_')),
            'medium_risk_issues': sum(len(matches) for issue_type, matches in issues.items() if issue_type.startswith('MEDIUM_')),
            'good_practices_count': sum(len(matches) for matches in practices.values()),
            'security_categories_analyzed': len(self.critical_vulnerabilities) + len(self.high_risk_patterns) + len(self.medium_risk_patterns),
            'practice_categories_found': len(practices)
        }
