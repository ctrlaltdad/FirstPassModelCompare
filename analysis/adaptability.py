#!/usr/bin/env python3
"""
Adaptability Analysis Module

Evaluates how well a solution can adapt to different environments, requirements changes,
and use cases. Assesses configurability, extensibility, and cross-platform compatibility.
"""

import re
from typing import List, Dict, Any
from .base import BaseAnalyzer, FileInfo, AnalysisScore

class AdaptabilityAnalyzer(BaseAnalyzer):
    """
    Analyzes the adaptability and flexibility of code solutions.
    
    Evaluation criteria:
    - Configuration flexibility (parameters, settings files)
    - Cross-platform compatibility
    - Extensibility (modular design, hooks for customization)
    - Environment adaptation (path handling, OS detection)
    - Input/output flexibility
    - Error recovery and graceful degradation
    """
    
    def __init__(self):
        super().__init__(
            name="Adaptability Analysis",
            description="Evaluates solution flexibility, configurability, and cross-platform compatibility",
            weight=0.10  # 10% weight
        )
    
    def get_name(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return self.description
    
    def analyze(self, files: List[FileInfo], llm_name: str, requirements: Dict[str, Any]) -> AnalysisScore:
        """Perform comprehensive adaptability analysis"""
        
        # Initialize scoring components
        configuration_score = 0
        cross_platform_score = 0
        extensibility_score = 0
        environment_adaptation_score = 0
        input_output_flexibility_score = 0
        error_recovery_score = 0
        
        notes = []
        
        total_files = len(files)
        if total_files == 0:
            return AnalysisScore(0.0, ["No files found for analysis"], {})
        
        # Analyze each file
        for file_info in files:
            if file_info.path.endswith('.ps1'):
                config_score, config_notes = self._analyze_configuration_flexibility(file_info.content)
                platform_score, platform_notes = self._analyze_cross_platform_compatibility(file_info.content)
                extend_score, extend_notes = self._analyze_extensibility(file_info.content)
                env_score, env_notes = self._analyze_environment_adaptation(file_info.content)
                io_score, io_notes = self._analyze_input_output_flexibility(file_info.content)
                recovery_score, recovery_notes = self._analyze_error_recovery(file_info.content)
                
                configuration_score += config_score
                cross_platform_score += platform_score
                extensibility_score += extend_score
                environment_adaptation_score += env_score
                input_output_flexibility_score += io_score
                error_recovery_score += recovery_score
                
                notes.extend(config_notes)
                notes.extend(platform_notes)
                notes.extend(extend_notes)
                notes.extend(env_notes)
                notes.extend(io_notes)
                notes.extend(recovery_notes)
        
        # Calculate component scores (normalized)
        config_final = min(100, (configuration_score / total_files) * 10)
        platform_final = min(100, (cross_platform_score / total_files) * 10)
        extend_final = min(100, (extensibility_score / total_files) * 10)
        env_final = min(100, (environment_adaptation_score / total_files) * 10)
        io_final = min(100, (input_output_flexibility_score / total_files) * 10)
        recovery_final = min(100, (error_recovery_score / total_files) * 10)
        
        # Weighted final score
        final_score = (
            config_final * 0.25 +           # Configuration flexibility: 25%
            platform_final * 0.20 +         # Cross-platform compatibility: 20%
            extend_final * 0.20 +            # Extensibility: 20%
            env_final * 0.15 +               # Environment adaptation: 15%
            io_final * 0.10 +                # Input/output flexibility: 10%
            recovery_final * 0.10            # Error recovery: 10%
        )
        
        # Generate summary notes
        summary_notes = [
            f"Configuration Flexibility: {config_final:.1f}/100",
            f"Cross-Platform Compatibility: {platform_final:.1f}/100",
            f"Extensibility: {extend_final:.1f}/100",
            f"Environment Adaptation: {env_final:.1f}/100",
            f"Input/Output Flexibility: {io_final:.1f}/100",
            f"Error Recovery: {recovery_final:.1f}/100"
        ]
        
        # Add component breakdown
        if config_final >= 80:
            summary_notes.append("✓ Excellent configuration options")
        elif config_final >= 60:
            summary_notes.append("⚡ Good configuration flexibility")
        else:
            summary_notes.append("❌ Limited configuration options")
            
        if platform_final >= 80:
            summary_notes.append("✓ Strong cross-platform design")
        elif platform_final >= 60:
            summary_notes.append("⚡ Some cross-platform considerations")
        else:
            summary_notes.append("❌ Platform-specific limitations")
            
        if extend_final >= 80:
            summary_notes.append("✓ Highly extensible architecture")
        elif extend_final >= 60:
            summary_notes.append("⚡ Moderately extensible design")
        else:
            summary_notes.append("❌ Limited extensibility")
        
        return AnalysisScore(
            round(final_score, 1),
            summary_notes,  # Store summary in notes for dashboard
            {
                'configuration_score': config_final,
                'cross_platform_score': platform_final,
                'extensibility_score': extend_final,
                'environment_adaptation_score': env_final,
                'input_output_flexibility_score': io_final,
                'error_recovery_score': recovery_final,
                'detailed_notes': notes[:15]  # Detailed notes in details
            }
        )
    
    def _analyze_configuration_flexibility(self, content: str) -> tuple[int, List[str]]:
        """Analyze how configurable and parameterizable the solution is"""
        score = 0
        notes = []
        
        # Check for PowerShell parameters
        param_patterns = [
            r'\[Parameter\(',
            r'\[CmdletBinding\(',
            r'param\s*\(',
            r'\$\w+\s*=\s*[^,\)]+',  # Default parameter values
        ]
        
        for pattern in param_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            if matches > 0:
                score += min(matches, 3)  # Cap contribution
                notes.append(f"+ {matches} configurable parameters found")
        
        # Check for configuration files or settings
        config_patterns = [
            r'\.config',
            r'\.json',
            r'\.xml',
            r'\.ini',
            r'settings?',
            r'configuration'
        ]
        
        for pattern in config_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append(f"+ Configuration file support detected")
                break
        
        # Check for environment variables
        env_patterns = [
            r'\$env:',
            r'Get-ChildItem\s+env:',
            r'\[Environment\]::GetEnvironmentVariable'
        ]
        
        for pattern in env_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append(f"+ Environment variable usage found")
                break
        
        # Check for switch parameters
        if re.search(r'\[switch\]', content, re.IGNORECASE):
            score += 2
            notes.append("+ Switch parameters for boolean options")
        
        # Check for parameter validation
        validation_patterns = [
            r'ValidateSet',
            r'ValidateRange',
            r'ValidateScript',
            r'ValidateNotNull'
        ]
        
        for pattern in validation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 1
                notes.append("+ Parameter validation implemented")
                break
        
        return score, notes
    
    def _analyze_cross_platform_compatibility(self, content: str) -> tuple[int, List[str]]:
        """Analyze cross-platform compatibility considerations"""
        score = 0
        notes = []
        
        # Check for OS detection
        os_detection_patterns = [
            r'\$IsWindows',
            r'\$IsLinux',
            r'\$IsMacOS',
            r'\[Environment\]::OSVersion',
            r'Get-ComputerInfo',
            r'\$PSVersionTable'
        ]
        
        for pattern in os_detection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 3
                notes.append("+ Operating system detection implemented")
                break
        
        # Check for path handling
        path_patterns = [
            r'Join-Path',
            r'\[System\.IO\.Path\]',
            r'Split-Path',
            r'Resolve-Path'
        ]
        
        for pattern in path_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append("+ Proper path handling methods used")
                break
        
        # Check for hardcoded paths (negative)
        hardcoded_patterns = [
            r'C:\\',
            r'D:\\',
            r'/home/',
            r'/usr/',
            r'\\\\server\\'
        ]
        
        hardcoded_found = False
        for pattern in hardcoded_patterns:
            if re.search(pattern, content):
                score -= 2
                hardcoded_found = True
        
        if hardcoded_found:
            notes.append("- Hardcoded paths detected (reduces portability)")
        
        # Check for PowerShell Core features
        core_patterns = [
            r'pwsh',
            r'PowerShell\s+7',
            r'Core',
            r'\$PSEdition.*Core'
        ]
        
        for pattern in core_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append("+ PowerShell Core compatibility considered")
                break
        
        # Check for cross-platform cmdlets
        cross_platform_cmdlets = [
            r'Get-ChildItem',
            r'Test-Path',
            r'New-Item',
            r'Remove-Item',
            r'Copy-Item',
            r'Move-Item'
        ]
        
        cross_platform_count = 0
        for pattern in cross_platform_cmdlets:
            if re.search(pattern, content, re.IGNORECASE):
                cross_platform_count += 1
        
        if cross_platform_count >= 3:
            score += 2
            notes.append("+ Uses cross-platform PowerShell cmdlets")
        
        return score, notes
    
    def _analyze_extensibility(self, content: str) -> tuple[int, List[str]]:
        """Analyze how extensible and modular the solution is"""
        score = 0
        notes = []
        
        # Check for functions (modularity)
        function_count = len(re.findall(r'function\s+[\w-]+', content, re.IGNORECASE))
        if function_count >= 3:
            score += 3
            notes.append(f"+ Well-modularized with {function_count} functions")
        elif function_count >= 1:
            score += 2
            notes.append(f"+ Some modularity with {function_count} function(s)")
        
        # Check for script modules
        module_patterns = [
            r'\.psm1',
            r'Import-Module',
            r'Export-ModuleMember',
            r'New-Module'
        ]
        
        for pattern in module_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 3
                notes.append("+ Module-based architecture detected")
                break
        
        # Check for plugin/extension points
        extension_patterns = [
            r'plugin',
            r'extension',
            r'hook',
            r'callback',
            r'delegate',
            r'ScriptBlock'
        ]
        
        for pattern in extension_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append("+ Extension/plugin architecture found")
                break
        
        # Check for configuration-driven behavior
        config_driven_patterns = [
            r'foreach.*\$_',
            r'\.ForEach\(',
            r'Where-Object',
            r'Select-Object'
        ]
        
        config_driven_count = 0
        for pattern in config_driven_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                config_driven_count += 1
        
        if config_driven_count >= 2:
            score += 2
            notes.append("+ Data-driven processing patterns detected")
        
        # Check for inheritance or class-based design
        if re.search(r'class\s+\w+', content, re.IGNORECASE):
            score += 3
            notes.append("+ Object-oriented design with classes")
        
        return score, notes
    
    def _analyze_environment_adaptation(self, content: str) -> tuple[int, List[str]]:
        """Analyze how well the solution adapts to different environments"""
        score = 0
        notes = []
        
        # Check for permission handling
        permission_patterns = [
            r'Test-Administrator',
            r'RunAsAdministrator',
            r'Elevate',
            r'UAC',
            r'Principal',
            r'WindowsIdentity'
        ]
        
        for pattern in permission_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append("+ Permission/elevation handling detected")
                break
        
        # Check for registry access (environment-specific)
        if re.search(r'Registry|HKEY_|Get-ItemProperty.*HKLM', content, re.IGNORECASE):
            score += 1
            notes.append("+ Registry access for system information")
        
        # Check for service/process adaptation
        service_patterns = [
            r'Get-Service',
            r'Get-Process',
            r'Start-Service',
            r'Stop-Service'
        ]
        
        for pattern in service_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 1
                notes.append("+ System service interaction capability")
                break
        
        # Check for network/remote capability
        network_patterns = [
            r'Invoke-WebRequest',
            r'Invoke-RestMethod',
            r'Test-NetConnection',
            r'New-PSSession',
            r'Enter-PSSession'
        ]
        
        for pattern in network_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append("+ Network/remote operation capability")
                break
        
        # Check for PowerShell version compatibility
        version_patterns = [
            r'\$PSVersionTable',
            r'requires.*version',
            r'#Requires'
        ]
        
        for pattern in version_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append("+ PowerShell version compatibility checks")
                break
        
        return score, notes
    
    def _analyze_input_output_flexibility(self, content: str) -> tuple[int, List[str]]:
        """Analyze input/output flexibility and format support"""
        score = 0
        notes = []
        
        # Check for multiple output formats
        output_patterns = [
            r'ConvertTo-Json',
            r'ConvertTo-Csv',
            r'ConvertTo-Xml',
            r'ConvertTo-Html',
            r'Export-Csv',
            r'Export-Clixml'
        ]
        
        output_formats = 0
        for pattern in output_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                output_formats += 1
        
        if output_formats >= 2:
            score += 3
            notes.append(f"+ Multiple output formats supported ({output_formats} types)")
        elif output_formats == 1:
            score += 2
            notes.append("+ Alternative output format available")
        
        # Check for pipeline support
        pipeline_patterns = [
            r'\|\s*\w+',
            r'ValueFromPipeline',
            r'ValueFromPipelineByPropertyName',
            r'Process\s*{'
        ]
        
        for pattern in pipeline_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2
                notes.append("+ PowerShell pipeline integration")
                break
        
        # Check for flexible input sources
        input_patterns = [
            r'Get-Content',
            r'Import-Csv',
            r'Import-Clixml',
            r'ConvertFrom-Json',
            r'Read-Host'
        ]
        
        for pattern in input_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 1
                notes.append("+ Flexible input source handling")
                break
        
        # Check for output customization
        if re.search(r'Format-Table|Format-List|Select-Object.*@{', content, re.IGNORECASE):
            score += 2
            notes.append("+ Customizable output formatting")
        
        return score, notes
    
    def _analyze_error_recovery(self, content: str) -> tuple[int, List[str]]:
        """Analyze error handling and graceful degradation"""
        score = 0
        notes = []
        
        # Check for comprehensive error handling
        error_patterns = [
            r'try\s*{.*}.*catch',
            r'trap\s*{',
            r'-ErrorAction',
            r'\$Error\[',
            r'\$LastExitCode'
        ]
        
        error_handling_count = 0
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                error_handling_count += 1
        
        if error_handling_count >= 3:
            score += 3
            notes.append("+ Comprehensive error handling implemented")
        elif error_handling_count >= 1:
            score += 2
            notes.append("+ Basic error handling present")
        
        # Check for graceful degradation
        degradation_patterns = [
            r'if.*Test-Path',
            r'if.*Get-Command',
            r'SilentlyContinue',
            r'Ignore'
        ]
        
        for pattern in degradation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 1
                notes.append("+ Graceful degradation patterns detected")
                break
        
        # Check for retry mechanisms
        retry_patterns = [
            r'do\s*{.*}.*while',
            r'for.*retry',
            r'while.*attempt'
        ]
        
        for pattern in retry_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                score += 2
                notes.append("+ Retry mechanism implemented")
                break
        
        # Check for logging/debugging support
        logging_patterns = [
            r'Write-Debug',
            r'Write-Verbose',
            r'Write-Warning',
            r'Write-Information',
            r'Start-Transcript',
            r'Add-Content.*log'
        ]
        
        for pattern in logging_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 1
                notes.append("+ Logging/debugging support included")
                break
        
        return score, notes
