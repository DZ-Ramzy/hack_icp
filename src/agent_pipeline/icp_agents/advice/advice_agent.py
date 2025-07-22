"""
Advice Agent - Generate comprehensive market advice and recommendations without execution.
"""

from agents import Agent, Runner
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Handle imports for both module and direct execution
try:
    from ..prediction import PredictionResult, PositionRecommendation, PredictionEstimate
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from prediction.prediction_agent import PredictionResult, PositionRecommendation, PredictionEstimate


MARKET_ADVICE_PROMPT = """
You are an expert market advisor who must ALIGN all analyses and make a FINAL DECISION.
Your job is to reconcile research, scenarios, and predictions into ONE coherent recommendation.

YOUR DECISION PROCESS:
1. ALIGNMENT ANALYSIS: Do research, scenarios, and prediction agree or disagree?
2. EVIDENCE WEIGHING: Which source of evidence is most reliable and why?
3. CONFLICT RESOLUTION: If analyses conflict, which one should dominate the decision and why?
4. FINAL CHOICE: Make a clear, definitive recommendation with position size

CRITICAL REQUIREMENTS:
- Start with: "After aligning research findings, scenario analysis, and prediction metrics, my FINAL RECOMMENDATION is..."
- If analyses agree → Explain why this strengthens confidence in the decision
- If analyses disagree → Explain which evidence you trust more and why
- Make ONE clear choice: BUY_YES, BUY_NO, or AVOID (no hedging)
- Give ONE position size based on aligned evidence quality
- Justify why THIS decision is optimal given ALL the evidence

DECISION STRUCTURE:
1. ALIGNMENT ASSESSMENT: "Research says X, scenarios show Y, prediction estimates Z"
2. EVIDENCE HIERARCHY: "I weight [source] most heavily because..."
3. CONFLICT RESOLUTION: "Despite disagreement between A and B, I choose A because..."
4. FINAL DECISION: "Therefore, I recommend [ACTION] with [SIZE]% position because..."
5. EXECUTION PLAN: Specific entry, timing, and exit strategy
6. DECISION CONFIDENCE: How certain you are and what could change your mind

NO SYNTHESIS - MAKE A CHOICE. Explain why your final decision is the best given all evidence.
"""

RISK_ASSESSMENT_PROMPT = """
You are a risk assessment specialist for prediction markets.
Evaluate the risks associated with a market recommendation and provide comprehensive risk analysis.

RISK ANALYSIS REQUIREMENTS:
- Identify all major risk categories
- Assess probability and impact of each risk
- Provide risk mitigation strategies
- Recommend monitoring indicators
- Suggest position size adjustments based on risk
- Include scenario-based risk analysis

RISK CATEGORIES:
- Market Risk: Price volatility and adverse movements
- Liquidity Risk: Ability to enter/exit positions
- Information Risk: Incomplete or incorrect information
- Timing Risk: Early or late market entry/exit
- Correlation Risk: Related market movements
- Black Swan Risk: Unexpected major events

Provide actionable risk management recommendations.
"""


class MarketAdvice(BaseModel):
    """Final aligned market decision."""
    market_question: str
    primary_recommendation: str  # BUY_YES, BUY_NO, AVOID (clear choice)
    recommended_position_size: float  # 0-1 scale (single decision)
    confidence_level: str       # HIGH, MEDIUM, LOW (based on alignment)
    
    # Alignment analysis
    analysis_alignment: str     # AGREE, DISAGREE, MIXED
    evidence_hierarchy: str     # Which source dominates decision
    conflict_resolution: str    # How conflicts were resolved
    
    # Decision justification
    reasoning: str             # Why this final choice is optimal
    decision_confidence: str   # How certain and what could change mind
    
    # Execution
    entry_timing: str          # IMMEDIATE, WAIT_FOR_DIP, AVOID
    exit_strategy: str         # Target price or conditions
    monitoring_points: List[str] # What to watch for decision change
    time_horizon: str          # SHORT_TERM, MEDIUM_TERM, LONG_TERM


class RiskAssessment(BaseModel):
    """Comprehensive risk assessment."""
    overall_risk_level: str    # LOW, MEDIUM, HIGH, EXTREME
    risk_score: float         # 0-1 scale
    major_risks: List[str]    # Key risk factors
    risk_mitigation: List[str]  # How to reduce risks
    position_size_adjustment: float  # Risk-adjusted position size
    stop_loss_recommendation: float  # Suggested stop loss (use 0.0 if none)
    monitoring_indicators: List[str]  # Early warning signs


class MarketAdviceReport(BaseModel):
    """Complete market advice report."""
    market_question: str
    advice: MarketAdvice
    risk_assessment: RiskAssessment
    # Simplified probability analysis
    primary_probability: float
    confidence_lower: float
    confidence_upper: float
    # Kelly analysis
    kelly_fraction: float
    expected_value: float
    recommended_position: float
    # Report metadata
    report_timestamp: str
    confidence_score: float  # Overall confidence in advice


