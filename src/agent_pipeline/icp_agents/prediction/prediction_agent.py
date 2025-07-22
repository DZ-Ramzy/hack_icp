from agents import Agent, Runner
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Handle imports for both module and direct execution
try:
    from ..analysis import AnalysisResult, MarketInsight
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from analysis.analysis_agent import AnalysisResult, MarketInsight
import logging


PREDICTION_PROMPT = """
You are an expert prediction agent that converts market insights into probability estimates.
Your task is to analyze market insights and generate probabilistic predictions for market outcomes.

PREDICTION REQUIREMENTS:
- Convert qualitative insights into quantitative probabilities
- Account for confidence levels and signal strength
- Consider time horizons and market dynamics
- Provide clear reasoning for probability estimates
- Include risk-adjusted confidence intervals
- Factor in market efficiency and information asymmetries

PROBABILITY GUIDELINES:
- Use evidence-based reasoning
- Account for base rates and historical precedents
- Consider multiple scenarios and outcomes
- Adjust for market sentiment and momentum
- Include uncertainty bounds
- Provide calibrated probability estimates

OUTPUT STRUCTURE:
- Primary Prediction: Main probability estimate with reasoning
- Confidence Interval: Upper and lower bounds
- Key Factors: Most important drivers of the prediction
- Risk Adjustments: How risks affect the probability
- Time Sensitivity: How prediction changes over time
- Alternative Scenarios: Other possible outcomes

Focus on well-calibrated probability estimates that reflect true uncertainty.
"""

POSITION_SIZING_PROMPT = """
You are a risk management specialist that determines optimal position sizes for prediction market bets.
Convert probability estimates into specific trading recommendations.

POSITION SIZING CRITERIA:
- Kelly Criterion for optimal bet size
- Risk tolerance and bankroll management
- Market liquidity and slippage considerations
- Confidence level and uncertainty bounds
- Expected value and risk-adjusted returns

RISK MANAGEMENT:
- Maximum position size limits (never exceed 15% of bankroll)
- Stop-loss and take-profit levels
- Market volatility adjustments

Provide specific position sizing recommendations with clear risk parameters.
"""


class PredictionEstimate(BaseModel):
    probability: float  # 0-1 probability estimate
    confidence_lower: float  # Lower bound of confidence interval
    confidence_upper: float  # Upper bound of confidence interval
    confidence_level: str  # low, medium, high
    reasoning: str  # Explanation of the prediction
    key_factors: List[str]  # Most important drivers
    time_horizon: str  # When prediction applies
    alternative_scenarios: List[str]  # Other possible outcomes


class PositionRecommendation(BaseModel):
    action: str  # BUY_YES, BUY_NO, HOLD, AVOID
    position_size: float  # Percentage of bankroll (0-1)
    max_exposure: float  # Maximum amount to risk
    entry_price_target: Optional[float]  # Ideal entry price
    stop_loss: Optional[float]  # Stop loss level
    take_profit: Optional[float]  # Take profit level
    reasoning: str  # Why this position is recommended
    risk_level: str  # low, medium, high


class PredictionResult(BaseModel):
    market_question: str
    prediction: PredictionEstimate
    position_recommendation: PositionRecommendation
    overall_assessment: str
    risk_factors: List[str]
    expected_value: float
    kelly_fraction: float


