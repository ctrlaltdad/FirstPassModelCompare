#!/usr/bin/env python3
"""
Base Analysis Module

Defines the interface and base classes for all analysis modules.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import os

@dataclass
class FileInfo:
    """Information about a code file"""
    path: str
    size: int
    lines: int
    content: str

@dataclass
class AnalysisScore:
    """Result of a single analysis"""
    score: float  # 0-100
    max_score: float = 100.0
    notes: List[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.notes is None:
            self.notes = []
        if self.details is None:
            self.details = {}

class BaseAnalyzer(ABC):
    """Base class for all analysis modules"""
    
    def __init__(self, name: str, description: str, weight: float = 1.0):
        self.name = name
        self.description = description
        self.weight = weight
        self.enabled = True
    
    @abstractmethod
    def analyze(self, files: List[FileInfo], llm_name: str, prompt_requirements: Dict[str, Any]) -> AnalysisScore:
        """
        Analyze the given files and return a score
        
        Args:
            files: List of files to analyze
            llm_name: Name of the LLM being analyzed
            prompt_requirements: Original prompt requirements
            
        Returns:
            AnalysisScore object with score and details
        """
        pass
    
    @property
    def category(self) -> str:
        """Category of this analysis (e.g., 'code_quality', 'performance')"""
        return "general"
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this analyzer"""
        return {
            'name': self.name,
            'description': self.description,
            'weight': self.weight,
            'category': self.category,
            'enabled': self.enabled
        }

class AnalysisRegistry:
    """Registry for managing analysis modules"""
    
    def __init__(self):
        self.analyzers: List[BaseAnalyzer] = []
    
    def register(self, analyzer: BaseAnalyzer):
        """Register a new analyzer"""
        self.analyzers.append(analyzer)
        print(f"Registered analyzer: {analyzer.name}")
    
    def get_enabled_analyzers(self) -> List[BaseAnalyzer]:
        """Get all enabled analyzers"""
        return [a for a in self.analyzers if a.enabled]
    
    def get_by_category(self, category: str) -> List[BaseAnalyzer]:
        """Get analyzers by category"""
        return [a for a in self.analyzers if a.category == category and a.enabled]
    
    def disable_analyzer(self, name: str):
        """Disable an analyzer by name"""
        for analyzer in self.analyzers:
            if analyzer.name == name:
                analyzer.enabled = False
                print(f"Disabled analyzer: {name}")
                break
    
    def enable_analyzer(self, name: str):
        """Enable an analyzer by name"""
        for analyzer in self.analyzers:
            if analyzer.name == name:
                analyzer.enabled = True
                print(f"Enabled analyzer: {name}")
                break
    
    def list_analyzers(self) -> List[Dict[str, Any]]:
        """List all registered analyzers"""
        return [a.get_info() for a in self.analyzers]
