"""
ICP Agents - Streamlined prediction market analysis for ICP
"""

__version__ = "0.1.0"

# Lazy imports to avoid import issues when modules are used independently
def get_pipeline():
    """Get pipeline orchestrator"""
    from .orchestrator import create_pipeline
    return create_pipeline()

def get_prediction_agent():
    """Get prediction agent"""  
    from .prediction_agent import PredictionAgent
    return PredictionAgent()

def get_analysis_agent():
    """Get analysis agent"""
    from .analysis_agent import AnalysisAgent
    return AnalysisAgent()

def get_think_thoroughly_agent():
    """Get think thoroughly agent"""
    from .think_thoroughly_agent import ThinkThoroughlyAgent
    return ThinkThoroughlyAgent()

__all__ = [
    "get_pipeline",
    "get_prediction_agent", 
    "get_analysis_agent",
    "get_think_thoroughly_agent",
    "__version__"
]