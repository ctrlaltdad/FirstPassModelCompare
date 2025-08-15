#!/usr/bin/env python3
"""
Dashboard Generator for LLM Analysis Results

Generates interactive HTML dashboards from analysis results (both monolithic and modular formats).
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Union

class DashboardGenerator:
    """Generates interactive HTML dashboards from analysis results"""
    
    def __init__(self):
        self.chart_colors = [
            'rgba(255, 99, 132, 0.8)',   # Red
            'rgba(54, 162, 235, 0.8)',   # Blue
            'rgba(255, 205, 86, 0.8)',   # Yellow
            'rgba(75, 192, 192, 0.8)',   # Teal
            'rgba(153, 102, 255, 0.8)',  # Purple
            'rgba(255, 159, 64, 0.8)',   # Orange
        ]
        
        self.border_colors = [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 205, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
        ]
    
    def _calculate_overall_scores(self, data: Dict[str, Any]) -> List[float]:
        """Calculate overall scores for each LLM based on analysis scores and weights"""
        
        results = data.get('results', [])
        analyzers_used = data.get('analyzers_used', [])
        
        # Create a mapping of analyzer names to weights
        analyzer_weights = {}
        for analyzer in analyzers_used:
            analyzer_weights[analyzer['name']] = analyzer['weight']
        
        overall_scores = []
        
        for result in results:
            analysis_scores = result.get('analysis_scores', {})
            weighted_sum = 0.0
            total_weight = 0.0
            
            for analyzer_name, score_data in analysis_scores.items():
                if analyzer_name in analyzer_weights:
                    score = score_data.get('score', 0)
                    weight = analyzer_weights[analyzer_name]
                    weighted_sum += score * weight
                    total_weight += weight
            
            # Calculate weighted average
            overall_score = weighted_sum / total_weight if total_weight > 0 else 0
            overall_scores.append(overall_score)
        
        return overall_scores
    
    def load_analysis_data(self, source_path: str) -> Dict[str, Any]:
        """Load analysis data from JSON file or extract from analyzer results"""
        
        # Try to load modular JSON first
        if os.path.isdir(source_path):
            modular_json = os.path.join(source_path, 'modular_analysis_detailed.json')
        else:
            modular_json = os.path.join(os.path.dirname(source_path), 'modular_analysis_detailed.json')
            
        if os.path.exists(modular_json):
            with open(modular_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Fallback to extracting from results if available
        return self._extract_from_results(source_path)
    
    def _extract_from_results(self, source_path: str) -> Dict[str, Any]:
        """Extract data from existing analysis results for compatibility"""
        # This would be implemented to parse markdown/csv if needed
        # For now, return a basic structure
        return {
            'analysis_timestamp': datetime.now().isoformat(),
            'results': [],
            'analyzers_used': []
        }
    
    def generate_dashboard(self, data: Dict[str, Any], output_path: str):
        """Generate the interactive HTML dashboard"""
        
        results = data.get('results', [])
        if not results:
            print("No analysis results found")
            return
        
        # Extract data for charts
        llm_names = [result['llm_name'] for result in results]
        
        # Calculate overall scores using analyzer weights
        overall_scores = self._calculate_overall_scores(data)
        
        # Get all analyzer categories
        analyzer_categories = set()
        for result in results:
            analyzer_categories.update(result.get('analysis_scores', {}).keys())
        
        analyzer_categories = sorted(analyzer_categories)
        
        # Prepare data for category comparison chart (radar chart)
        # For radar chart: each dataset = one LLM, data points = scores for each category
        llm_datasets = []
        for i, result in enumerate(results):
            scores_for_categories = []
            for category in analyzer_categories:
                score_data = result.get('analysis_scores', {}).get(category, {})
                if isinstance(score_data, dict):
                    scores_for_categories.append(score_data.get('score', 0))
                else:
                    scores_for_categories.append(0)
            
            color_idx = i % len(self.chart_colors)
            llm_datasets.append({
                'label': result['llm_name'],
                'data': scores_for_categories,
                'backgroundColor': self.chart_colors[color_idx],
                'borderColor': self.border_colors[color_idx],
                'borderWidth': 2,
                'fill': True,
                'pointRadius': 4
            })
        
        # Generate the HTML
        html_content = self._generate_html_template(
            llm_names=llm_names,
            overall_scores=overall_scores,
            llm_datasets=llm_datasets,
            analyzer_categories=analyzer_categories,
            results=results,
            timestamp=data.get('analysis_timestamp', datetime.now().isoformat())
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Dashboard generated: {output_path}")
    
    def _generate_html_template(self, llm_names: List[str], overall_scores: List[float], 
                              llm_datasets: List[Dict], analyzer_categories: List[str],
                              results: List[Dict], timestamp: str) -> str:
        """Generate the complete HTML template"""
        
        # Generate detailed results table
        results_table = self._generate_results_table(results, analyzer_categories, overall_scores)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Solution Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .chart-container h3 {{
            margin-top: 0;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}
        
        .results-section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-top: 20px;
        }}
        
        .results-section h3 {{
            margin-top: 0;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        th {{
            background-color: #f7fafc;
            font-weight: 600;
            color: #4a5568;
        }}
        
        tr:hover {{
            background-color: #f7fafc;
        }}
        
        .score {{
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
        }}
        
        .score.excellent {{ background-color: #48bb78; }}
        .score.good {{ background-color: #38b2ac; }}
        .score.average {{ background-color: #ed8936; }}
        .score.poor {{ background-color: #e53e3e; }}
        
        .llm-rank {{
            font-size: 1.2em;
            font-weight: bold;
            color: #4a5568;
        }}
        
        .details-toggle {{
            background: #4299e1;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        
        .details-toggle:hover {{
            background: #3182ce;
        }}
        
        .details-content {{
            display: none;
            margin-top: 10px;
            padding: 15px;
            background-color: #f7fafc;
            border-radius: 5px;
            border-left: 4px solid #4299e1;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .metric-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #4299e1;
        }}
        
        .metric-label {{
            color: #718096;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 LLM Solution Analysis Dashboard</h1>
        <p>Comprehensive comparison of AI-generated code solutions</p>
        <p><small>Generated on: {timestamp}</small></p>
    </div>
    
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-value">{len(llm_names)}</div>
            <div class="metric-label">Solutions Analyzed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(analyzer_categories)}</div>
            <div class="metric-label">Analysis Dimensions</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{max(overall_scores):.1f}</div>
            <div class="metric-label">Highest Score</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{sum(overall_scores)/len(overall_scores):.1f}</div>
            <div class="metric-label">Average Score</div>
        </div>
    </div>
    
    <div class="dashboard-grid">
        <div class="chart-container">
            <h3>📊 Overall Performance Ranking</h3>
            <canvas id="overallChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>📈 Category Performance Comparison</h3>
            <canvas id="categoryChart"></canvas>
        </div>
    </div>
    
    <div class="results-section">
        <h3>📋 Detailed Results</h3>
        {results_table}
    </div>
    
    <script>
        // Overall Performance Chart
        const overallCtx = document.getElementById('overallChart').getContext('2d');
        new Chart(overallCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(llm_names)},
                datasets: [{{
                    label: 'Overall Score',
                    data: {json.dumps(overall_scores)},
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.parsed.y.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Category Comparison Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps([cat.replace(' Analysis', '') for cat in analyzer_categories])},
                datasets: {json.dumps(llm_datasets)}
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.r.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Toggle details functionality
        function toggleDetails(id) {{
            const content = document.getElementById(id);
            const isVisible = content.style.display === 'block';
            content.style.display = isVisible ? 'none' : 'block';
        }}
    </script>
</body>
</html>"""
    
    def _generate_results_table(self, results: List[Dict], analyzer_categories: List[str], overall_scores: List[float]) -> str:
        """Generate the detailed results table HTML"""
        
        # Combine results with their calculated overall scores
        results_with_scores = []
        for i, result in enumerate(results):
            result_copy = result.copy()
            result_copy['overall_score'] = overall_scores[i] if i < len(overall_scores) else 0
            results_with_scores.append(result_copy)
        
        # Sort results by overall score
        sorted_results = sorted(results_with_scores, key=lambda x: x.get('overall_score', 0), reverse=True)
        
        rows = []
        for i, result in enumerate(sorted_results, 1):
            llm_name = result['llm_name']
            overall_score = result.get('overall_score', 0)
            
            # Determine score class
            if overall_score >= 90:
                score_class = 'excellent'
            elif overall_score >= 80:
                score_class = 'good'
            elif overall_score >= 70:
                score_class = 'average'
            else:
                score_class = 'poor'
            
            # Build category scores
            category_scores = []
            for category in analyzer_categories:
                score_data = result.get('analysis_scores', {}).get(category, {})
                if isinstance(score_data, dict):
                    score = score_data.get('score', 0)
                else:
                    score = 0
                category_scores.append(f"{score:.1f}")
            
            category_cells = "".join([f"<td>{score}</td>" for score in category_scores])
            
            # Generate details content
            details_id = f"details-{llm_name}"
            details_content = self._generate_details_content(result, analyzer_categories)
            
            rows.append(f"""
                <tr>
                    <td class="llm-rank">#{i}</td>
                    <td><strong>{llm_name}</strong></td>
                    <td><span class="score {score_class}">{overall_score:.1f}</span></td>
                    {category_cells}
                    <td>
                        <button class="details-toggle" onclick="toggleDetails('{details_id}')">
                            View Details
                        </button>
                    </td>
                </tr>
                <tr>
                    <td colspan="{len(analyzer_categories) + 4}">
                        <div id="{details_id}" class="details-content">
                            {details_content}
                        </div>
                    </td>
                </tr>
            """)
        
        # Build header
        category_headers = "".join([f"<th>{cat.replace(' Analysis', '')}</th>" for cat in analyzer_categories])
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>LLM</th>
                    <th>Overall</th>
                    {category_headers}
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
        """
    
    def _generate_details_content(self, result: Dict, analyzer_categories: List[str]) -> str:
        """Generate detailed content for each LLM result"""
        
        details = []
        
        # File structure
        files = result.get('files', [])
        if files:
            details.append("<h4>📁 File Structure</h4>")
            details.append("<ul>")
            for file_info in files:
                filename = os.path.basename(file_info.get('path', 'unknown'))
                lines = file_info.get('lines', 0)
                size = file_info.get('size', 0)
                details.append(f"<li><strong>{filename}</strong>: {lines} lines, {size:,} bytes</li>")
            details.append("</ul>")
        
        # Analysis details
        analysis_scores = result.get('analysis_scores', {})
        for category in analyzer_categories:
            score_data = analysis_scores.get(category, {})
            if isinstance(score_data, dict):
                details.append(f"<h4>🔍 {category}</h4>")
                details.append(f"<p><strong>Score:</strong> {score_data.get('score', 0):.1f}/100</p>")
                
                # Add notes
                notes = score_data.get('notes', [])
                
                # Special handling for Requirements Traceability Analysis
                if category == "Requirements Traceability Analysis":
                    # For Requirements Traceability, the summary notes are in max_score
                    max_score_data = score_data.get('max_score', [])
                    if isinstance(max_score_data, list):
                        notes = max_score_data
                
                if notes and isinstance(notes, list):
                    details.append("<p><strong>Key Points:</strong></p>")
                    details.append("<ul>")
                    # Show more notes for Requirements Traceability to include methodology insights
                    max_notes = 15 if category == "Requirements Traceability Analysis" else 5
                    for note in notes[:max_notes]:
                        if note.strip():  # Skip empty strings
                            details.append(f"<li>{note}</li>")
                    details.append("</ul>")
        
        return "".join(details)

def main():
    """Main function to generate dashboard from latest analysis"""
    workspace_path = r"d:\CodingModel\ModelCompare\FirstPassModelCompare"
    
    generator = DashboardGenerator()
    
    # Load data from analysis_detailed.json (the correct file)
    json_path = os.path.join(workspace_path, 'analysis_detailed.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("No analysis results found")
        data = generator.load_analysis_data(workspace_path)
    
    # Generate dashboard with the correct filename
    dashboard_path = os.path.join(workspace_path, 'analysis_dashboard.html')
    generator.generate_dashboard(data, dashboard_path)
    
    print(f"Interactive dashboard generated: {dashboard_path}")

if __name__ == "__main__":
    main()
