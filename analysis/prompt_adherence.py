#!/usr/bin/env python3
"""
Prompt Adherence Analysis Module

Analyzes how well solutions adhere to the original prompt requirements.
"""

import re
from typing import List, Dict, Any
from .base import BaseAnalyzer, FileInfo, AnalysisScore

class PromptAdherenceAnalyzer(BaseAnalyzer):
    """Analyzes adherence to the original prompt requirements"""
    
    def __init__(self):
        super().__init__(
            name="Prompt Adherence Analysis",
            description="Evaluates how well the solution follows the original requirements",
            weight=0.25
        )
    
    @property
    def category(self) -> str:
        return "requirements"
    
    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """Analyze prompt adherence"""
        score = 0  # Start from 0 for objective scoring
        notes = []
        details = {}
        
        ps1_files = [f for f in files if f.path.endswith('.ps1')]
        all_content = ' '.join(f.content for f in ps1_files)
        all_content_lower = all_content.lower()
        
        # REQUIREMENT 1: Windows script (20 points)
        windows_score = self._check_windows_compatibility(ps1_files)
        score += windows_score['score']
        notes.extend(windows_score['notes'])
        details.update(windows_score['details'])
        
        # REQUIREMENT 2: Identifies files safe to delete (20 points)
        identification_score = self._check_file_identification(all_content_lower)
        score += identification_score['score']
        notes.extend(identification_score['notes'])
        details.update(identification_score['details'])
        
        # REQUIREMENT 3: Does NOT delete files (15 points)
        safety_score = self._check_no_deletion(all_content, all_content_lower)
        score += safety_score['score']
        notes.extend(safety_score['notes'])
        details.update(safety_score['details'])
        
        # REQUIREMENT 4: Provides ranking/safety score (15 points)
        ranking_score = self._check_ranking_system(all_content_lower)
        score += ranking_score['score']
        notes.extend(ranking_score['notes'])
        details.update(ranking_score['details'])
        
        # REQUIREMENT 5: Required output fields (30 points total - 5 each)
        fields_score = self._check_required_fields(all_content_lower)
        score += fields_score['score']
        notes.extend(fields_score['notes'])
        details.update(fields_score['details'])
        
        # Bonus points for going beyond requirements (max 10 points)
        bonus_score = self._check_bonus_features(all_content_lower)
        score += bonus_score['score']
        notes.extend(bonus_score['notes'])
        details.update(bonus_score['details'])
        
        final_score = min(100, score)
        return AnalysisScore(score=final_score, notes=notes, details=details)
    
    def _check_windows_compatibility(self, ps1_files: List[FileInfo]) -> Dict[str, Any]:
        """Check Windows compatibility"""
        score = 0
        notes = []
        details = {}
        
        if ps1_files:
            score += 20
            notes.append("✓ Creates Windows-compatible PowerShell script")
            details['windows_compatible'] = True
        else:
            notes.append("✗ No PowerShell files found")
            details['windows_compatible'] = False
        
        details['powershell_file_count'] = len(ps1_files)
        return {'score': score, 'notes': notes, 'details': details}
    
    def _check_file_identification(self, content_lower: str) -> Dict[str, Any]:
        """Check if solution identifies files for deletion"""
        score = 0
        notes = []
        details = {}
        
        safety_indicators = ['safe', 'delete', 'safety', 'risk', 'dangerous']
        found_indicators = [indicator for indicator in safety_indicators if indicator in content_lower]
        details['safety_indicators_found'] = found_indicators
        
        if found_indicators:
            score += 20
            notes.append("✓ Identifies files for potential deletion")
            details['identifies_files'] = True
        else:
            notes.append("✗ Does not clearly identify deletion candidates")
            details['identifies_files'] = False
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _check_no_deletion(self, all_content: str, content_lower: str) -> Dict[str, Any]:
        """Check that solution doesn't actually delete files"""
        score = 0
        notes = []
        details = {}
        
        # Check for explicit statements about not deleting
        deletion_protection = any(phrase in content_lower for phrase in [
            'does not delete', 'not delete', 'no delete', 'only identifies', 
            'only reports', 'never deletes'
        ])
        details['has_deletion_protection_statement'] = deletion_protection
        
        # Check for actual deletion commands (should NOT be present)
        dangerous_patterns = [
            r'\bremove-item\s+',
            r'\bdel\s+[^\s]',
            r'\berase\s+[^\s]',
            r'\brm\s+[^\s]'
        ]
        
        has_deletion_commands = False
        for pattern in dangerous_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                matches = re.finditer(pattern, all_content, re.IGNORECASE)
                for match in matches:
                    start = all_content.rfind('\n', 0, match.start()) + 1
                    end = all_content.find('\n', match.end())
                    if end == -1:
                        end = len(all_content)
                    line = all_content[start:end].strip()
                    
                    if not (line.startswith('#') or '"delete' in line.lower() or 
                           "'delete" in line.lower() or 'does not' in line.lower() or 
                           'not perform' in line.lower()):
                        has_deletion_commands = True
                        break
                if has_deletion_commands:
                    break
        
        details['has_deletion_commands'] = has_deletion_commands
        
        if deletion_protection and not has_deletion_commands:
            score += 15
            notes.append("✓ Explicitly states no deletion occurs and contains no deletion commands")
        elif not has_deletion_commands:
            score += 10
            notes.append("~ No deletion commands found (good)")
        else:
            notes.append("✗ Contains actual deletion commands!")
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _check_ranking_system(self, content_lower: str) -> Dict[str, Any]:
        """Check for ranking/scoring system"""
        score = 0
        notes = []
        details = {}
        
        ranking_indicators = ['score', 'rank', 'rating', 'priority', 'safety']
        found_ranking = [indicator for indicator in ranking_indicators if indicator in content_lower]
        details['ranking_indicators_found'] = found_ranking
        
        if found_ranking:
            score += 15
            notes.append("✓ Implements ranking/scoring system")
            details['has_ranking_system'] = True
        else:
            notes.append("✗ No clear ranking system found")
            details['has_ranking_system'] = False
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _check_required_fields(self, content_lower: str) -> Dict[str, Any]:
        """Check for all required output fields"""
        score = 0
        notes = []
        details = {}
        
        required_fields = {
            'safety-score': ['safety', 'score', 'rating'],
            'parameters': ['parameter', 'factor', 'reason', 'criteria'],
            'file name': ['name', 'filename', 'fullname'],
            'size': ['size', 'length', 'kb', 'mb', 'byte'],
            'date created': ['creation', 'created', 'creationtime'],
            'date updated': ['lastwrite', 'modified', 'updated', 'lastmodified']
        }
        
        fields_found = []
        for field_name, keywords in required_fields.items():
            if any(keyword in content_lower for keyword in keywords):
                fields_found.append(field_name)
                score += 5
                notes.append(f"✓ Includes {field_name}")
            else:
                notes.append(f"✗ Missing {field_name}")
        
        details['required_fields_found'] = fields_found
        details['required_fields_count'] = len(fields_found)
        
        return {'score': score, 'notes': notes, 'details': details}
    
    def _check_bonus_features(self, content_lower: str) -> Dict[str, Any]:
        """Check for bonus features beyond requirements"""
        score = 0
        notes = []
        details = {}
        
        bonus_features = {
            'export_options': ['csv', 'json', 'xml', 'export'],
            'configurable_params': ['param(', 'parameter('],
            'help_documentation': ['.synopsis', '.description', '.example'],
            'error_handling': ['try', 'catch', 'erroraction'],
            'progress_indication': ['write-progress', 'write-host', 'verbose']
        }
        
        bonus_found = []
        for feature, keywords in bonus_features.items():
            if any(keyword in content_lower for keyword in keywords):
                bonus_found.append(feature)
                score += 2
                if score <= 10:  # Max 10 bonus points
                    notes.append(f"+ Bonus: {feature.replace('_', ' ')}")
        
        details['bonus_features_found'] = bonus_found
        details['bonus_score'] = min(score, 10)
        
        return {'score': min(score, 10), 'notes': notes, 'details': details}
