#!/usr/bin/env python3
"""
Test script to verify the framework works with 2 or 3 LLM solutions
"""

import sys
import os
sys.path.append('.')

from modular_analyzer import ModularLLMAnalyzer

def test_two_llm_analysis():
    """Test analysis with only 2 LLM solutions"""
    print("Testing analysis with 2 LLM solutions...")
    
    try:
        analyzer = ModularLLMAnalyzer('./test_workspace')
        results = analyzer.analyze_all_solutions()
        
        print(f"✅ Successfully analyzed {len(results)} LLM solutions")
        for result in results:
            print(f"   - {result.llm_name}: {result.overall_score:.1f} points")
        
        if len(results) == 2:
            print("✅ Framework correctly handles 2 LLM solutions")
        else:
            print(f"❌ Expected 2 solutions, got {len(results)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_two_llm_analysis()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