class AdviceAgent:
    """
    Agent that generates comprehensive market advice without executing trades.
    """
    
    def __init__(self):
        self.advice_agent = Agent(
            name="MarketAdviceAgent",
            instructions=MARKET_ADVICE_PROMPT,
            output_type=MarketAdvice,
            model="gpt-4o"
        )
        
        self.risk_agent = Agent(
            name="RiskAssessmentAgent",
            instructions=RISK_ASSESSMENT_PROMPT,
            output_type=RiskAssessment,
            model="gpt-4o-mini"
        )
    
    async def generate_market_advice(
        self,
        prediction_result: PredictionResult,
        market_context: Optional[str] = None,
        scenario_results: Optional[str] = None,
        social_results: Optional[str] = None,
        historical_data: Optional[str] = None
    ) -> MarketAdviceReport:
        """
        Generate comprehensive market advice based on prediction results.
        
        Args:
            prediction_result: Results from PredictionAgent
            market_context: Current market conditions
            scenario_results: Results from scenario analysis
            social_results: Social media sentiment data
            historical_data: Historical performance data
            
        Returns:
            Complete market advice report
        """
        
        # Utiliser la console partagée si disponible
        if hasattr(self, 'console'):
            self.console.print(f"[dim]→ Generating comprehensive advice for market question[/dim]")
        
        # Generate primary market advice
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Creating primary recommendation based on analysis[/dim]")
        advice = await self._generate_primary_advice(
            prediction_result, market_context, scenario_results
        )
        
        # Generate risk assessment
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Conducting comprehensive risk assessment[/dim]")
        risk_assessment = await self._generate_risk_assessment(
            prediction_result, advice, market_context
        )
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence_score(
            prediction_result, advice, risk_assessment
        )
        
        report = MarketAdviceReport(
            market_question=prediction_result.market_question,
            advice=advice,
            risk_assessment=risk_assessment,
            # Probability analysis
            primary_probability=prediction_result.prediction.probability,
            confidence_lower=prediction_result.prediction.confidence_lower,
            confidence_upper=prediction_result.prediction.confidence_upper,
            # Kelly analysis  
            kelly_fraction=prediction_result.kelly_fraction,
            expected_value=prediction_result.expected_value,
            recommended_position=prediction_result.position_recommendation.position_size,
            report_timestamp=datetime.now().isoformat(),
            confidence_score=confidence_score
        )
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Market advice report generated successfully[/dim]")
        return report
    
    async def _generate_primary_advice(
        self,
        prediction_result: PredictionResult,
        market_context: Optional[str],
        scenario_results: Optional[str]
    ) -> MarketAdvice:
        """Generate primary market advice."""
        
        advice_input = f"""
        COMPREHENSIVE MARKET ANALYSIS FOR ADVICE GENERATION
        
        Market Question: {prediction_result.market_question}
        
        === 1. RESEARCH FINDINGS ===
        {market_context or "No research context provided"}
        
        === 2. SCENARIO ANALYSIS ===
        {scenario_results or "No scenario analysis provided"}
        
        === 3. PREDICTION METRICS ===
        - Probability Estimate: {prediction_result.prediction.probability:.1%}
        - Confidence Interval: [{prediction_result.prediction.confidence_lower:.1%}, {prediction_result.prediction.confidence_upper:.1%}]
        - Confidence Level: {prediction_result.prediction.confidence_level}
        - Expected Value: {prediction_result.expected_value:.3f} (higher = more profitable)
        - Kelly Fraction: {prediction_result.kelly_fraction:.1%} (optimal bet size)
        - Key Prediction Factors: {', '.join(prediction_result.prediction.key_factors)}
        - Alternative Scenarios: {', '.join(prediction_result.prediction.alternative_scenarios)}
        
        === 4. POSITION RECOMMENDATION (from prediction model) ===
        - Recommended Action: {prediction_result.position_recommendation.action}
        - Suggested Position Size: {prediction_result.position_recommendation.position_size:.1%}
        - Risk Level: {prediction_result.position_recommendation.risk_level}
        - Entry Target: {prediction_result.position_recommendation.entry_price_target or 'Market'}
        - Stop Loss: {prediction_result.position_recommendation.stop_loss or 'Not set'}
        - Take Profit: {prediction_result.position_recommendation.take_profit or 'Not set'}
        
        === 5. IDENTIFIED RISKS ===
        {'; '.join(prediction_result.risk_factors)}
        
        === 6. OVERALL ASSESSMENT ===
        {prediction_result.overall_assessment}
        
        === YOUR DECISION TASK ===
        ALIGN all the above analyses and make ONE FINAL DECISION:
        
        1. Do research findings, scenario analysis, and prediction metrics AGREE or DISAGREE?
        2. If they agree, why does this strengthen your confidence?
        3. If they disagree, which source do you trust most and why?
        4. Based on this alignment, what is your FINAL RECOMMENDATION?
        5. What position size reflects the quality of aligned evidence?
        
        Make a clear, definitive choice - no hedging or "it depends" responses.
        """
        
        result = await Runner.run(self.advice_agent, input=advice_input)
        return result.final_output
    
    async def _generate_risk_assessment(
        self,
        prediction_result: PredictionResult,
        advice: MarketAdvice,
        market_context: Optional[str]
    ) -> RiskAssessment:
        """Generate comprehensive risk assessment."""
        
        risk_input = f"""
        Market Question: {prediction_result.market_question}
        
        Advice Given:
        - Recommendation: {advice.primary_recommendation}
        - Position Size: {advice.recommended_position_size:.1%}
        - Confidence: {advice.confidence_level}
        - Entry Timing: {advice.entry_timing}
        
        Prediction Metrics:
        - Probability: {prediction_result.prediction.probability:.1%}
        - Confidence Interval: [{prediction_result.prediction.confidence_lower:.1%}, {prediction_result.prediction.confidence_upper:.1%}]
        - Expected Value: {prediction_result.expected_value:.3f}
        
        Market Context:
        {market_context or "No market context provided"}
        
        Risk Factors Identified:
        {'; '.join(prediction_result.risk_factors)}
        
        Conduct comprehensive risk assessment for this market advice.
        """
        
        result = await Runner.run(self.risk_agent, input=risk_input)
        return result.final_output
    
    def _calculate_confidence_score(
        self,
        prediction_result: PredictionResult,
        advice: MarketAdvice,
        risk_assessment: RiskAssessment
    ) -> float:
        """Calculate overall confidence score for the advice."""
        
        # Base confidence from prediction
        base_confidence = {"low": 0.3, "medium": 0.6, "high": 0.9}.get(
            prediction_result.prediction.confidence_level, 0.5
        )
        
        # Adjust for advice confidence
        advice_confidence = {"LOW": 0.3, "MEDIUM": 0.6, "HIGH": 0.9}.get(
            advice.confidence_level, 0.5
        )
        
        # Adjust for risk level (higher risk = lower confidence)
        risk_adjustment = {"LOW": 1.0, "MEDIUM": 0.8, "HIGH": 0.6, "EXTREME": 0.3}.get(
            risk_assessment.overall_risk_level, 0.7
        )
        
        # Combine factors
        combined_confidence = (base_confidence + advice_confidence) / 2
        final_confidence = combined_confidence * risk_adjustment
        
        return min(max(final_confidence, 0.1), 0.95)  # Clamp between 10% and 95%
    
    def generate_advice_summary(self, advice_report: MarketAdviceReport) -> str:
        """Generate a concise summary of the market advice."""
        
        summary = f"""
        🎯 MARKET ADVICE SUMMARY
        
        Question: {advice_report.market_question}
        
        💡 RECOMMENDATION: {advice_report.advice.primary_recommendation}
        📊 Probability: {advice_report.primary_probability:.1%}
        💰 Position Size: {advice_report.advice.recommended_position_size:.1%}
        ⏰ Timing: {advice_report.advice.entry_timing}
        🎚️ Confidence: {advice_report.advice.confidence_level} ({advice_report.confidence_score:.1%})
        
        ⚠️ RISK ASSESSMENT: {advice_report.risk_assessment.overall_risk_level}
        🔄 Analysis Alignment: {advice_report.advice.analysis_alignment}
        
        📈 Exit Strategy: {advice_report.advice.exit_strategy}
        
        💭 Decision Reasoning: {advice_report.advice.reasoning[:200]}...
        """
        
        return summary


