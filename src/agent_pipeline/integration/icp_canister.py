"""
ICP Canister Integration - Bridge between agent pipeline and ICP_hack canisters.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging

from agent_pipeline.core.orchestrator import PipelineOrchestrator, PipelineConfig
from agent_pipeline.icp_agents.search import SearchAgent
from agent_pipeline.icp_agents.analysis import AnalysisAgent, AnalysisResult
from agent_pipeline.icp_agents.prediction import PredictionAgent, PredictionResult
from agent_pipeline.icp_agents.advice import AdviceAgent, MarketAdviceReport

logger = logging.getLogger(__name__)

class ICPAgentCanister:
    """
    ICP Canister interface for AI agents.
    
    This class provides the bridge between the agent pipeline and 
    ICP_hack's insight canister, enabling real AI-powered market analysis.
    """
    
    def __init__(self):
        self.orchestrator = PipelineOrchestrator()
        self.search_agent = None
        self.analysis_agent = None
        self.prediction_agent = None
        self.advice_agent = None
        
    async def initialize_agents(self) -> bool:
        """Initialize all agents for the canister."""
        try:
            # Initialize agents lazily to avoid startup overhead
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            return False
    
    async def generate_insight(
        self, 
        market_id: str, 
        market_title: str, 
        market_description: str,
        current_price: Optional[float] = None,
        research_depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate AI insight for a market (replaces mock implementation in ICP_hack).
        
        Args:
            market_id: Unique identifier for the market
            market_title: Market question/title
            market_description: Detailed market description
            current_price: Current market price (implied probability)
            research_depth: Level of research ("quick", "standard", "deep")
            
        Returns:
            Dict containing AI insight with probability, confidence, reasoning, etc.
        """
        try:
            logger.info(f"Generating AI insight for market {market_id}: {market_title}")
            
            # Configure pipeline
            config = PipelineConfig(
                research_depth=research_depth,
                use_scenario_analysis=True,
                timeout_seconds=300
            )
            
            # Run full agent pipeline
            result = await self.orchestrator.analyze_market(
                question=market_title,
                market_context=market_description,
                market_price=current_price,
                config=config
            )
            
            # Convert to ICP canister format
            insight_data = {
                "market_id": market_id,
                "generated_at": datetime.now().isoformat(),
                "ai_prediction": {
                    "probability": result.probability,
                    "confidence": result.confidence.upper(),
                    "recommendation": result.recommendation,
                    "reasoning": result.reasoning[:500],  # Truncate for canister storage
                },
                "risk_assessment": {
                    "risk_level": result.risk_level,
                    "risk_factors": result.errors if result.errors else ["Standard market risks"]
                },
                "market_analysis": {
                    "kelly_fraction": getattr(result, 'kelly_fraction', 0.0),
                    "expected_value": getattr(result, 'expected_value', 0.0),
                    "market_price": current_price
                },
                "metadata": {
                    "research_depth": research_depth,
                    "processing_time": result.duration_seconds,
                    "agent_version": "1.0.0",
                    "success": result.success
                }
            }
            
            logger.info(f"AI insight generated successfully for market {market_id}")
            return insight_data
            
        except Exception as e:
            logger.error(f"Failed to generate insight for market {market_id}: {e}")
            return {
                "market_id": market_id,
                "generated_at": datetime.now().isoformat(),
                "error": str(e),
                "ai_prediction": {
                    "probability": 0.5,
                    "confidence": "LOW",
                    "recommendation": "INSUFFICIENT_DATA",
                    "reasoning": f"AI analysis failed: {str(e)}"
                },
                "metadata": {
                    "success": False,
                    "error_type": type(e).__name__
                }
            }
    
    async def validate_market(
        self, 
        market_title: str, 
        market_description: str,
        resolution_criteria: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate market quality and provide recommendations for improvement.
        
        Args:
            market_title: Proposed market title
            market_description: Market description
            resolution_criteria: How the market will be resolved
            
        Returns:
            Dict with validation result and suggestions
        """
        try:
            # Use search agent for quick validation research
            if not self.search_agent:
                self.search_agent = SearchAgent(market_title)
            
            # Quick research on the market topic
            research_result = await self.search_agent.research(
                f"Market validation: {market_title}"
            )
            
            # Basic validation logic
            validation_score = 0.8  # Would be calculated based on research
            is_valid = len(market_title) > 10 and len(market_description) > 50
            
            validation_result = {
                "is_valid": is_valid,
                "validation_score": validation_score,
                "suggestions": [],
                "research_summary": research_result[:200] if research_result else "No research available",
                "validated_at": datetime.now().isoformat()
            }
            
            # Add suggestions based on validation
            if len(market_title) <= 10:
                validation_result["suggestions"].append("Market title should be more descriptive")
            
            if len(market_description) <= 50:
                validation_result["suggestions"].append("Market description needs more detail")
            
            if not resolution_criteria:
                validation_result["suggestions"].append("Consider adding clear resolution criteria")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Market validation failed: {e}")
            return {
                "is_valid": False,
                "validation_score": 0.0,
                "error": str(e),
                "validated_at": datetime.now().isoformat()
            }
    
    async def batch_analyze_markets(
        self, 
        markets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple markets in batch for efficiency.
        
        Args:
            markets: List of market dicts with id, title, description
            
        Returns:
            List of insights for each market
        """
        insights = []
        
        # Process markets with some concurrency but not too much to avoid API limits
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent analyses
        
        async def analyze_single_market(market_data):
            async with semaphore:
                return await self.generate_insight(
                    market_id=market_data["id"],
                    market_title=market_data["title"],
                    market_description=market_data.get("description", ""),
                    current_price=market_data.get("price"),
                    research_depth="quick"  # Use quick analysis for batch processing
                )
        
        tasks = [analyze_single_market(market) for market in markets]
        insights = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_insights = []
        for i, insight in enumerate(insights):
            if isinstance(insight, Exception):
                logger.error(f"Batch analysis failed for market {markets[i].get('id', i)}: {insight}")
                processed_insights.append({
                    "market_id": markets[i].get("id", f"market_{i}"),
                    "error": str(insight),
                    "success": False
                })
            else:
                processed_insights.append(insight)
        
        return processed_insights
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents."""
        return {
            "canister_status": "active",
            "agents_initialized": {
                "search_agent": self.search_agent is not None,
                "analysis_agent": self.analysis_agent is not None,
                "prediction_agent": self.prediction_agent is not None,
                "advice_agent": self.advice_agent is not None
            },
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }


# Factory function for easy integration
def create_icp_agent_canister() -> ICPAgentCanister:
    """Create and return an initialized ICP Agent Canister."""
    return ICPAgentCanister()


# Main functions that can be called from ICP_hack's insight canister
async def icp_generate_insight(
    market_id: str,
    market_title: str, 
    market_description: str,
    current_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Main function to be called from ICP_hack's insight canister.
    
    This replaces the mock implementation in the insight.mo canister.
    """
    canister = create_icp_agent_canister()
    await canister.initialize_agents()
    
    return await canister.generate_insight(
        market_id=market_id,
        market_title=market_title,
        market_description=market_description,
        current_price=current_price
    )


async def icp_validate_market(
    market_title: str,
    market_description: str,
    resolution_criteria: Optional[str] = None
) -> Dict[str, Any]:
    """
    Market validation function for ICP_hack integration.
    """
    canister = create_icp_agent_canister()
    await canister.initialize_agents()
    
    return await canister.validate_market(
        market_title=market_title,
        market_description=market_description,
        resolution_criteria=resolution_criteria
    )


if __name__ == "__main__":
    # Test the integration
    async def test_integration():
        canister = create_icp_agent_canister()
        await canister.initialize_agents()
        
        # Test insight generation
        test_insight = await canister.generate_insight(
            market_id="test_001",
            market_title="Will Bitcoin reach $100,000 by end of 2025?",
            market_description="Prediction market for Bitcoin price reaching $100k by December 31, 2025",
            current_price=0.35
        )
        
        print("Test Insight Generated:")
        print(json.dumps(test_insight, indent=2))
        
        # Test market validation
        validation = await canister.validate_market(
            market_title="Will Bitcoin reach $100,000 by end of 2025?",
            market_description="Prediction market for Bitcoin price reaching $100k by December 31, 2025"
        )
        
        print("\nMarket Validation:")
        print(json.dumps(validation, indent=2))
    
    asyncio.run(test_integration())