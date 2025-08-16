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
    
    def _generate_weight_controls(self, analyzer_categories: List[str], results: List[Dict]) -> str:
        """Generate HTML for weight controls"""
        
        # Default weights - extract from the first result if available
        default_weights = {
            'Adaptability Analysis': 10,
            'Code Quality Analysis': 10,
            'Documentation Analysis': 5,
            'Performance Analysis': 20,
            'Readability Analysis': 15,
            'Requirements Traceability Analysis': 25,
            'Security Analysis': 15
        }
        
        controls = []
        
        for category in analyzer_categories:
            # Get icon for category
            icon = self._get_category_icon(category)
            # Get default weight
            weight = default_weights.get(category, 10)
            # Create clean ID for the category
            category_id = category.lower().replace(' ', '_').replace('_analysis', '')
            
            controls.append(f'''
            <div class="weight-item">
                <div class="weight-label">
                    <span>{icon} {category.replace(' Analysis', '')}</span>
                    <span class="weight-value" id="{category_id}_value">{weight}%</span>
                </div>
                <input type="range" min="0" max="50" value="{weight}" 
                       class="weight-slider" id="{category_id}_slider"
                       oninput="updateWeight('{category_id}', '{category}', this.value)">
            </div>
            ''')
        
        return ''.join(controls)
    
    def _generate_initial_weights_js(self, analyzer_categories: List[str]) -> str:
        """Generate JavaScript object for initial weights"""
        default_weights = {
            'Adaptability Analysis': 10,
            'Code Quality Analysis': 10,
            'Documentation Analysis': 5,
            'Performance Analysis': 20,
            'Readability Analysis': 15,
            'Requirements Traceability Analysis': 25,
            'Security Analysis': 15
        }
        
        weights_js = []
        for category in analyzer_categories:
            weight = default_weights.get(category, 10)
            weights_js.append(f'"{category}": {weight}')
        
        return ',\n            '.join(weights_js)
    
    def _generate_html_template(self, llm_names: List[str], overall_scores: List[float], 
                              llm_datasets: List[Dict], analyzer_categories: List[str],
                              results: List[Dict], timestamp: str) -> str:
        """Generate the complete HTML template"""
        
        # Generate detailed results table
        results_table = self._generate_results_table(results, analyzer_categories, overall_scores)
        
        # Generate weight controls
        weight_controls_html = self._generate_weight_controls(analyzer_categories, results)
        
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
            padding: 20px;
            background-color: #f7fafc;
            border-radius: 8px;
            border-left: 4px solid #4299e1;
        }}
        
        .analysis-section {{
            background: white;
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .analysis-section h4 {{
            margin: 0 0 12px 0;
            color: #2d3748;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            font-size: 1.1em;
        }}
        
        .score-display {{
            background: #4299e1;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 10px;
        }}
        
        .key-points {{
            margin: 0;
            padding: 0;
        }}
        
        .key-points li {{
            margin: 6px 0;
            padding: 4px 8px;
            border-radius: 4px;
            list-style: none;
            position: relative;
            padding-left: 25px;
        }}
        
        .key-points li.positive {{
            background-color: #f0fff4;
            border-left: 3px solid #38a169;
        }}
        
        .key-points li.negative {{
            background-color: #fffaf0;
            border-left: 3px solid #ed8936;
        }}
        
        .key-points li.warning {{
            background-color: #fef5e7;
            border-left: 3px solid #f6ad55;
        }}
        
        .key-points li.info {{
            background-color: #ebf8ff;
            border-left: 3px solid #4299e1;
        }}
        
        .key-points li.success {{
            background-color: #f0fff4;
            border-left: 3px solid #48bb78;
        }}
        
        .key-points li.error {{
            background-color: #fed7d7;
            border-left: 3px solid #e53e3e;
        }}
        
        .file-structure {{
            background: #f7fafc;
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }}
        
        .file-structure ul {{
            margin: 0;
            padding-left: 20px;
        }}
        
        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
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
        
        .weight-controls {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        
        .weight-controls h3 {{
            margin-top: 0;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}
        
        .weight-controls-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
        }}
        
        .weight-controls-header:hover {{
            color: #2d3748;
        }}
        
        .collapse-toggle {{
            background: none;
            border: none;
            font-size: 1.2em;
            cursor: pointer;
            color: #4299e1;
            transition: transform 0.3s ease;
            padding: 0;
            margin: 0;
        }}
        
        .collapse-toggle.collapsed {{
            transform: rotate(-90deg);
        }}
        
        .weight-controls-content {{
            overflow: hidden;
            transition: max-height 0.3s ease, opacity 0.3s ease;
            max-height: 0;
            opacity: 0;
        }}
        
        .weight-controls-content.expanded {{
            max-height: 1000px;
            opacity: 1;
        }}
        
        .advanced-badge {{
            background: #4299e1;
            color: white;
            font-size: 0.75em;
            padding: 2px 8px;
            border-radius: 12px;
            margin-left: 8px;
            font-weight: 500;
        }}
        
        .weight-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}
        
        .weight-item {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .weight-label {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            color: #2d3748;
        }}
        
        .weight-value {{
            background: #4299e1;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            min-width: 45px;
            text-align: center;
        }}
        
        .weight-slider {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #e2e8f0;
            outline: none;
            -webkit-appearance: none;
        }}
        
        .weight-slider::-webkit-slider-thumb {{
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #4299e1;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .weight-slider::-moz-range-thumb {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #4299e1;
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .weight-total {{
            text-align: center;
            margin-top: 15px;
            padding: 10px;
            background: #f7fafc;
            border-radius: 8px;
            font-weight: 600;
        }}
        
        .weight-warning {{
            color: #e53e3e;
        }}
        
        .weight-good {{
            color: #38a169;
        }}
        
        .weight-item.changing {{
            background-color: #bee3f8;
            transform: scale(1.02);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .redistribution-info {{
            animation: slideIn 0.3s ease-out;
        }}
        
        @keyframes slideIn {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        
        .weight-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        
        .modal-content {{
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            position: relative;
        }}
        
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 15px;
        }}
        
        .modal-title {{
            font-size: 1.5em;
            font-weight: 600;
            color: #2d3748;
        }}
        
        .close-modal {{
            background: none;
            border: none;
            font-size: 2em;
            color: #718096;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .close-modal:hover {{
            color: #2d3748;
        }}
        
        .modal-section {{
            margin-bottom: 20px;
        }}
        
        .modal-section h4 {{
            color: #4a5568;
            margin-bottom: 10px;
        }}
        
        .preset-buttons {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        
        .preset-btn {{
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .preset-btn:hover {{
            background: #edf2f7;
            border-color: #4299e1;
        }}
        
        .preset-btn.active {{
            background: #e6fffa;
            border-color: #38a169;
            color: #234e52;
        }}
        
        .weight-help {{
            background: #ebf8ff;
            border-left: 4px solid #4299e1;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }}
        
        .redistribution-info {{
            background: #fffaf0;
            border-left: 4px solid #ed8936;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .weight-item.changing {{
            background: #fef5e7;
            border-radius: 8px;
            padding: 8px;
            transition: background-color 0.3s;
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
    
    <div class="weight-controls">
        <div class="weight-controls-header" onclick="toggleWeightControls()">
            <h3 style="margin: 0; border: none; padding: 0;">
                ⚖️ Analysis Weight Controls
                <span class="advanced-badge">Advanced</span>
            </h3>
            <button class="collapse-toggle collapsed" id="weight-toggle">▼</button>
        </div>
        
        <div class="weight-controls-content" id="weight-controls-content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; margin-top: 15px;">
                <p style="color: #718096; margin: 0;">Adjust the importance of each analysis dimension - weights automatically balance to 100%</p>
                <button onclick="openWeightModal()" style="background: #4299e1; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-size: 0.9em;">
                    💡 Weight Guide
                </button>
            </div>
        
        <div class="weight-grid">
            {weight_controls_html}
        </div>
        
        <div class="weight-total">
            Total Weight: <span id="totalWeight">100</span>%
            <span id="weightStatus" class="weight-good">✓ Balanced</span>
        </div>
        </div> <!-- Close weight-controls-content -->
    </div>
    
    <!-- Weight Guide Modal -->
    <div id="weightModal" class="weight-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">⚖️ Weight Distribution Guide</h3>
                <button class="close-modal" onclick="closeWeightModal()">&times;</button>
            </div>
            
            <div class="modal-section">
                <div class="weight-help">
                    <strong>🎯 How It Works:</strong><br>
                    When you adjust any weight, the system automatically redistributes the remaining weights proportionally to maintain 100% total.
                    This ensures fair comparison while respecting your priorities.
                </div>
            </div>
            
            <div class="modal-section">
                <h4>📋 Quick Presets</h4>
                <div class="preset-buttons">
                    <div class="preset-btn" onclick="applyPreset('balanced')">
                        <strong>🏛️ Balanced</strong><br>
                        <small>Equal focus on all dimensions</small>
                    </div>
                    <div class="preset-btn" onclick="applyPreset('security')">
                        <strong>🔒 Security First</strong><br>
                        <small>Prioritize security & compliance</small>
                    </div>
                    <div class="preset-btn" onclick="applyPreset('performance')">
                        <strong>⚡ Performance</strong><br>
                        <small>Speed & efficiency focused</small>
                    </div>
                    <div class="preset-btn" onclick="applyPreset('enterprise')">
                        <strong>🏢 Enterprise</strong><br>
                        <small>Documentation & requirements</small>
                    </div>
                    <div class="preset-btn" onclick="applyPreset('agile')">
                        <strong>🚀 Agile Development</strong><br>
                        <small>Adaptability & code quality</small>
                    </div>
                    <div class="preset-btn" onclick="applyPreset('maintenance')">
                        <strong>🔧 Maintenance</strong><br>
                        <small>Readability & documentation</small>
                    </div>
                </div>
            </div>
            
            <div class="modal-section">
                <h4>💡 Tips</h4>
                <ul style="color: #4a5568; line-height: 1.6;">
                    <li><strong>Start with presets</strong> then fine-tune for your specific needs</li>
                    <li><strong>Watch the rankings change</strong> as you adjust weights</li>
                    <li><strong>Higher weights</strong> make that dimension more influential in the final score</li>
                    <li><strong>Zero weight</strong> excludes that dimension from scoring entirely</li>
                </ul>
            </div>
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
        // Weight management with smart redistribution
        let currentWeights = {{
            {self._generate_initial_weights_js(analyzer_categories)}
        }};
        
        let originalScores = {json.dumps(results)};
        let chartInstances = {{}};
        let isUpdating = false; // Prevent recursive updates
        
        function updateWeight(categoryId, categoryName, value) {{
            if (isUpdating) return;
            
            const newValue = parseInt(value);
            const oldValue = currentWeights[categoryName];
            const difference = newValue - oldValue;
            
            // Update the current weight
            currentWeights[categoryName] = newValue;
            
            // Smart redistribution of remaining weights
            redistributeWeights(categoryName, difference);
            
            // Update UI
            updateAllWeightDisplays();
            
            // Add visual feedback
            highlightChangingWeight(categoryId);
            
            // Recalculate scores
            recalculateScores();
        }}
        
        function redistributeWeights(changedCategory, difference) {{
            const otherCategories = Object.keys(currentWeights).filter(cat => cat !== changedCategory);
            const totalOtherWeights = otherCategories.reduce((sum, cat) => sum + currentWeights[cat], 0);
            
            if (totalOtherWeights === 0) {{
                // If all other weights are 0, distribute evenly
                const remainingWeight = 100 - currentWeights[changedCategory];
                const weightPerCategory = Math.floor(remainingWeight / otherCategories.length);
                let remainder = remainingWeight % otherCategories.length;
                
                otherCategories.forEach((cat, index) => {{
                    currentWeights[cat] = weightPerCategory + (index < remainder ? 1 : 0);
                }});
            }} else {{
                // Proportional redistribution
                const targetTotal = 100 - currentWeights[changedCategory];
                const scaleFactor = targetTotal / totalOtherWeights;
                
                otherCategories.forEach(cat => {{
                    currentWeights[cat] = Math.round(currentWeights[cat] * scaleFactor);
                }});
                
                // Ensure exactly 100% total
                ensureExact100Percent();
            }}
        }}
        
        function ensureExact100Percent() {{
            const total = Object.values(currentWeights).reduce((sum, weight) => sum + weight, 0);
            const difference = 100 - total;
            
            if (difference !== 0) {{
                // Find the category with the highest weight to adjust
                const sortedCategories = Object.keys(currentWeights)
                    .sort((a, b) => currentWeights[b] - currentWeights[a]);
                
                currentWeights[sortedCategories[0]] += difference;
            }}
        }}
        
        function updateAllWeightDisplays() {{
            isUpdating = true;
            
            Object.keys(currentWeights).forEach(category => {{
                const categoryId = category.toLowerCase().replace(' ', '_').replace('_analysis', '');
                const slider = document.getElementById(categoryId + '_slider');
                const valueDisplay = document.getElementById(categoryId + '_value');
                
                if (slider && valueDisplay) {{
                    slider.value = currentWeights[category];
                    valueDisplay.textContent = currentWeights[category] + '%';
                }}
            }});
            
            // Update total weight display (should always be 100)
            const totalElement = document.getElementById('totalWeight');
            const statusElement = document.getElementById('weightStatus');
            
            totalElement.textContent = '100';
            statusElement.textContent = '✓ Balanced';
            statusElement.className = 'weight-good';
            
            isUpdating = false;
        }}
        
        function highlightChangingWeight(categoryId) {{
            const weightItem = document.getElementById(categoryId + '_slider').closest('.weight-item');
            if (weightItem) {{
                weightItem.classList.add('changing');
                setTimeout(() => {{
                    weightItem.classList.remove('changing');
                }}, 300);
            }}
        }}
        
        // Modal functions
        function openWeightModal() {{
            document.getElementById('weightModal').style.display = 'block';
        }}
        
        function closeWeightModal() {{
            document.getElementById('weightModal').style.display = 'none';
        }}
        
        // Preset weight configurations
        const presets = {{
            balanced: {{
                'Adaptability Analysis': 14,
                'Code Quality Analysis': 14,
                'Documentation Analysis': 14,
                'Performance Analysis': 15,
                'Readability Analysis': 14,
                'Requirements Traceability Analysis': 15,
                'Security Analysis': 14
            }},
            security: {{
                'Adaptability Analysis': 5,
                'Code Quality Analysis': 15,
                'Documentation Analysis': 10,
                'Performance Analysis': 15,
                'Readability Analysis': 10,
                'Requirements Traceability Analysis': 20,
                'Security Analysis': 25
            }},
            performance: {{
                'Adaptability Analysis': 15,
                'Code Quality Analysis': 15,
                'Documentation Analysis': 5,
                'Performance Analysis': 30,
                'Readability Analysis': 10,
                'Requirements Traceability Analysis': 15,
                'Security Analysis': 10
            }},
            enterprise: {{
                'Adaptability Analysis': 8,
                'Code Quality Analysis': 12,
                'Documentation Analysis': 20,
                'Performance Analysis': 15,
                'Readability Analysis': 15,
                'Requirements Traceability Analysis': 25,
                'Security Analysis': 5
            }},
            agile: {{
                'Adaptability Analysis': 25,
                'Code Quality Analysis': 20,
                'Documentation Analysis': 5,
                'Performance Analysis': 20,
                'Readability Analysis': 15,
                'Requirements Traceability Analysis': 10,
                'Security Analysis': 5
            }},
            maintenance: {{
                'Adaptability Analysis': 10,
                'Code Quality Analysis': 15,
                'Documentation Analysis': 25,
                'Performance Analysis': 10,
                'Readability Analysis': 25,
                'Requirements Traceability Analysis': 10,
                'Security Analysis': 5
            }}
        }};
        
        function applyPreset(presetName) {{
            const preset = presets[presetName];
            if (preset) {{
                // Update weights
                Object.keys(preset).forEach(category => {{
                    if (currentWeights.hasOwnProperty(category)) {{
                        currentWeights[category] = preset[category];
                    }}
                }});
                
                // Update displays
                updateAllWeightDisplays();
                
                // Recalculate scores
                recalculateScores();
                
                // Visual feedback
                document.querySelectorAll('.preset-btn').forEach(btn => {{
                    btn.classList.remove('active');
                }});
                event.target.closest('.preset-btn').classList.add('active');
                
                // Show redistribution info
                showRedistributionInfo(`Applied ${{presetName}} preset`);
            }}
        }}
        
        function showRedistributionInfo(message) {{
            const info = document.createElement('div');
            info.className = 'redistribution-info';
            info.textContent = message;
            info.style.position = 'fixed';
            info.style.top = '20px';
            info.style.right = '20px';
            info.style.zIndex = '1001';
            info.style.padding = '15px';
            info.style.backgroundColor = '#38a169';
            info.style.color = 'white';
            info.style.borderRadius = '8px';
            info.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
            
            document.body.appendChild(info);
            
            setTimeout(() => {{
                info.style.opacity = '0';
                setTimeout(() => {{
                    if (info.parentNode) {{
                        info.parentNode.removeChild(info);
                    }}
                }}, 300);
            }}, 2000);
        }}
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('weightModal');
            if (event.target === modal) {{
                closeWeightModal();
            }}
        }}
        
        function recalculateScores() {{
            // Recalculate overall scores for each LLM
            const newOverallScores = [];
            const llmNames = {json.dumps(llm_names)};
            
            originalScores.forEach((result, index) => {{
                let weightedSum = 0;
                let totalWeight = 0;
                
                const analysisScores = result.analysis_scores || {{}};
                Object.keys(currentWeights).forEach(category => {{
                    const weight = currentWeights[category] / 100;
                    const score = analysisScores[category]?.score || 0;
                    weightedSum += score * weight;
                    totalWeight += weight;
                }});
                
                const overallScore = totalWeight > 0 ? weightedSum / totalWeight : 0;
                newOverallScores.push(overallScore);
                
                // Update the score display in the table
                const scoreElement = document.querySelector(`#score-${{result.llm_name}}`);
                if (scoreElement) {{
                    scoreElement.textContent = overallScore.toFixed(1);
                }}
            }});
            
            // Sort results by new scores and update rankings
            const sortedResults = originalScores.map((result, index) => ({{
                ...result,
                newScore: newOverallScores[index]
            }})).sort((a, b) => b.newScore - a.newScore);
            
            // Update table rankings
            updateTableRankings(sortedResults);
            
            // Update charts
            updateCharts(llmNames, newOverallScores);
        }}
        
        function updateTableRankings(sortedResults) {{
            // Update rank numbers in the table
            sortedResults.forEach((result, index) => {{
                const rankElement = document.querySelector(`#rank-${{result.llm_name}}`);
                if (rankElement) {{
                    rankElement.textContent = `#${{index + 1}}`;
                }}
            }});
        }}
        
        function updateCharts(llmNames, newScores) {{
            // Update overall performance chart
            if (chartInstances.overallChart) {{
                chartInstances.overallChart.data.datasets[0].data = newScores;
                chartInstances.overallChart.update();
            }}
            
            // Update category chart with new weights
            if (chartInstances.categoryChart) {{
                // Recalculate category data with new weights
                const categoryData = [];
                const categories = Object.keys(currentWeights);
                
                llmNames.forEach(llmName => {{
                    const result = originalScores.find(r => r.llm_name === llmName);
                    const scores = [];
                    categories.forEach(category => {{
                        const score = result?.analysis_scores[category]?.score || 0;
                        scores.push(score);
                    }});
                    categoryData.push(scores);
                }});
                
                // Update the chart datasets
                categoryData.forEach((scores, index) => {{
                    if (chartInstances.categoryChart.data.datasets[index]) {{
                        chartInstances.categoryChart.data.datasets[index].data = scores;
                    }}
                }});
                
                chartInstances.categoryChart.update();
            }}
        }}
        
        // Overall Performance Chart
        const overallCtx = document.getElementById('overallChart').getContext('2d');
        chartInstances.overallChart = new Chart(overallCtx, {{
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
        chartInstances.categoryChart = new Chart(categoryCtx, {{
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
        
        // Toggle weight controls visibility
        function toggleWeightControls() {{
            const content = document.getElementById('weight-controls-content');
            const toggle = document.getElementById('weight-toggle');
            
            if (content.classList.contains('expanded')) {{
                content.classList.remove('expanded');
                toggle.classList.add('collapsed');
            }} else {{
                content.classList.add('expanded');
                toggle.classList.remove('collapsed');
            }}
        }}
        
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
                    <td class="llm-rank" id="rank-{llm_name}">#{i}</td>
                    <td><strong>{llm_name}</strong></td>
                    <td><span class="score {score_class}" id="score-{llm_name}">{overall_score:.1f}</span></td>
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
        """Generate detailed content for each LLM result with enhanced UX"""
        
        details = []
        
        # File structure section
        files = result.get('files', [])
        if files:
            details.append('<div class="analysis-section">')
            details.append('<h4>📁 File Structure</h4>')
            details.append('<div class="file-structure">')
            details.append('<ul>')
            for file_info in files:
                filename = os.path.basename(file_info.get('path', 'unknown'))
                lines = file_info.get('lines', 0)
                size = file_info.get('size', 0)
                details.append(f'<li><strong>{filename}</strong>: {lines} lines, {size:,} bytes</li>')
            details.append('</ul>')
            details.append('</div>')
            details.append('</div>')
        
        # Analysis grid container
        details.append('<div class="analysis-grid">')
        
        # Analysis details
        analysis_scores = result.get('analysis_scores', {})
        for category in analyzer_categories:
            score_data = analysis_scores.get(category, {})
            if isinstance(score_data, dict):
                details.append('<div class="analysis-section">')
                
                # Get appropriate icon for each category
                icon = self._get_category_icon(category)
                details.append(f'<h4>{icon} {category}</h4>')
                details.append(f'<div class="score-display">{score_data.get("score", 0):.1f}/100</div>')
                
                # Add notes
                notes = score_data.get('notes', [])
                
                # Special handling for analyzers that store summary in max_score
                if category in ["Requirements Traceability Analysis", "Security Analysis", "Adaptability Analysis"]:
                    max_score_data = score_data.get('max_score', [])
                    if isinstance(max_score_data, list):
                        notes = max_score_data
                
                if notes and isinstance(notes, list):
                    details.append('<ul class="key-points">')
                    max_notes = 15 if category in ["Requirements Traceability Analysis", "Security Analysis", "Adaptability Analysis"] else 5
                    for note in notes[:max_notes]:
                        if note.strip():  # Skip empty strings
                            css_class = self._get_note_css_class(note)
                            details.append(f'<li class="{css_class}">{note}</li>')
                    details.append('</ul>')
                
                details.append('</div>')
        
        details.append('</div>')  # Close analysis-grid
        
        return "".join(details)
    
    def _get_category_icon(self, category: str) -> str:
        """Get appropriate icon for each analysis category"""
        icons = {
            'Adaptability Analysis': '🔧',
            'Code Quality Analysis': '🏗️',
            'Documentation Analysis': '📚',
            'Performance Analysis': '⚡',
            'Readability Analysis': '📖',
            'Requirements Traceability Analysis': '📋',
            'Security Analysis': '🔒'
        }
        return icons.get(category, '🔍')
    
    def _get_note_css_class(self, note: str) -> str:
        """Determine CSS class based on note content"""
        note_lower = note.lower().strip()
        
        # Positive indicators
        if (note.startswith('+') or 
            note.startswith('✓') or
            'excellent' in note_lower or
            'comprehensive' in note_lower or
            'good' in note_lower and not 'no' in note_lower):
            return 'positive'
        
        # Negative indicators  
        elif (note.startswith('-') or
              note.startswith('❌') or
              'no ' in note_lower or
              'limited' in note_lower or
              'missing' in note_lower):
            return 'negative'
        
        # Warning indicators
        elif (note.startswith('⚡') or
              'medium' in note_lower or
              'warning' in note_lower):
            return 'warning'
        
        # Success indicators
        elif (note.startswith('Requirements Implementation:') or
              note.startswith('Mandatory Requirements:') or
              'all mandatory requirements' in note_lower or
              note.lower().startswith('✓')):
            return 'success'
        
        # Error indicators
        elif ('critical' in note_lower or
              'error' in note_lower or
              'failed' in note_lower):
            return 'error'
        
        # Default to info
        else:
            return 'info'

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