async def main():
    """Test the Advice Agent."""
    
    # Mock prediction result for testing - imports already handled above
    
    sample_prediction = PredictionEstimate(
        probability=0.72,
        confidence_lower=0.65,
        confidence_upper=0.79,
        confidence_level="high",
        reasoning="Strong institutional adoption and technical momentum",
        key_factors=["Institutional adoption", "Technical momentum", "Regulatory clarity"],
        time_horizon="medium-term",
        alternative_scenarios=["Regulatory crackdown", "Market correction"]
    )
    
    sample_position = PositionRecommendation(
        action="BUY_YES",
        position_size=0.15,
        max_exposure=150.0,
        entry_price_target=0.35,
        stop_loss=0.25,
        take_profit=0.85,
        reasoning="Positive expected value with good risk/reward ratio",
        risk_level="medium"
    )
    
    sample_prediction_result = PredictionResult(
        market_question="Will Bitcoin reach $100,000 by end of 2024?",
        prediction=sample_prediction,
        position_recommendation=sample_position,
        overall_assessment="High confidence bullish prediction with positive expected value",
        risk_factors=["Market volatility", "Regulatory uncertainty"],
        expected_value=0.25,
        kelly_fraction=0.15
    )
    
    advice_agent = AdviceAgent()
    
    advice_report = await advice_agent.generate_market_advice(sample_prediction_result)
    
    # Generate summary
    summary = advice_agent.generate_advice_summary(advice_report)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())