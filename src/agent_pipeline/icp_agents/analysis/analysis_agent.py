from agents import Agent, Runner
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel


ANALYSIS_PROMPT = """
You are an expert market analyst that extracts actionable insights from research reports.
Your task is to analyze research reports and identify key factors that could influence prediction markets.

ANALYSIS REQUIREMENTS:
- Extract key market drivers and catalysts
- Identify quantitative data points and trends
- Assess sentiment and market momentum
- Highlight risks and uncertainties
- Provide confidence levels for each insight
- Focus on factors that affect probability outcomes

OUTPUT STRUCTURE:
- Key Insights: Most important findings that affect market outcomes
- Supporting Data: Quantitative evidence and statistics
- Risk Factors: Potential threats or uncertainties
- Market Sentiment: Overall sentiment and momentum
- Confidence Assessment: How reliable each insight is
- Time Sensitivity: Which insights are time-critical

Focus on extracting insights that can be converted into tradable probabilities.
"""

INSIGHT_EXTRACTION_PROMPT = """
You are a signal extraction specialist. Analyze the research findings and extract specific tradable signals.

For each insight, provide:
1. Signal Type: (bullish/bearish/neutral)
2. Strength: (weak/moderate/strong)
3. Time Horizon: (short-term/medium-term/long-term)
4. Confidence: (low/medium/high)
5. Key Evidence: Supporting facts
6. Risk Factors: Potential downsides

Focus on signals that directly impact market probabilities.
Return structured insights that can be quantified.
"""


class MarketInsight(BaseModel):
    signal_type: str  # bullish, bearish, neutral
    strength: str     # weak, moderate, strong
    time_horizon: str # short-term, medium-term, long-term
    confidence: str   # low, medium, high
    evidence: str     # Supporting facts
    risk_factors: str # Potential downsides
    impact_score: float # 0-1 scale


class AnalysisResult(BaseModel):
    market_insights: List[MarketInsight]
    overall_sentiment: str
    key_drivers: List[str]
    risk_assessment: str
    confidence_level: str
    analysis_summary: str