class PredictionAgent:
    """Agent that converts market insights into probability estimates and trading recommendations."""
    
    def __init__(self):
        self.prediction_agent = Agent(
            name="ProbabilityPredictionAgent",
            instructions=PREDICTION_PROMPT,
            output_type=PredictionEstimate,
            model="gpt-4o"
        )
        
        self.position_agent = Agent(
            name="PositionSizingAgent",
            instructions=POSITION_SIZING_PROMPT,
            output_type=PositionRecommendation,
            model="gpt-4o-mini"
        )
    
    async def generate_prediction(
        self, 
        analysis_result: AnalysisResult, 
        market_question: str,
        current_market_price: Optional[float] = None
    ) -> PredictionResult:
        """
        Generate probability prediction from analysis results.
        
        Args:
            analysis_result: Results from AnalysisAgent
            market_question: The market question to predict
            current_market_price: Current market price (if available)
            
        Returns:
            Complete prediction with probability estimates and position recommendations
        """
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Starting probability prediction generation[/dim]")
        
        # Generate probability estimate
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Calculating probability estimates from market insights[/dim]")
        prediction_input = f"""
        Market Question: {market_question}
        Current Market Price: {current_market_price or "Unknown"}
        
        Analysis Summary:
        - Overall Sentiment: {analysis_result.overall_sentiment}
        - Confidence Level: {analysis_result.confidence_level}
        - Key Drivers: {', '.join(analysis_result.key_drivers)}
        - Risk Assessment: {analysis_result.risk_assessment}
        
        Market Insights:
        {self._format_insights_for_prediction(analysis_result.market_insights)}
        
        Analysis Summary:
        {analysis_result.analysis_summary}
        
        Current Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        Generate a well-calibrated probability estimate for this market question.
        """
        
        prediction_result = await Runner.run(
            self.prediction_agent,
            input=prediction_input
        )
        prediction = prediction_result.final_output
        
        if hasattr(self, 'console'):
            confidence_level = prediction.confidence_level if hasattr(prediction, 'confidence_level') else "unknown"
            self.console.print(f"[dim]→ Probability estimate complete - confidence: {confidence_level}[/dim]")
        
        # Generate position recommendation
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Calculating optimal position sizing recommendations[/dim]")
        position_input = f"""
        Market Question: {market_question}
        Current Market Price: {current_market_price or "Unknown"}
        
        Prediction Results:
        - Probability Estimate: {prediction.probability:.3f}
        - Confidence Interval: [{prediction.confidence_lower:.3f}, {prediction.confidence_upper:.3f}]
        - Confidence Level: {prediction.confidence_level}
        - Reasoning: {prediction.reasoning}
        
        Market Analysis:
        - Overall Sentiment: {analysis_result.overall_sentiment}
        - Number of Insights: {len(analysis_result.market_insights)}
        - High Confidence Insights: {len([i for i in analysis_result.market_insights if i.confidence == "high"])}
        
        Calculate optimal position size and trading recommendation.
        """
        
        position_result = await Runner.run(
            self.position_agent,
            input=position_input
        )
        position = position_result.final_output
        
        if hasattr(self, 'console'):
            action = position.action if hasattr(position, 'action') else "UNKNOWN"
            self.console.print(f"[dim]→ Position recommendation: {action}[/dim]")
        
        # Calculate expected value and Kelly fraction
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Computing Kelly fraction and expected value[/dim]")
        expected_value = self._calculate_expected_value(prediction, current_market_price)
        kelly_fraction = self._calculate_kelly_fraction(prediction, current_market_price)
        
        if hasattr(self, 'console'):
            self.console.print(f"[dim]→ Kelly fraction: {kelly_fraction:.1%}, Expected value: {expected_value:.3f}[/dim]")
        
        return PredictionResult(
            market_question=market_question,
            prediction=prediction,
            position_recommendation=position,
            overall_assessment=self._generate_overall_assessment(prediction, position, analysis_result),
            risk_factors=self._extract_risk_factors(analysis_result),
            expected_value=expected_value,
            kelly_fraction=kelly_fraction
        )
    
    def _format_insights_for_prediction(self, insights: List[MarketInsight]) -> str:
        """Format insights for prediction input."""
        if not insights:
            return "No specific insights available."
        
        formatted = ""
        for i, insight in enumerate(insights, 1):
            formatted += f"""
            Insight {i}:
            - Signal: {insight.signal_type} ({insight.strength} strength)
            - Time Horizon: {insight.time_horizon}
            - Confidence: {insight.confidence}
            - Evidence: {insight.evidence}
            - Risk Factors: {insight.risk_factors}
            - Impact Score: {insight.impact_score}
            """
        
        return formatted
    
    def _calculate_expected_value(self, prediction: PredictionEstimate, market_price: Optional[float]) -> float:
        """Calculate expected value of the bet."""
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Analyzing expected value for betting opportunity[/dim]")
            
        if market_price is None:
            return 0.0
        
        # Expected value calculation for binary market
        # EV = (probability * payout_if_win) - (1-probability * stake)
        
        # Assuming we bet on YES
        prob_yes = prediction.probability
        price_yes = market_price
        
        if price_yes <= 0 or price_yes >= 1:
            return 0.0
        
        payout_ratio = 1 / price_yes
        expected_value = (prob_yes * payout_ratio) - 1
        
        return expected_value
    
    def _calculate_kelly_fraction(self, prediction: PredictionEstimate, market_price: Optional[float]) -> float:
        """Calculate Kelly Criterion fraction for optimal bet sizing."""
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Applying Kelly Criterion for optimal bet sizing[/dim]")
            
        if market_price is None or market_price <= 0 or market_price >= 1:
            return 0.0
        
        # Kelly formula: f = (bp - q) / b
        # where:
        # f = fraction of bankroll to bet
        # b = odds received (payout ratio - 1)
        # p = probability of winning
        # q = probability of losing (1 - p)
        
        p = prediction.probability  # Our probability estimate
        market_prob = market_price  # Market's implied probability
        
        # Calculate odds received
        if market_prob >= 0.99:
            return 0.0  # No edge
        
        payout_ratio = 1 / market_prob
        b = payout_ratio - 1  # Net odds
        
        q = 1 - p  # Probability of losing
        
        # Kelly fraction
        kelly = (b * p - q) / b
        
        # Apply confidence adjustment
        confidence_multiplier = {
            "low": 0.25,
            "medium": 0.5, 
            "high": 0.75
        }.get(prediction.confidence_level, 0.5)
        
        if hasattr(self, 'console'):
            self.console.print(f"[dim]→ Adjusting Kelly fraction for {prediction.confidence_level} confidence level[/dim]")
        
        adjusted_kelly = kelly * confidence_multiplier
        
        # Cap at reasonable maximum (15% of bankroll)
        return max(0.0, min(adjusted_kelly, 0.15))
    
    
    def _generate_overall_assessment(
        self, 
        prediction: PredictionEstimate, 
        position: PositionRecommendation, 
        analysis: AnalysisResult
    ) -> str:
        """Generate overall assessment of the prediction and recommendation."""
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Generating comprehensive investment assessment[/dim]")
        
        assessment_parts = []
        
        # Prediction quality assessment
        if prediction.confidence_level == "high":
            assessment_parts.append("High confidence prediction based on strong evidence")
        elif prediction.confidence_level == "medium":
            assessment_parts.append("Moderate confidence prediction with some uncertainty")
        else:
            assessment_parts.append("Low confidence prediction due to limited evidence")
        
        # Analysis insights integration
        if analysis and analysis.market_insights:
            insight_count = len(analysis.market_insights)
            assessment_parts.append(f"Analysis based on {insight_count} market insights")
        
        # Position recommendation assessment
        if position.action in ["BUY_YES", "BUY_NO"]:
            assessment_parts.append(f"Recommended {position.action} with {position.position_size:.1%} position size")
        else:
            assessment_parts.append(f"Recommended to {position.action} due to insufficient edge")
        
        # Risk assessment
        if position.risk_level == "high":
            assessment_parts.append("High risk trade requiring careful monitoring")
        elif position.risk_level == "medium":
            assessment_parts.append("Moderate risk with standard position management")
        else:
            assessment_parts.append("Low risk opportunity with good risk/reward ratio")
        
        return ". ".join(assessment_parts) + "."
    
    def _extract_risk_factors(self, analysis: AnalysisResult) -> List[str]:
        """Extract key risk factors from analysis."""
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Identifying and consolidating risk factors[/dim]")
            
        risk_factors = []
        
        # Add risks from analysis
        if hasattr(analysis, 'risk_assessment') and analysis.risk_assessment:
            risk_factors.append(analysis.risk_assessment)
        
        # Add risks from individual insights
        for insight in analysis.market_insights:
            if insight.risk_factors and insight.risk_factors.strip():
                risk_factors.append(insight.risk_factors)
        
        # Deduplicate and limit
        unique_risks = list(set(risk_factors))[:5]
        
        return unique_risks if unique_risks else ["Standard market volatility and uncertainty"]
    

