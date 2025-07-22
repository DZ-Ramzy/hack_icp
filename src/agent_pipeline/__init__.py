"""
Agent Pipeline - Comprehensive AI-driven market analysis system.

This package provides a modular, extensible framework for market analysis
using specialized AI agents integrated with the Internet Computer Protocol.
"""

__version__ = "1.0.0"
__author__ = "ICP Agents Team"

# Main imports for easy access
from agent_pipeline.core.orchestrator import PipelineOrchestrator, PipelineConfig
from agent_pipeline.cli.run import run_pipeline_with_interface

__all__ = [
    'PipelineOrchestrator', 
    'PipelineConfig',
    'run_pipeline_with_interface'
]