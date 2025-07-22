"""
Pipeline Orchestrator - Simplified agent coordination using Agents library patterns.
"""

from agents import Agent, Runner
from typing import Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import asyncio
import logging

# Updated imports for new structure
from agent_pipeline.icp_agents.search import SearchAgent
from agent_pipeline.icp_agents.analysis import AnalysisAgent
from agent_pipeline.icp_agents.prediction import PredictionAgent
from agent_pipeline.icp_agents.advice import AdviceAgent
from agent_pipeline.icp_agents.scenario import ThinkThoroughlyAgent
from agent_pipeline.utils.memory_system import MemorySystem
from agent_pipeline.config.env_config import config

# Configure logging - will be overridden by rich console in run.py
logger = logging.getLogger(__name__)


class PipelineConfig(BaseModel):
    """Simple pipeline configuration."""
    research_depth: str = "standard"  # quick, standard, deep
    use_scenario_analysis: bool = True
    timeout_seconds: int = 300  # 5 minutes default


class PipelineResult(BaseModel):
    """Structured pipeline output."""
    success: bool
    run_id: str
    market_question: str
    recommendation: str
    probability: float
    confidence: str
    risk_level: str
    reasoning: str
    duration_seconds: float
    errors: List[str] = []


class PipelineOrchestrator:
   
    
    def __init__(self):
        # Validate API keys on startup
        if not config.validate_required_keys():
            raise ValueError("Required API keys not found in environment")
        
        # Core agents
        self.analysis_agent = AnalysisAgent()
        self.prediction_agent = PredictionAgent()
        self.advice_agent = AdviceAgent()
        
        # Optional advanced agents
        self.think_thoroughly_agent = ThinkThoroughlyAgent()
        self.memory_system = MemorySystem()
        
        # Simple direct approach - no complex orchestration needed
    
    async def analyze_market(
        self, 
        market_question: str, 
        config: PipelineConfig = None,
        market_price: float = None
    ) -> PipelineResult:
        """
        Main entry point - analyze market question with optional configuration.
        Handles research, scenario analysis, social sentiment, prediction, and advice.

        """
        if config is None:
            config = PipelineConfig()
        
        start_time = datetime.now()
        run_id = f"run_{start_time.strftime('%Y%m%d_%H%M%S')}"
        errors = []
        
        try:
            logger.info(f"Starting market analysis: {run_id}")
            logger.info(f"Question: {market_question}")
            
            # Step 1: Research (always required)
            logger.info("Starting research phase")
            research_result = await self._run_with_timeout(
                self._do_research(market_question, config.research_depth),
                config.timeout_seconds
            )
            
            # Step 2: Scenario analysis (sequential - needs research results)
            scenario_report = None
            if config.use_scenario_analysis:
                logger.info("Starting scenario analysis based on research")
                scenario_report = await self._run_with_timeout(
                    self._do_scenario_analysis(market_question, research_result, config.research_depth),
                    config.timeout_seconds
                )
            
            
            
            # Step 4: Generate prediction and advice
            logger.info("Generating prediction")
            prediction_result = await self._generate_prediction(
                research_result, market_question, scenario_report, market_price
            )
            
            logger.info("Creating comprehensive advice based on all analysis")
            advice_result = await self._generate_advice(
                prediction_result, research_result, scenario_report, market_question
            )
            
            # Step 5: Store in memory (optional)
            if hasattr(self, 'memory_system'):
                logger.info("Storing results in memory")
                await self._store_results(prediction_result, market_question, config)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return PipelineResult(
                success=True,
                run_id=run_id,
                market_question=market_question,
                recommendation=advice_result.advice.primary_recommendation,
                probability=prediction_result.prediction.probability,
                confidence=prediction_result.prediction.confidence_level,
                risk_level=advice_result.risk_assessment.overall_risk_level,
                reasoning=advice_result.advice.reasoning,
                duration_seconds=duration,
                errors=errors
            )
            
        except asyncio.TimeoutError:
            errors.append("Pipeline execution timed out")
            return self._create_error_result(run_id, market_question, errors, start_time)
        except Exception as e:
            errors.append(f"Pipeline error: {str(e)}")
            logger.error(f"Pipeline failed: {e}")
            return self._create_error_result(run_id, market_question, errors, start_time)
    
    async def _run_with_timeout(self, coro, timeout_seconds: int):
        """Simple timeout wrapper."""
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    
    async def _do_research(self, question: str, depth: str) -> str:
        """Execute research step."""
        search_agent = SearchAgent(question)
        return await search_agent.research(question)
    
    async def _do_scenario_analysis(self, question: str, research_result: str, _depth: str) -> Any:
        """Execute scenario analysis step using research results."""
        return await self.think_thoroughly_agent.analyze_market_thoroughly(
            question, research_report=research_result, research_depth=_depth
        )
    
    
    async def _enrich_question_with_market_data(self, question: str) -> str:
        """Enrichir la question avec des données de marché actuelles pour le calcul Kelly."""
        # Pour l'instant, retourner la question originale
        # TODO: Intégrer des APIs de prix (Polymarket, Kalshi, etc.) pour les vraies cotes
        return question
    
    async def _generate_prediction(self, research_result: str, question: str, _scenario_report, market_price: float = None) -> Any:
        """Generate prediction from research and analysis."""
        # Analyze research
        analysis_result = await self.analysis_agent.analyze_report(research_result, question)
        
        # Generate prediction with market price
        prediction_result = await self.prediction_agent.generate_prediction(
            analysis_result, question, market_price
        )
        
        return prediction_result
    
    async def _generate_advice(self, prediction_result: Any, research_result: str, scenario_report: Any, _market_question: str) -> Any:
        """Generate comprehensive final market advice integrating all pipeline elements."""
        
        # Prepare market context from research as string
        market_context = f"Research Summary: {research_result[:500]}{'...' if len(research_result) > 500 else ''}"
        
        # Prepare scenario results as string if available
        scenario_context = None
        if scenario_report:
            scenario_context = f"""Scenario Analysis Results:
Executive Summary: {getattr(scenario_report, 'executive_summary', 'N/A')}
Key Insights: {', '.join(getattr(scenario_report, 'key_insights', [])[:3])}
Decision Framework: {getattr(scenario_report, 'decision_framework', 'N/A')[:200]}"""
        
        # Generate comprehensive advice with all context
        return await self.advice_agent.generate_market_advice(
            prediction_result=prediction_result,
            market_context=market_context,
            scenario_results=scenario_context,
            social_results=None,  # Not used since we removed social media
            historical_data=None  # Could be added later
        )
    
    async def _store_results(self, _prediction_result: Any, _question: str, _config: PipelineConfig):
        """Store results in memory for learning."""
        # Simple storage - can be enhanced later
        # TODO: Implement memory storage using prediction_result, question, and config
        pass
    
    def _extract_topic(self, question: str) -> str:
        """Extract topic for social sentiment analysis."""
        question_lower = question.lower()
        
        topics = {
            "bitcoin": ["bitcoin", "btc"],
            "ethereum": ["ethereum", "eth"],
            "crypto": ["crypto", "cryptocurrency"],
        }
        
        for topic, keywords in topics.items():
            if any(keyword in question_lower for keyword in keywords):
                return topic
        
        # Default to first significant word
        words = question.split()
        for word in words:
            if len(word) > 3 and word.lower() not in ["will", "does", "when"]:
                return word.lower()
        
        return "general"
    
    def _create_error_result(self, run_id: str, question: str, errors: List[str], start_time: datetime) -> PipelineResult:
        """Create error result."""
        duration = (datetime.now() - start_time).total_seconds()
        return PipelineResult(
            success=False,
            run_id=run_id,
            market_question=question,
            recommendation="AVOID",
            probability=0.5,
            confidence="low",
            risk_level="HIGH",
            reasoning="Analysis failed due to errors",
            duration_seconds=duration,
            errors=errors
        )


# Simple factory function
def create_pipeline() -> PipelineOrchestrator:
    """Create a new pipeline orchestrator."""
    return PipelineOrchestrator()


# Example usage
async def main():
    """Example usage of the simplified orchestrator."""
    orchestrator = create_pipeline()
    
    config = PipelineConfig(
        research_depth="standard",
        use_scenario_analysis=True,
        timeout_seconds=180  # 3 minutes
    )
    
    result = await orchestrator.analyze_market(
        "Will Bitcoin reach $100,0000 by end of 2035?",
        config,
        market_price=0.45  # Exemple: 45% de probabilité implicite du marché
    )
    
    logger.info("Analysis Complete")
    logger.info(f"Recommendation: {result.recommendation}")
    logger.info(f"Probability: {result.probability:.1%}")
    logger.info(f"Confidence: {result.confidence}")
    logger.info(f"Duration: {result.duration_seconds:.1f}s")
    
    if result.errors:
        logger.error(f"Errors: {result.errors}")


if __name__ == "__main__":
    asyncio.run(main())