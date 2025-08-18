#!/usr/bin/env python3
"""
Modular LLM Solution Analyzer

A plugin-based system for analyzing and comparing LLM-generated code solutions.
"""

import os
import json
import csv
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

# Import analysis modules
from analysis.base import FileInfo, AnalysisScore, AnalysisRegistry
from analysis.performance import PerformanceAnalyzer
from analysis.readability import ReadabilityAnalyzer
from analysis.code_quality import CodeQualityAnalyzer
from analysis.documentation import DocumentationAnalyzer
from analysis.requirements_traceability import RequirementsTraceabilityAnalyzer
from analysis.security import SecurityAnalyzer
from analysis.adaptability import AdaptabilityAnalyzer

@dataclass
class LLMAnalysisResult:
    """Complete analysis results for a single LLM solution"""
    llm_name: str
    files: List[FileInfo]
    analysis_scores: Dict[str, AnalysisScore]
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score"""
        if not self.analysis_scores:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Get weights from the analyzers - updated with Security and Adaptability Analyzers
        weights = {
            'Performance Analysis': 0.20,
            'Readability Analysis': 0.15,
            'Requirements Traceability Analysis': 0.25,
            'Code Quality Analysis': 0.10,
            'Documentation Analysis': 0.05,
            'Security Analysis': 0.15,
            'Adaptability Analysis': 0.10
        }
        
        for analyzer_name, score in self.analysis_scores.items():
            weight = weights.get(analyzer_name, 0.05)  # Default weight for new analyzers
            total_weighted_score += score.score * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    @property
    def total_lines(self) -> int:
        return sum(f.lines for f in self.files if f.path.endswith('.ps1'))
    
    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)

class ModularLLMAnalyzer:
    """Main analyzer class using modular analysis system"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.registry = AnalysisRegistry()
        self.prompt_requirements = self._parse_prompt_requirements()
        
        # Register default analyzers
        self._register_default_analyzers()
    
    def _register_default_analyzers(self):
        """Register the default set of analyzers"""
        self.registry.register(PerformanceAnalyzer())
        self.registry.register(ReadabilityAnalyzer())
        self.registry.register(CodeQualityAnalyzer())
        self.registry.register(DocumentationAnalyzer())
        self.registry.register(RequirementsTraceabilityAnalyzer())
        self.registry.register(SecurityAnalyzer())
        self.registry.register(AdaptabilityAnalyzer())
    
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
    
    def analyze_solution(self, llm_folder: str) -> LLMAnalysisResult:
        """Analyze a single LLM solution using all registered analyzers"""
        llm_path = os.path.join(self.workspace_path, llm_folder)
        
        # Gather files
        files = self._gather_files(llm_path)
        
        # Run all enabled analyzers
        analysis_scores = {}
        enabled_analyzers = self.registry.get_enabled_analyzers()
        
        for analyzer in enabled_analyzers:
            try:
                score = analyzer.analyze(files, llm_folder, self.prompt_requirements)
                analysis_scores[analyzer.name] = score
                print(f"  {analyzer.name}: {score.score:.1f}/100")
            except Exception as e:
                print(f"  Error in {analyzer.name}: {e}")
                analysis_scores[analyzer.name] = AnalysisScore(
                    score=0, 
                    notes=[f"Analysis failed: {str(e)}"]
                )
        
        return LLMAnalysisResult(
            llm_name=llm_folder,
            files=files,
            analysis_scores=analysis_scores
        )
    
    def analyze_all_solutions(self) -> List[LLMAnalysisResult]:
        """Analyze all LLM solutions"""
        results = []
        
        # Dynamically discover LLM folders instead of hardcoding
        potential_folders = ['llm1', 'llm2', 'llm3', 'llm4']
        existing_folders = []
        
        for folder in potential_folders:
            folder_path = os.path.join(self.workspace_path, folder)
            if os.path.exists(folder_path):
                existing_folders.append(folder)
        
        if not existing_folders:
            print("Warning: No LLM folders found. Expected folders: llm1, llm2, llm3, llm4")
            return results
        
        print(f"Found {len(existing_folders)} LLM solution(s): {', '.join(existing_folders)}")
        
        for folder in existing_folders:
            folder_path = os.path.join(self.workspace_path, folder)
            print(f"Analyzing {folder}...")
            result = self.analyze_solution(folder)
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[LLMAnalysisResult]) -> str:
        """Generate a comprehensive comparison report"""
        report = []
        report.append("# Modular LLM Solution Analysis Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall rankings
        report.append("## Overall Rankings")
        report.append("")
        sorted_results = sorted(results, key=lambda x: x.overall_score, reverse=True)
        
        report.append("| Rank | LLM | Overall Score | Files | Lines | Size (KB) |")
        report.append("|------|-----|---------------|-------|-------|-----------|")
        
        for i, result in enumerate(sorted_results, 1):
            size_kb = result.total_size / 1024
            report.append(f"| {i} | {result.llm_name} | {result.overall_score:.1f} | {len(result.files)} | {result.total_lines} | {size_kb:.1f} |")
        
        report.append("")
        
        # Analysis breakdown table
        report.append("## Detailed Score Breakdown")
        report.append("")
        
        # Get all analyzer names
        all_analyzers = set()
        for result in results:
            all_analyzers.update(result.analysis_scores.keys())
        
        analyzer_names = sorted(all_analyzers)
        
        # Create header
        header = "| LLM |"
        separator = "|-----|"
        for analyzer in analyzer_names:
            header += f" {analyzer.replace(' Analysis', '')} |"
            separator += "-------|"
        
        report.append(header)
        report.append(separator)
        
        # Add data rows
        for result in sorted_results:
            row = f"| {result.llm_name} |"
            for analyzer in analyzer_names:
                score = result.analysis_scores.get(analyzer, AnalysisScore(0))
                row += f" {score.score:.1f} |"
            report.append(row)
        
        report.append("")
        
        # Detailed analysis for each solution
        for result in sorted_results:
            report.append(f"## {result.llm_name} - Detailed Analysis")
            report.append("")
            report.append(f"**Overall Score: {result.overall_score:.1f}/100**")
            report.append("")
            
            report.append("### File Structure")
            for file in result.files:
                filename = os.path.basename(file.path)
                report.append(f"- {filename}: {file.lines} lines, {file.size:,} bytes")
            report.append("")
            
            for analyzer_name, score in result.analysis_scores.items():
                report.append(f"### {analyzer_name}")
                report.append(f"**Score: {score.score:.1f}/100**")
                report.append("")
                
                if score.notes:
                    for note in score.notes:
                        report.append(f"  {note}")
                    report.append("")
                
                if score.details:
                    # Add key details
                    important_details = ['has_error_handling', 'uses_generic_collections', 
                                       'comment_ratio', 'function_count', 'has_readme']
                    shown_details = {k: v for k, v in score.details.items() 
                                   if k in important_details or isinstance(v, (int, float, bool))}
                    
                    if shown_details:
                        report.append("  **Key Details:**")
                        for key, value in shown_details.items():
                            if isinstance(value, float):
                                report.append(f"  - {key}: {value:.3f}")
                            else:
                                report.append(f"  - {key}: {value}")
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
        category_winners = {}
        for analyzer_name in analyzer_names:
            best_in_category = max(results, key=lambda x: x.analysis_scores.get(analyzer_name, AnalysisScore(0)).score)
            category_winners[analyzer_name] = best_in_category
        
        report.append("### Category Winners")
        for analyzer_name, winner in category_winners.items():
            score = winner.analysis_scores.get(analyzer_name, AnalysisScore(0)).score
            report.append(f"- **{analyzer_name}:** {winner.llm_name} ({score:.1f})")
        
        report.append("")
        report.append("### Analysis Modules Used")
        for analyzer in self.registry.get_enabled_analyzers():
            report.append(f"- **{analyzer.name}** (Weight: {analyzer.weight:.0%}): {analyzer.description}")
        
        return '\n'.join(report)
    
    def export_csv_summary(self, results: List[LLMAnalysisResult], filename: str):
        """Export results summary to CSV"""
        if not results:
            return
        
        # Get all analyzer names
        all_analyzers = set()
        for result in results:
            all_analyzers.update(result.analysis_scores.keys())
        
        analyzer_names = sorted(all_analyzers)
        
        fieldnames = ['LLM', 'Overall_Score', 'Total_Lines', 'Total_Files', 'File_Size'] + \
                    [name.replace(' ', '_').replace('Analysis', '').strip('_') for name in analyzer_names]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in sorted(results, key=lambda x: x.overall_score, reverse=True):
                row = {
                    'LLM': result.llm_name,
                    'Overall_Score': round(result.overall_score, 1),
                    'Total_Lines': result.total_lines,
                    'Total_Files': len(result.files),
                    'File_Size': result.total_size
                }
                
                for analyzer_name in analyzer_names:
                    field_name = analyzer_name.replace(' ', '_').replace('Analysis', '').strip('_')
                    score = result.analysis_scores.get(analyzer_name, AnalysisScore(0))
                    row[field_name] = round(score.score, 1)
                
                writer.writerow(row)
    
    def export_detailed_json(self, results: List[LLMAnalysisResult], filename: str):
        """Export detailed results to JSON"""
        def convert_to_dict(obj):
            if hasattr(obj, '__dict__'):
                return {k: convert_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [convert_to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_to_dict(v) for k, v in obj.items()}
            else:
                return obj
        
        # Get the original prompt for display
        prompt_requirements = self._parse_prompt_requirements()
        original_prompt = prompt_requirements.get('prompt_text', 'Prompt not available')
        
        data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'workspace_path': self.workspace_path,
            'original_prompt': original_prompt,
            'analyzers_used': [analyzer.get_info() for analyzer in self.registry.get_enabled_analyzers()],
            'results': convert_to_dict(results)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Main function to run the modular analysis and update dashboard"""
    workspace_path = r"d:\CodingModel\ModelCompare\FirstPassModelCompare"
    
    analyzer = ModularLLMAnalyzer(workspace_path)
    
    print("🤖 Running LLM Analysis...")
    print("Enabled Analyzers:")
    for info in analyzer.registry.list_analyzers():
        if info['enabled']:
            print(f"  ✓ {info['name']} (Weight: {info['weight']:.0%})")
    print()
    
    # Run analysis
    results = analyzer.analyze_all_solutions()
    
    # Generate all outputs
    report = analyzer.generate_report(results)
    
    # Save files with consistent naming
    report_path = os.path.join(workspace_path, 'analysis_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    csv_path = os.path.join(workspace_path, 'analysis_summary.csv')
    analyzer.export_csv_summary(results, csv_path)
    
    json_path = os.path.join(workspace_path, 'analysis_detailed.json')
    analyzer.export_detailed_json(results, json_path)
    
    # Generate updated dashboard
    from dashboard_generator import DashboardGenerator
    dashboard_generator = DashboardGenerator()
    dashboard_path = os.path.join(workspace_path, 'analysis_dashboard.html')
    
    # Convert results to dashboard format
    dashboard_data = {
        "analysis_timestamp": datetime.now().isoformat(),
        "analyzers_used": [
            {"name": info['name'], "weight": info['weight']} 
            for info in analyzer.registry.list_analyzers() 
            if info['enabled']
        ],
        "results": [
            {
                "llm_name": r.llm_name,
                "overall_score": r.overall_score,
                "files": [{"path": f.path, "lines": f.lines, "size": f.size} for f in r.files],
                "analysis_scores": {name: {"score": score.score, "notes": score.notes} 
                                 for name, score in r.analysis_scores.items()}
            } for r in results
        ]
    }
    
    dashboard_generator.generate_dashboard(dashboard_data, dashboard_path)
    
    # Print results summary
    print("✅ Analysis Complete!")
    print("="*50)
    
    sorted_results = sorted(results, key=lambda x: x.overall_score, reverse=True)
    for i, result in enumerate(sorted_results, 1):
        print(f"{i}. {result.llm_name}: {result.overall_score:.1f}/100")
    
    print(f"\n📄 Files generated:")
    print(f"  • {os.path.basename(dashboard_path)} - Interactive dashboard")
    print(f"  • {os.path.basename(report_path)} - Detailed report")
    print(f"  • {os.path.basename(csv_path)} - CSV summary")
    print(f"  • {os.path.basename(json_path)} - JSON data")
    
    # Try to open dashboard
    try:
        import webbrowser
        abs_path = os.path.abspath(dashboard_path)
        url = f"file:///{abs_path.replace(os.sep, '/')}"
        webbrowser.open(url)
        print(f"\n🌐 Dashboard opened in browser!")
    except Exception:
        print(f"\n📍 Open dashboard manually: {dashboard_path}")

if __name__ == "__main__":
    main()
