#!/usr/bin/env python3
"""
Requirements Traceability Matrix Analyzer

This module provides detailed traceability mapping between the original prompt requirements
and each LLM solution's implementation, creating a comprehensive matrix view.
"""

import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from analysis.base import BaseAnalyzer, AnalysisScore, FileInfo

@dataclass
class RequirementTrace:
    """Represents the traceability of a single requirement"""
    requirement_id: str
    requirement_text: str
    implemented: bool
    evidence: List[str]
    implementation_quality: int  # 0-100
    notes: List[str]

class RequirementsTraceabilityAnalyzer(BaseAnalyzer):
    """
    Analyzes requirements traceability matrix for each LLM solution
    
    SCORING METHODOLOGY:
    This analyzer uses a dual-layer approach:
    1. Binary Compliance: Does the solution meet the requirement? (Pass/Fail)
    2. Quality Assessment: How well does it meet the requirement? (0-100 score)
    
    Key Principles:
    - Requirements compliance ≠ implementation quality
    - Quality scores consider evidence count + implementation depth
    - Higher evidence count = stronger confidence in requirement fulfillment
    - Comprehensive implementations score higher than minimal ones
    
    Example: All LLMs might "pass" REQ-006 (parameter tracking), but:
    - Simple approach: 1 evidence, quality_score=94
    - Comprehensive approach: 4+ evidence, quality_score=100
    
    This explains why scores can be 98.9% vs 99.5% despite all requirements being met.
    """
    
    def __init__(self):
        super().__init__(
            name="Requirements Traceability Analysis",
            description="Maps original prompt requirements to implementation evidence with quality assessment",
            weight=0.25  # 25% weight - covers prompt adherence and compliance
        )
        
        # Define the detailed requirements from the prompt
        self.requirements = {
            "REQ-001": {
                "text": "Script must run on Windows platform",
                "type": "platform",
                "mandatory": True,
                "patterns": [r"\.ps1$", r"PowerShell", r"Windows", r"\.bat$", r"\.cmd$"],
                "evidence_patterns": [r"param\s*\(", r"\[CmdletBinding\(\)", r"\.ps1", r"PowerShell"]
            },
            "REQ-002": {
                "text": "Must identify files that are safe to delete",
                "type": "functionality",
                "mandatory": True,
                "patterns": [r"safe.*delete", r"identify.*files", r"candidate.*deletion", r"delete.*safe"],
                "evidence_patterns": [r"Get-ChildItem", r"files", r"identify", r"safe", r"delete"]
            },
            "REQ-003": {
                "text": "Must NOT actually delete files (identification only)",
                "type": "safety",
                "mandatory": True,
                "patterns": [r"not.*delete", r"does.*not.*delete", r"identify.*only", r"no.*deletion"],
                "evidence_patterns": [r"does not delete", r"no delete", r"identify only", r"NOT delete"],
                "anti_patterns": [r"Remove-Item", r"Delete\(", r"\.Delete\(\)", r"rm\s+-rf"]
            },
            "REQ-004": {
                "text": "Must provide ranking/scoring of safety level",
                "type": "functionality",
                "mandatory": True,
                "patterns": [r"ranking", r"safety.*score", r"score", r"rank", r"sort"],
                "evidence_patterns": [r"safety.*score", r"score", r"rank", r"sort", r"SafetyScore"]
            },
            "REQ-005": {
                "text": "Report must include safety-score field",
                "type": "output",
                "mandatory": True,
                "patterns": [r"safety.score", r"safety.*score", r"SafetyScore"],
                "evidence_patterns": [r"SafetyScore", r"safety.*score", r"score"]
            },
            "REQ-006": {
                "text": "Report must include parameters that went into score consideration",
                "type": "output",
                "mandatory": True,
                "patterns": [r"parameters", r"criteria", r"factors", r"consideration"],
                "evidence_patterns": [r"parameters", r"criteria", r"ScoreParameters", r"factors", r"reasons"]
            },
            "REQ-007": {
                "text": "Report must include file name",
                "type": "output",
                "mandatory": True,
                "patterns": [r"file.*name", r"filename", r"Name"],
                "evidence_patterns": [r"Name", r"FileName", r"\.Name", r"file.*name"]
            },
            "REQ-008": {
                "text": "Report must include file size",
                "type": "output",
                "mandatory": True,
                "patterns": [r"size", r"Size", r"Length"],
                "evidence_patterns": [r"Size", r"Length", r"\.Length", r"size"]
            },
            "REQ-009": {
                "text": "Report must include date created",
                "type": "output",
                "mandatory": True,
                "patterns": [r"date.*created", r"creation.*date", r"CreationTime"],
                "evidence_patterns": [r"CreationTime", r"Created", r"date.*created", r"creation"]
            },
            "REQ-010": {
                "text": "Report must include date updated/modified",
                "type": "output",
                "mandatory": True,
                "patterns": [r"date.*updated", r"date.*modified", r"LastWriteTime", r"modified"],
                "evidence_patterns": [r"LastWriteTime", r"Modified", r"date.*updated", r"last.*write"]
            }
        }
    
    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """Analyze requirements traceability for the given LLM solution"""
        
        # Combine all content for analysis
        all_content = ""
        code_content = ""
        doc_content = ""
        
        for file in files:
            all_content += file.content + "\n"
            if file.path.endswith('.ps1'):
                code_content += file.content + "\n"
            elif file.path.endswith('.md'):
                doc_content += file.content + "\n"
        
        # Analyze each requirement
        requirement_traces = []
        total_score = 0
        max_score = 0
        
        for req_id, req_info in self.requirements.items():
            trace = self._analyze_requirement(req_id, req_info, all_content, code_content, doc_content)
            requirement_traces.append(trace)
            
            # Calculate scoring
            if req_info["mandatory"]:
                max_score += 100
                if trace.implemented:
                    total_score += trace.implementation_quality
            else:
                max_score += 50  # Bonus requirements worth less
                if trace.implemented:
                    total_score += trace.implementation_quality * 0.5
        
        # Calculate final score
        final_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Generate summary notes
        notes = self._generate_summary_notes(requirement_traces)
        
        # Create detailed traceability matrix
        matrix = self._create_traceability_matrix(requirement_traces)
        
        details = {
            "requirements_total": len(self.requirements),
            "requirements_implemented": sum(1 for t in requirement_traces if t.implemented),
            "mandatory_requirements": sum(1 for req in self.requirements.values() if req["mandatory"]),
            "mandatory_implemented": sum(1 for t in requirement_traces 
                                       if t.implemented and self.requirements[t.requirement_id]["mandatory"]),
            "traceability_matrix": matrix,
            "requirement_traces": [
                {
                    "id": t.requirement_id,
                    "text": t.requirement_text,
                    "implemented": t.implemented,
                    "quality": t.implementation_quality,
                    "evidence_count": len(t.evidence)
                } for t in requirement_traces
            ]
        }
        
        return AnalysisScore(final_score, notes, details)
    
    def _search_pattern(self, content: str, pattern: str) -> List[str]:
        """Search for a pattern in content and return matches"""
        try:
            matches = re.findall(pattern, content, re.IGNORECASE)
            return matches[:5]  # Limit to first 5 matches for performance
        except re.error:
            # If regex fails, try simple string search
            if pattern.lower() in content.lower():
                return [pattern]
            return []
    
    def _analyze_requirement(self, req_id: str, req_info: Dict, all_content: str, 
                           code_content: str, doc_content: str) -> RequirementTrace:
        """Analyze a single requirement for implementation evidence"""
        
        evidence = []
        notes = []
        implemented = False
        quality_score = 0
        
        # Search for positive evidence
        evidence_found = 0
        for pattern in req_info.get("evidence_patterns", []):
            matches = self._search_pattern(all_content, pattern)
            if matches:
                evidence_found += len(matches)
                evidence.extend([f"Found '{pattern}': {matches[:3]}"])  # Limit examples
        
        # Check for anti-patterns (things that should NOT be present)
        anti_violations = 0
        if "anti_patterns" in req_info:
            for anti_pattern in req_info["anti_patterns"]:
                matches = self._search_pattern(code_content, anti_pattern)
                if matches:
                    anti_violations += len(matches)
                    evidence.append(f"⚠ Anti-pattern '{anti_pattern}': {matches[:2]}")
        
        # Determine implementation status and quality
        if req_id == "REQ-003":  # Special handling for "must NOT delete"
            if anti_violations == 0 and any("not delete" in content.lower() or "does not delete" in content.lower() 
                                           for content in [all_content]):
                implemented = True
                quality_score = 95  # High score for explicit safety statements
                notes.append("✓ Explicitly states no deletion occurs")
            elif anti_violations == 0:
                implemented = True
                quality_score = 80  # Good - no deletion commands found
                notes.append("✓ No deletion commands detected")
            else:
                implemented = False
                quality_score = 0
                notes.append(f"✗ Found {anti_violations} potential deletion commands")
        else:
            # Standard requirement analysis
            if evidence_found >= 2:
                implemented = True
                quality_score = min(90 + (evidence_found * 2), 100)
                notes.append(f"✓ Strong evidence found ({evidence_found} matches)")
            elif evidence_found >= 1:
                implemented = True
                quality_score = 70 + (evidence_found * 10)
                notes.append(f"✓ Evidence found ({evidence_found} matches)")
            else:
                implemented = False
                quality_score = 0
                notes.append("✗ No evidence found")
        
        # Bonus points for comprehensive implementation
        if implemented and evidence_found >= 3:
            quality_score = min(quality_score + 5, 100)
            notes.append("+ Comprehensive implementation")
        
        return RequirementTrace(
            requirement_id=req_id,
            requirement_text=req_info["text"],
            implemented=implemented,
            evidence=evidence,
            implementation_quality=quality_score,
            notes=notes
        )
    
    def _generate_summary_notes(self, traces: List[RequirementTrace]) -> List[str]:
        """Generate summary notes for the overall traceability analysis"""
        
        notes = []
        
        total_reqs = len(traces)
        implemented_reqs = sum(1 for t in traces if t.implemented)
        mandatory_reqs = sum(1 for t in traces if self.requirements[t.requirement_id]["mandatory"])
        mandatory_implemented = sum(1 for t in traces 
                                  if t.implemented and self.requirements[t.requirement_id]["mandatory"])
        
        # Overall compliance
        compliance_percent = (implemented_reqs / total_reqs) * 100
        mandatory_compliance = (mandatory_implemented / mandatory_reqs) * 100
        
        notes.append(f"Requirements Implementation: {implemented_reqs}/{total_reqs} ({compliance_percent:.1f}%)")
        notes.append(f"Mandatory Requirements: {mandatory_implemented}/{mandatory_reqs} ({mandatory_compliance:.1f}%)")
        
        # Identify any missing critical requirements
        missing_mandatory = []
        for trace in traces:
            if not trace.implemented and self.requirements[trace.requirement_id]["mandatory"]:
                missing_mandatory.append(trace.requirement_id)
        
        if missing_mandatory:
            notes.append(f"⚠ Missing mandatory requirements: {', '.join(missing_mandatory)}")
        else:
            notes.append("✓ All mandatory requirements implemented")
        
        # Quality assessment
        avg_quality = sum(t.implementation_quality for t in traces if t.implemented) / max(implemented_reqs, 1)
        if avg_quality >= 90:
            notes.append("✓ Excellent implementation quality")
        elif avg_quality >= 80:
            notes.append("✓ Good implementation quality")
        elif avg_quality >= 70:
            notes.append("⚠ Average implementation quality")
        else:
            notes.append("⚠ Implementation quality needs improvement")
        
        # Key insights about scoring methodology
        notes.append("")
        notes.append("📊 SCORING METHODOLOGY INSIGHTS:")
        notes.append("• Requirements compliance (binary pass/fail) ≠ implementation quality (0-100)")
        notes.append("• Quality scores based on evidence count + implementation depth")
        notes.append("• Higher evidence count = stronger confidence in requirement fulfillment")
        notes.append("• Even 'PASS' requirements can vary in quality (94-100% range observed)")
        notes.append("• Comprehensive implementations score higher than minimal implementations")
        notes.append("• Example: REQ-006 parameter tracking - detailed vs simple approaches affect scoring")
        
        return notes
    
    def _create_traceability_matrix(self, traces: List[RequirementTrace]) -> Dict[str, Any]:
        """Create a structured traceability matrix"""
        
        matrix = {
            "requirements": {},
            "summary": {
                "total_requirements": len(traces),
                "implemented": 0,
                "not_implemented": 0,
                "mandatory_met": 0,
                "optional_met": 0
            }
        }
        
        for trace in traces:
            req_info = self.requirements[trace.requirement_id]
            
            matrix["requirements"][trace.requirement_id] = {
                "text": trace.requirement_text,
                "type": req_info["type"],
                "mandatory": req_info["mandatory"],
                "implemented": trace.implemented,
                "quality_score": trace.implementation_quality,
                "evidence_count": len(trace.evidence),
                "status": "✓ PASS" if trace.implemented else "✗ FAIL"
            }
            
            # Update summary
            if trace.implemented:
                matrix["summary"]["implemented"] += 1
                if req_info["mandatory"]:
                    matrix["summary"]["mandatory_met"] += 1
                else:
                    matrix["summary"]["optional_met"] += 1
            else:
                matrix["summary"]["not_implemented"] += 1
        
        return matrix