class AnalysisAgent:
    """Agent that analyzes research reports and extracts tradable insights."""
    
    def __init__(self):
        self.analysis_agent = Agent(
            name="MarketAnalysisAgent",
            instructions=ANALYSIS_PROMPT,
            model="gpt-4o-mini"
        )
        
        self.insight_agent = Agent(
            name="InsightExtractionAgent", 
            instructions=INSIGHT_EXTRACTION_PROMPT,
            output_type=AnalysisResult,
            model="gpt-4o-mini"
        )
    
    async def analyze_report(self, research_report: str, market_question: str) -> AnalysisResult:
        """
        Analyze a research report and extract tradable insights.
        
        Args:
            research_report: The research report to analyze
            market_question: The specific market question being analyzed
            
        Returns:
            AnalysisResult with extracted insights and signals
        """
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Starting comprehensive analysis of research report[/dim]")
        
        # First pass: General analysis
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Initial analysis phase of collected market data[/dim]")
        analysis_input = f"""
        Market Question: {market_question}
        
        Research Report:
        {research_report}
        
        Current Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        analysis_result = await Runner.run(
            self.analysis_agent,
            input=analysis_input
        )
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Extracting structured market signals and insights[/dim]")
        
        # Second pass: Extract structured insights
        insight_input = f"""
        Market Question: {market_question}
        
        Analysis Results:
        {analysis_result.final_output}
        
        Original Research Report:
        {research_report[:2000]}...  # Truncated for efficiency
        """
        
        insights_result = await Runner.run(
            self.insight_agent,
            input=insight_input
        )
        
        if hasattr(self, 'console'):
            final_result = insights_result.final_output
            num_insights = len(final_result.market_insights) if hasattr(final_result, 'market_insights') else 0
            self.console.print(f"[dim]→ Analysis complete - successfully extracted {num_insights} market insights[/dim]")
        
        return insights_result.final_output
    
    async def quick_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Quick sentiment analysis for market content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Performing rapid sentiment analysis...[/dim]")
        
        sentiment_prompt = """
        Analyze the sentiment of this market-related text.
        Return: BULLISH, BEARISH, or NEUTRAL with confidence score 0-1.
        Also identify key sentiment drivers.
        """
        
        sentiment_agent = Agent(
            name="SentimentAgent",
            instructions=sentiment_prompt,
            model="gpt-4o-mini"
        )
        
        result = await Runner.run(
            sentiment_agent,
            input=f"Text to analyze: {text[:1000]}"
        )
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Processing sentiment classification results...[/dim]")
        
        # Parse the result into structured format
        sentiment_text = result.final_output
        
        # Simple parsing logic (could be enhanced with structured output)
        if "BULLISH" in sentiment_text.upper():
            sentiment = "BULLISH"
        elif "BEARISH" in sentiment_text.upper():
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"
            
        return {
            "sentiment": sentiment,
            "analysis": sentiment_text,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_signal_strength(self, insights: List[MarketInsight]) -> Dict[str, float]:
        """
        Calculate overall signal strength from individual insights.
        
        Args:
            insights: List of market insights
            
        Returns:
            Signal strength metrics
        """
        
        if hasattr(self, 'console'):
            self.console.print(f"[dim]→ Computing signal strength from {len(insights)} market insights...[/dim]")
        
        if not insights:
            if hasattr(self, 'console'):
                self.console.print("[dim]→ No insights available - returning neutral signal strength[/dim]")
            return {"overall_strength": 0.0, "bullish_signals": 0.0, "bearish_signals": 0.0}
        
        bullish_strength = 0.0
        bearish_strength = 0.0
        total_weight = 0.0
        
        strength_weights = {"weak": 0.3, "moderate": 0.6, "strong": 1.0}
        confidence_weights = {"low": 0.5, "medium": 0.75, "high": 1.0}
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Weighting signals by strength and confidence levels...[/dim]")
        
        for insight in insights:
            weight = strength_weights.get(insight.strength, 0.5) * confidence_weights.get(insight.confidence, 0.5)
            total_weight += weight
            
            if insight.signal_type == "bullish":
                bullish_strength += weight * insight.impact_score
            elif insight.signal_type == "bearish":
                bearish_strength += weight * insight.impact_score
        
        if total_weight == 0:
            return {"overall_strength": 0.0, "bullish_signals": 0.0, "bearish_signals": 0.0}
        
        result = {
            "overall_strength": (bullish_strength - bearish_strength) / total_weight,
            "bullish_signals": bullish_strength / total_weight,
            "bearish_signals": bearish_strength / total_weight,
            "total_insights": len(insights),
            "high_confidence_insights": len([i for i in insights if i.confidence == "high"])
        }
        
        if hasattr(self, 'console'):
            overall_direction = "bullish" if result["overall_strength"] > 0 else "bearish" if result["overall_strength"] < 0 else "neutral"
            self.console.print(f"[dim]→ Signal strength analysis complete - overall trend: {overall_direction}[/dim]")
        
        return result


async def main():
    """Test the analysis agent"""
    
    # Sample research report
    sample_report = """
    # Bitcoin Market Analysis Report
    
    ## Executive Summary
    Recent analysis indicates strong institutional adoption with BlackRock ETF seeing $2B inflows.
    Technical indicators show bullish momentum above $45k resistance level.
    
    ## Key Findings
    - Institutional demand increasing 300% QoQ
    - Mining difficulty at all-time high
    - Regulatory clarity improving in major markets
    - Correlation with traditional assets decreasing
    
    ## Risk Factors
    - Potential Federal Reserve rate changes
    - Regulatory uncertainty in some jurisdictions
    - Market volatility remains elevated
    """
    
    market_question = "Will Bitcoin reach $100,000 by end of 2024?"
    
    analysis_agent = AnalysisAgent()
    
    # Utiliser la console partagée pour feedback utilisateur
    if hasattr(analysis_agent, 'console'):
        analysis_agent.console.print("[dim]→ Analyzing research report...[/dim]")
    result = await analysis_agent.analyze_report(sample_report, market_question)
    
    # Calculate signal strength
    signal_metrics = analysis_agent.calculate_signal_strength(result.market_insights)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())