logger = logging.getLogger(__name__)

async def main():
    """Test the prediction agent"""
    
    # Mock analysis result for testing - imports already handled above
    
    sample_insights = [
        MarketInsight(
            signal_type="bullish",
            strength="strong", 
            time_horizon="medium-term",
            confidence="high",
            evidence="Institutional adoption increasing 300% QoQ with BlackRock ETF inflows",
            risk_factors="Potential regulatory changes and market volatility",
            impact_score=0.8
        ),
        MarketInsight(
            signal_type="bullish",
            strength="moderate",
            time_horizon="short-term", 
            confidence="medium",
            evidence="Technical indicators showing bullish momentum above key resistance",
            risk_factors="Possible correction if Federal Reserve changes policy",
            impact_score=0.6
        )
    ]
    
    sample_analysis = AnalysisResult(
        market_insights=sample_insights,
        overall_sentiment="BULLISH",
        key_drivers=["Institutional adoption", "Technical momentum", "Regulatory clarity"],
        risk_assessment="Moderate risk due to regulatory uncertainty and market volatility",
        confidence_level="high",
        analysis_summary="Strong bullish indicators with institutional support and technical momentum"
    )
    
    market_question = "Will Bitcoin reach $100,000 by end of 2024?"
    current_price = 0.35  # 35% implied probability
    
    prediction_agent = PredictionAgent()
    
    logger.info("Starting prediction generation process")
    result = await prediction_agent.generate_prediction(
        sample_analysis, 
        market_question, 
        current_price
    )
    
    logger.info("Prediction generation completed successfully")
    return result  # Return the result to make it clear it's being used
    


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())