def main():
    """Test the requirements traceability analyzer"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from modular_analyzer import ModularLLMAnalyzer
    
    workspace_path = r"d:\CodingModel\ModelCompare\FirstPassModelCompare"
    
    # Create analyzer and add traceability module
    analyzer = ModularLLMAnalyzer(workspace_path)
    traceability_analyzer = RequirementsTraceabilityAnalyzer()
    analyzer.registry.register(traceability_analyzer)
    
    print("🔍 Requirements Traceability Analysis")
    print("=" * 50)
    
    # Test on one LLM solution
    llm_path = "llm1"
    files = analyzer._gather_files(analyzer.workspace_path + "\\" + llm_path)
    result = traceability_analyzer.analyze(files, llm_path, analyzer.prompt_requirements)
    
    print(f"LLM1 Traceability Score: {result.score:.1f}/100")
    print()
    print("Requirements Matrix:")
    
    matrix = result.details["traceability_matrix"]
    for req_id, req_data in matrix["requirements"].items():
        status = "✓" if req_data["implemented"] else "✗"
        mandatory = "MANDATORY" if req_data["mandatory"] else "OPTIONAL"
        print(f"{status} {req_id} ({mandatory}): {req_data['text']}")
        print(f"   Quality: {req_data['quality_score']}/100, Evidence: {req_data['evidence_count']} items")
    
    print()
    print("Summary Notes:")
    for note in result.notes:
        print(f"  • {note}")

if __name__ == "__main__":
    main()
