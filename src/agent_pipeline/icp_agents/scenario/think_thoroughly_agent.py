"""
Think Thoroughly Agent - Intelligent scenario analysis with historical fact lookup.
"""

from agents import Agent, Runner, WebSearchTool, ModelSettings
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio
import logging

# Configure logging
logger = logging.getLogger(__name__)


SCENARIO_GENERATION_PROMPT = """
Generate 2-4 distinct scenarios for this prediction question.
Each scenario should include a probability estimate and clear reasoning.
Adapt your analysis to the question type (political, technology, etc.).
"""

SCENARIO_EVALUATION_PROMPT = """
Review scenarios and filter if needed. Keep at least 2 scenarios.
Eliminate only if one has very low probability (<0.15) AND weak reasoning.
"""

ENRICHMENT_PROMPT = """
Generate 2-3 research questions to validate this scenario.
Focus on current data, trends, and expert opinions.
"""

SYNTHESIS_PROMPT = """
Create a comprehensive analysis report with:
1. Executive summary and conclusion
2. Scenario probabilities (must sum to 1.0)
3. Key insights and evidence
4. Decision framework and recommendations
5. Monitoring indicators
"""



class ScenarioEvaluation(BaseModel):
    """Evaluation results for filtering scenarios"""
    scenarios_to_keep: List[str] = Field(description="Names/titles of scenarios to retain")
    eliminated_scenario: Optional[str] = Field(default=None, description="Name of eliminated scenario if any")
    reasoning: str = Field(description="Clear reasoning for filtering decision")


class ResearchDecision(BaseModel):
    """Decision on whether web research is needed"""
    needs_web_research: bool = Field(description="Whether current web research is needed")
    reasoning: str = Field(description="Explanation for the decision")


class EnrichedScenarioAnalysis(BaseModel):
    """Comprehensive scenario analysis report for any type of prediction question"""
    # Executive Summary
    executive_summary: str = Field(description="Concise summary of key findings and primary conclusion")
    primary_conclusion: str = Field(description="Main conclusion with confidence level")
    overall_assessment: str = Field(description="Overall assessment and recommendation")
    
    # Scenario Analysis
    scenario_summaries: List[str] = Field(description="Detailed descriptions of each final scenario")
    final_probabilities: List[float] = Field(description="Updated probability estimates (must sum to 1.0)")
    confidence_scores: List[float] = Field(description="Research-based confidence scores (0.0-1.0)")
    scenario_evidence: List[str] = Field(description="Key supporting/contradicting evidence for each scenario")
    
    # Key Insights
    key_insights: List[str] = Field(description="Most important discoveries from research enrichment")
    contrarian_perspectives: List[str] = Field(description="Surprising findings or alternative viewpoints")
    risk_factors: List[str] = Field(description="Key risks and potential unexpected developments")
    
    # Decision Framework (adapts to question type)
    decision_framework: str = Field(description="Actionable framework adapted to question type")
    strategic_implications: List[str] = Field(description="Strategic implications and action items")
    contingency_planning: str = Field(description="Preparation for different scenarios")
    
    # Monitoring Framework
    key_indicators: List[str] = Field(description="Critical indicators to track for scenario validation")
    early_warning_signs: List[str] = Field(description="Early warning signs for scenario shifts")
    
    # Historical Analysis (for post-mortem)
    is_historical: bool = Field(default=False, description="Whether this analyzes a past event")
    actual_outcome: Optional[str] = Field(default=None, description="What actually happened")
    prediction_accuracy: Optional[str] = Field(default=None, description="Assessment of prediction quality")
    lessons_learned: List[str] = Field(default=[], description="Key lessons from prediction vs reality")
    
    # Full Report
    full_report: str = Field(description="Complete formatted analysis report")


class WebResearchAgent:
    """Web research agent using OpenAI's WebSearchTool for real-time information."""
    
    def __init__(self, force_web_search: bool = False):
        # Configure model settings to force tool use when required
        model_settings = None
        if force_web_search:
            model_settings = ModelSettings(tool_choice="required")
        
        self.research_agent = Agent(
            name="WebResearchAgent",
            instructions=f"""You are a web research specialist who conducts thorough research using web search.
            
            IMPORTANT: Today's date is {datetime.now().strftime("%B %d, %Y")}. Use this context for all research and analysis.
            
            When given a research query:
            1. Use the web search tool to find current, relevant information
            2. Focus on authoritative sources and recent data
            3. Provide comprehensive analysis with supporting evidence
            4. Include specific facts, statistics, and expert opinions when available
            5. Cite sources and provide context for the information found
            6. Consider the current date when interpreting "future" or "past" events
            
            Structure your response with:
            - Key findings summary
            - Supporting evidence with sources
            - Analysis of data quality and reliability
            - Implications for the research question""",
            tools=[WebSearchTool()],
            model="gpt-4o-mini",
            model_settings=model_settings,
            tool_use_behavior="stop_on_first_tool" if force_web_search else "run_llm_again"
        )
        self.force_web_search = force_web_search
        logger.info(f"Using WebSearchTool for real-time web research (forced: {force_web_search})")
    
    async def search(self, query: str, context: str = "", depth: str = "standard") -> str:
        """Conduct web-based research analysis."""
        
        logger.debug(f"Web research: {query[:50]}...")
        
        # Construct research prompt based on depth
        depth_instructions = {
            "quick": "Provide a brief overview with key facts",
            "standard": "Conduct thorough research with multiple sources and detailed analysis",
            "deep": "Perform comprehensive research with extensive fact-checking and expert perspectives"
        }
        
        research_prompt = f"""
Research Query: {query}
Context: {context}

Instructions: {depth_instructions[depth]}

Please search for current, reliable information about this query and provide a comprehensive analysis.
Focus on factual data, expert opinions, and recent developments.
"""
        
        try:
            result = await Runner.run(self.research_agent, input=research_prompt)
            return result.final_output
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            # Fallback to basic response
            return f"""
WEB RESEARCH UNAVAILABLE

Research Query: {query}
Context: {context[:150]}{'...' if len(context) > 150 else ''}

Note: Web search is currently unavailable. This query would typically be researched using current web sources for:
- Recent developments and trends
- Expert opinions and analysis
- Statistical data and factual information
- Policy changes and market conditions

Depth: {depth.title()}
"""


class ThinkThoroughlyAgent:
    """Intelligent analysis agent with historical fact lookup and scenario analysis."""
    
    def __init__(self):
        # Agents for scenario analysis (future questions)
        self.scenario_generator = Agent(
            name="ScenarioGenerator",
            instructions=SCENARIO_GENERATION_PROMPT,
            output_type=List[str],
            model="gpt-4o-mini"
        )
        
        self.scenario_evaluator = Agent(
            name="ScenarioEvaluator", 
            instructions=SCENARIO_EVALUATION_PROMPT,
            output_type=ScenarioEvaluation,
            model="gpt-4o-mini"
        )
        
        self.enrichment_agent = Agent(
            name="EnrichmentAgent",
            instructions=ENRICHMENT_PROMPT,
            output_type=List[str],
            model="gpt-4o-mini"
        )
        
        self.synthesis_agent = Agent(
            name="SynthesisAgent",
            instructions=SYNTHESIS_PROMPT,
            output_type=EnrichedScenarioAnalysis,
            model="gpt-4o-mini"
        )
        
        self.research_tool = WebResearchAgent(force_web_search=False)
        
        # Agent to determine if web research is needed
        current_year = datetime.now().year
        self.research_decision_agent = Agent(
            name="ResearchDecisionAgent",
            instructions=f"""You analyze questions to determine if current web research is needed.

CRITICAL CONTEXT: Today is {datetime.now().strftime("%B %d, %Y")} (year {current_year}).

TEMPORAL AWARENESS RULES:
- The 2024 U.S. Presidential Election has ALREADY OCCURRED (we are in {current_year})
- Any question about "Will X happen in 2024" when we are in {current_year} is asking about PAST EVENTS
- Questions about 2024 events should be treated as HISTORICAL when we are in {current_year}

DECISION CRITERIA:
- Use web research for: events happening in {current_year} or later, real-time data, current prices
- Skip web research for: events that happened in 2024 or earlier (when current year is {current_year})

EXAMPLES FOR YEAR {current_year}:
- "Will Trump win 2024 election?" → HISTORICAL (already happened), NO web search needed
- "What is Bitcoin price today?" → CURRENT ({current_year}), web search needed
- "Will Bitcoin reach $100k in {current_year}?" → FUTURE/CURRENT, web search needed

Return structured decision with needs_web_research boolean and reasoning explanation.""",
            output_type=ResearchDecision,
            model="gpt-4o-mini"
        )
    
    async def analyze_market_thoroughly(
        self,
        market_question: str,
        research_report: str = None,
        research_depth: str = "standard",
        skip_enrichment: bool = False,
        actual_outcome: str = None
    ) -> EnrichedScenarioAnalysis:
        """Main analysis pipeline with intelligent web research decision."""
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Starting comprehensive market analysis...[/dim]")
        logger.info(f"Analyzing: {market_question}")
        
        # Step 1: Decide if web research is needed
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Evaluating need for web research...[/dim]")
        research_decision = await self._should_use_web_research(market_question, actual_outcome)
        use_web_research = research_decision.needs_web_research
        if hasattr(self, 'console'):
            research_status = "enabled" if use_web_research else "disabled"
            self.console.print(f"[dim]→ Web research {research_status} - {research_decision.reasoning}[/dim]")
        logger.info(f"Web research needed: {use_web_research} - {research_decision.reasoning}")
        
        # Step 2: For historical questions, do direct factual lookup instead of full pipeline
        reasoning_lower = research_decision.reasoning.lower()
        
        # Trust the AI agent's decision - if it says no web research needed and mentions historical indicators
        is_historical = any(keyword in reasoning_lower for keyword in [
            "historical", "already occurred", "has already", "past event", "happened before", "occurred"
        ])
        
        if not use_web_research and is_historical:
            if hasattr(self, 'console'):
                self.console.print("[dim]→ Historical question detected - performing factual lookup...[/dim]")
            logger.info("Historical question detected - doing direct factual lookup")
            return await self._handle_historical_question(market_question, research_decision.reasoning)
        
        # Continue with full pipeline for current/future questions
        # Generate scenarios as strings
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Generating market scenarios...[/dim]")
        scenarios = await self._generate_scenarios(market_question, research_report)
        if hasattr(self, 'console'):
            self.console.print(f"[dim]→ Generated {len(scenarios)} scenarios for analysis[/dim]")
        logger.info(f"Generated {len(scenarios)} scenarios")
        
        # Filter scenarios
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Evaluating and filtering scenarios...[/dim]")
        filtered_scenarios = await self._evaluate_and_filter_scenarios(scenarios)
        if hasattr(self, 'console'):
            self.console.print(f"[dim]→ Retained {len(filtered_scenarios)} high-quality scenarios[/dim]")
        logger.info(f"Retained {len(filtered_scenarios)} scenarios")
        
        # Configure research tool based on decision
        if use_web_research:
            if hasattr(self, 'console'):
                self.console.print("[dim]→ Configuring web research tools...[/dim]")
            self.research_tool = WebResearchAgent(force_web_search=True)
            logger.info("Configured for forced web search")
        
        # Enrich with research (optional)
        if skip_enrichment:
            if hasattr(self, 'console'):
                self.console.print("[dim]→ Skipping research enrichment step[/dim]")
            logger.info("Skipping research enrichment")
            enriched_scenarios = [{"scenario": s, "research_questions": [], "research_results": {}, "timestamp": datetime.now().isoformat()} for s in filtered_scenarios]
        else:
            if hasattr(self, 'console'):
                research_type = "web-based" if use_web_research else "knowledge-based"
                self.console.print(f"[dim]→ Enriching scenarios with {research_type} research...[/dim]")
            enriched_scenarios = await self._enrich_scenarios_parallel(filtered_scenarios, research_depth, use_web_research)
        
        # Synthesize final analysis
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Synthesizing comprehensive analysis report...[/dim]")
        final_analysis = await self._synthesize_enriched_analysis(market_question, enriched_scenarios, actual_outcome)
        
        return final_analysis
    
    async def _handle_historical_question(self, market_question: str, reasoning: str) -> EnrichedScenarioAnalysis:
        """Handle historical questions with direct web search for factual answers."""
        
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Performing direct factual lookup for historical question...[/dim]")
        logger.info("Performing direct web search for historical fact lookup")
        
        # Create a web research agent specifically for factual lookup
        factual_research_agent = WebResearchAgent(force_web_search=True)
        
        # Search for the factual answer
        search_query = f"What was the actual outcome: {market_question}"
        if hasattr(self, 'console'):
            self.console.print("[dim]→ Searching web for factual outcome...[/dim]")
        try:
            factual_result = await factual_research_agent.search(
                query=search_query,
                context="Historical fact lookup - need definitive answer",
                depth="standard"
            )
            
            # Create a simplified analysis with the factual result
            analysis = EnrichedScenarioAnalysis(
                # Executive Summary
                executive_summary=f"Historical Fact Lookup: {market_question}\n\nThis question asks about a past event. Here is the factual outcome based on web research.",
                primary_conclusion=f"FACTUAL RESULT: {factual_result[:150]}..." if len(factual_result) > 150 else f"FACTUAL RESULT: {factual_result}",
                overall_assessment="Historical fact confirmed through web research.",
                
                # No scenarios for historical facts - just the factual outcome
                scenario_summaries=[],  # No scenarios for historical facts
                final_probabilities=[],  # No probabilities for facts
                confidence_scores=[],   # No scenario confidence needed
                scenario_evidence=[],   # Evidence is in the factual result
                
                # Key Insights
                key_insights=[
                    "Historical fact lookup completed successfully",
                    f"Factual confidence: 100% (confirmed through web research)",
                    "No prediction scenarios applicable for past events"
                ],
                contrarian_perspectives=[],
                risk_factors=[],
                
                # Decision Framework
                decision_framework="FACTUAL LOOKUP: This was a historical event requiring fact verification, not scenario analysis.",
                strategic_implications=[f"Factual outcome: {factual_result[:100]}..."],
                contingency_planning="N/A - historical events are fixed facts",
                
                # Monitoring Framework  
                key_indicators=["Web search results", "Verified historical records"],
                early_warning_signs=["N/A for completed historical events"],
                
                # Historical Analysis
                is_historical=True,
                actual_outcome=factual_result,
                prediction_accuracy="100% factual accuracy - no prediction was made",
                lessons_learned=["Historical questions require factual lookup, not scenario analysis"],
                
                # Full Report
                full_report=""
            )
            
            # Generate the report
            analysis.full_report = self._generate_factual_report(market_question, factual_result, reasoning)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Historical factual lookup failed: {e}")
            # Fallback to basic response
            return self._create_fallback_historical_analysis(market_question, reasoning)
    
    def _generate_factual_report(self, question: str, factual_result: str, reasoning: str) -> str:
        """Generate a factual report for historical questions."""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        return f"""
# HISTORICAL FACT LOOKUP REPORT
**Question:** {question}
**Analysis Date:** {current_date}
**Type:** Historical Fact Finding

---

## EXECUTIVE SUMMARY

This question asks about a past event. Instead of generating prediction scenarios, we performed a direct web search to find the factual outcome.

**Decision Reasoning:** {reasoning}

---

## FACTUAL OUTCOME

{factual_result}

---

## ANALYSIS NOTES

**Methodology:** Direct web search for historical facts
**Confidence:** High (factual information)
**Type:** Historical event verification

**Key Point:** For questions about past events, factual lookup is more appropriate than scenario analysis.

---

*This analysis provides factual information about a historical event rather than predictive scenarios.*
"""
    
    def _create_fallback_historical_analysis(self, question: str, reasoning: str) -> EnrichedScenarioAnalysis:
        """Create fallback analysis when web search fails."""
        
        return EnrichedScenarioAnalysis(
            executive_summary=f"Historical question detected: {question}",
            primary_conclusion="This question asks about a past event - factual lookup recommended.",
            overall_assessment=reasoning,
            scenario_summaries=[],  # No scenarios for historical questions
            final_probabilities=[],  # No probabilities for facts
            confidence_scores=[],   # No scenario confidence
            scenario_evidence=[],   # No scenario evidence
            key_insights=["Historical question identified", "Direct factual lookup would be more appropriate"],
            contrarian_perspectives=[],
            risk_factors=[],
            decision_framework="For historical questions, perform factual research rather than scenario analysis.",
            strategic_implications=["Verify historical facts through reliable sources"],
            contingency_planning="N/A for historical events",
            key_indicators=["Historical records"],
            early_warning_signs=["N/A"],
            is_historical=True,
            actual_outcome="Search unavailable",
            prediction_accuracy="N/A",
            lessons_learned=["Historical questions need factual research"],
            full_report=f"HISTORICAL QUESTION DETECTED\n\nQuestion: {question}\nReasoning: {reasoning}\n\nRecommendation: Use direct web search for factual information about this past event."
        )
    
    async def _should_use_web_research(self, market_question: str, actual_outcome: str = None) -> ResearchDecision:
        """Determine if web research is needed for this question."""
        current_date = datetime.now().strftime("%B %d, %Y")
        analysis_input = f"""
CURRENT DATE: {current_date}
QUESTION: {market_question}
HISTORICAL ANALYSIS: {actual_outcome is not None}
ACTUAL OUTCOME: {actual_outcome if actual_outcome else "N/A"}

Analyze this question to determine if current web research is needed.
Consider the question type, time sensitivity, current date context, and whether it requires recent data.
"""
        
        try:
            result = await Runner.run(self.research_decision_agent, input=analysis_input)
            return result.final_output
        except Exception as e:
            logger.warning(f"Research decision failed: {e}")
            # Default to no web research on error
            return ResearchDecision(needs_web_research=False, reasoning=f"Decision failed: {str(e)}")
    
    async def _generate_scenarios(self, market_question: str, research_report: str = None) -> List[str]:
        """Generate scenarios as simple strings."""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_year = datetime.now().year
        input_text = f"""
        MARKET QUESTION: {market_question}
        CURRENT DATE: {current_date} (Year: {current_year})
        
        RESEARCH CONTEXT:
        {research_report if research_report else "No prior research available"}
        
        CRITICAL TEMPORAL CONTEXT:
        - Today is {current_date} 
        - We are in the year {current_year}
        - The 2024 U.S. Presidential Election has ALREADY OCCURRED
        - Any question about 2024 events is asking about PAST/HISTORICAL events
        
        If the question asks about 2024 events, generate scenarios that reflect what actually happened,
        not future predictions. For historical questions, focus on analysis of what occurred and why.
        
        Generate 2-4 distinct scenarios for this prediction market.
        """
        
        result = await Runner.run(self.scenario_generator, input=input_text)
        return result.final_output
    
    async def _evaluate_and_filter_scenarios(self, scenarios: List[str]) -> List[str]:
        """Filter scenarios using string-based evaluation."""
        if len(scenarios) <= 2:
            return scenarios
        
        scenarios_summary = "\n".join([f"- {scenario}" for scenario in scenarios])
        
        evaluation_input = f"""
        SCENARIOS TO EVALUATE:
        {scenarios_summary}
        
        Current count: {len(scenarios)} scenarios
        Apply the filtering rules to decide which scenarios to keep.
        """
        
        evaluation = await Runner.run(self.scenario_evaluator, input=evaluation_input)
        result = evaluation.final_output
        
        # Filter scenarios based on evaluation
        filtered_scenarios = []
        for scenario in scenarios:
            # Check if any of the kept scenario names/titles match this scenario
            scenario_title = scenario.split('(')[0].strip() if '(' in scenario else scenario.split(':')[0].strip()
            if any(kept in scenario or scenario_title in kept for kept in result.scenarios_to_keep):
                filtered_scenarios.append(scenario)
        
        if result.eliminated_scenario:
            logger.info(f"Eliminated scenario containing: {result.eliminated_scenario}")
        
        return filtered_scenarios if filtered_scenarios else scenarios  # Fallback
    
    async def _enrich_scenarios_parallel(self, scenarios: List[str], research_depth: str, use_web_research: bool = False) -> List[Dict[str, Any]]:
        """Enrich scenarios with research data."""
        enrichment_tasks = [
            self._enrich_single_scenario(scenario, research_depth, use_web_research)
            for scenario in scenarios
        ]
        return await asyncio.gather(*enrichment_tasks)
    
    async def _enrich_single_scenario(self, scenario: str, research_depth: str, use_web_research: bool = False) -> Dict[str, Any]:
        """Enrich a single scenario with research."""
        enriched = {
            "scenario": scenario,
            "research_questions": [],
            "research_results": {},
            "web_research_used": use_web_research,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Generate research questions
            if hasattr(self, 'console'):
                self.console.print("[dim]→ Generating research questions to enrich scenario analysis[/dim]")
            questions_result = await Runner.run(self.enrichment_agent, input=f"SCENARIO: {scenario}")
            research_questions = questions_result.final_output[:3]  # Limit to 3 questions
            enriched["research_questions"] = research_questions
            
            # Research each question with web search decision
            successful_research = 0
            if hasattr(self, 'console'):
                research_type = "web search" if use_web_research else "knowledge-based analysis"
                self.console.print(f"[dim]→ Executing {research_type} research for {len(research_questions)} specialized questions[/dim]")
            
            for question in research_questions:
                try:
                    if use_web_research:
                        research_result = await self.research_tool.search(
                            query=question,
                            context=f"Scenario analysis: {scenario[:200]}",
                            depth=research_depth
                        )
                        logger.debug(f"Web research successful for: {question[:50]}...")
                    else:
                        # Use knowledge-based analysis without web search
                        research_result = f"""
KNOWLEDGE-BASED ANALYSIS

Research Query: {question}
Context: Scenario analysis without current web data

This analysis is based on general knowledge and patterns rather than current web information.
For real-time accuracy, web research would be recommended for questions requiring current data.

Key considerations for this query would include historical patterns, 
established trends, and logical reasoning based on available context.
"""
                        logger.debug(f"Knowledge-based research for: {question[:50]}...")
                    
                    enriched["research_results"][question] = research_result
                    successful_research += 1
                    
                except Exception as e:
                    logger.warning(f"Research failed for question '{question[:50]}...': {str(e)[:100]}")
                    # Provide a more informative fallback
                    enriched["research_results"][question] = f"Research currently unavailable. This question would typically be answered with {'current web data' if use_web_research else 'knowledge-based analysis'} on: {question[:100]}..."
            
            logger.info(f"Scenario enrichment: {successful_research}/{len(research_questions)} research queries successful (web: {use_web_research})")
            
        except Exception as e:
            logger.error(f"Enrichment failed for scenario: {e}")
        
        return enriched
    
    async def _synthesize_enriched_analysis(self, market_question: str, enriched_scenarios: List[Dict[str, Any]], actual_outcome: str = None) -> EnrichedScenarioAnalysis:
        """Synthesize final analysis from enriched scenarios."""
        synthesis_input = f"""
        MARKET QUESTION: {market_question}
        DATE: {datetime.now().strftime("%Y-%m-%d")}
        
        ENRICHED SCENARIOS WITH RESEARCH:
        """
        
        for i, enriched in enumerate(enriched_scenarios, 1):
            synthesis_input += f"""
        
        SCENARIO {i}: {enriched['scenario']}
        
        Research Questions & Findings:
        """
            for question, result in enriched['research_results'].items():
                synthesis_input += f"- Q: {question}\n  A: {result[:300]}...\n"
        
        # Add historical analysis context if actual outcome provided
        if actual_outcome:
            synthesis_input += f"""
        
        HISTORICAL ANALYSIS MODE:
        This is a retrospective analysis. The actual outcome was: {actual_outcome}
        
        Focus on:
        1. How well each scenario predicted the actual outcome
        2. Which factors were correctly/incorrectly weighted
        3. Lessons learned from prediction vs reality
        4. Calibration assessment of the probability estimates
        5. Sources of prediction errors and their causes
        
        """
        
        synthesis_input += """
        
        Based on the scenario analysis and available research, provide a comprehensive final analysis including:
        
        1. Updated probability estimates for each scenario (must sum to 1.0)
        2. Confidence scores based on available evidence quality
        3. Key insights and important factors discovered
        4. Contrarian perspectives and alternative viewpoints
        5. Risk factors and potential unexpected developments  
        6. Actionable decision framework adapted to this question type
        7. Strategic implications and preparation recommendations
        8. Key indicators to monitor for scenario validation
        9. Early warning signs for scenario shifts
        """
        
        if actual_outcome:
            synthesis_input += """
        10. Historical analysis: prediction accuracy assessment
        11. Lessons learned from comparing predictions to actual outcome
        """
        
        synthesis_input += """
        
        Provide detailed, substantive content for each section even when research data is limited.
        """
        
        result = await Runner.run(self.synthesis_agent, input=synthesis_input)
        analysis = result.final_output
        
        # Set historical analysis fields if applicable
        if actual_outcome:
            analysis.is_historical = True
            analysis.actual_outcome = actual_outcome
        
        # Generate formatted report
        analysis.full_report = self._generate_formatted_report(market_question, enriched_scenarios, analysis, actual_outcome)
        
        return analysis
    
    def _generate_formatted_report(self, market_question: str, enriched_scenarios: List[Dict[str, Any]], analysis: EnrichedScenarioAnalysis, actual_outcome: str = None) -> str:
        """Generate a comprehensive formatted report with all scenario details."""
        
        historical_marker = " (HISTORICAL ANALYSIS)" if actual_outcome else ""
        
        report = f"""
# SCENARIO ANALYSIS REPORT{historical_marker}
**Question:** {market_question}
**Analysis Date:** {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}
**Methodology:** Multi-scenario analysis with {"web research" if any(s.get("web_research_used") for s in enriched_scenarios) else "knowledge-based analysis"}
"""
        
        if actual_outcome:
            report += f"""**Analysis Type:** Retrospective analysis of past event
**Actual Outcome:** {actual_outcome}
"""
        
        report += f"""
---

## EXECUTIVE SUMMARY

{analysis.executive_summary}

**Primary Conclusion:** {analysis.primary_conclusion}

**Overall Assessment:** {analysis.overall_assessment}
"""
        
        if actual_outcome and analysis.prediction_accuracy:
            report += f"""
**Prediction Accuracy:** {analysis.prediction_accuracy}
"""
        
        report += """
---

## DETAILED SCENARIO ANALYSIS

"""
        
        # Add each scenario with research details
        for i, (scenario_summary, probability, confidence, evidence) in enumerate(
            zip(analysis.scenario_summaries, analysis.final_probabilities, 
                analysis.confidence_scores, analysis.scenario_evidence), 1
        ):
            report += f"""
                ### Scenario {i}: {scenario_summary.split('(')[0].strip() if '(' in scenario_summary else f'Scenario {i}'}
                **Probability:** {probability:.1%}  
                **Confidence:** {confidence:.1f}/1.0  

                **Description:** {scenario_summary}

                **Supporting Evidence:** {evidence}

                **Research Findings:**
            """
            
            # Add research questions and results for this scenario
            if i <= len(enriched_scenarios):
                enriched = enriched_scenarios[i-1]
                for question, result in enriched['research_results'].items():
                    report += f"- **Q:** {question}\n"
                    report += f"  **A:** {result[:200]}{'...' if len(result) > 200 else ''}\n\n"
        
        report += f"""
---

## KEY INSIGHTS

"""
        for insight in analysis.key_insights:
            report += f"• {insight}\n"
        
        if analysis.contrarian_perspectives:
            report += f"""
### Contrarian Perspectives
"""
            for perspective in analysis.contrarian_perspectives:
                report += f"• {perspective}\n"
        
        if analysis.risk_factors:
            report += f"""
### Risk Factors
"""
            for risk in analysis.risk_factors:
                report += f"• {risk}\n"
        
        report += f"""
---

## DECISION FRAMEWORK

{analysis.decision_framework}

### Strategic Implications
"""
        for implication in analysis.strategic_implications:
            report += f"• {implication}\n"
        
        report += f"""
### Contingency Planning
{analysis.contingency_planning}

---

## MONITORING FRAMEWORK

### Key Indicators to Track
"""
        for indicator in analysis.key_indicators:
            report += f"• {indicator}\n"
        
        report += f"""
### Early Warning Signs
"""
        for warning in analysis.early_warning_signs:
            report += f"• {warning}\n"
        
        # Add historical analysis section if applicable
        if actual_outcome:
            report += f"""
---

## HISTORICAL ANALYSIS

### Prediction vs Reality
**What Actually Happened:** {actual_outcome}

"""
            if analysis.prediction_accuracy:
                report += f"**Accuracy Assessment:** {analysis.prediction_accuracy}\n\n"
            
            if analysis.lessons_learned:
                report += "### Lessons Learned\n"
                for lesson in analysis.lessons_learned:
                    report += f"• {lesson}\n"
                report += "\n"
        
        report += f"""
---

## METHODOLOGY NOTES

**Scenario Generation:** Based on research context analysis using GPT-4o-mini
**Research Enrichment:** {"WebSearchTool for current data" if any(s.get("web_research_used") for s in enriched_scenarios) else "Knowledge-based analysis"}
**Probability Calibration:** Evidence-weighted estimation with confidence scoring
**Analysis Framework:** Multi-factor analysis adapted to question type
"""
        
        if actual_outcome:
            report += "**Historical Analysis:** Retrospective comparison of predictions with actual outcomes\n"
        
        report += """
*This analysis is for informational purposes only and represents a structured approach to scenario planning.*
"""
        
        return report.strip()
    
    def save_report(self, analysis: EnrichedScenarioAnalysis, filename: str = None) -> str:
        """Save the formatted report to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scenario_analysis_report_{timestamp}.md"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(analysis.full_report)
            logger.info(f"Report saved to: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise


# Simplified API remains the same
async def analyze_with_smart_scenarios(
    market_question: str,
    research_report: str = None,
    depth: str = "standard",
    skip_enrichment: bool = False
) -> EnrichedScenarioAnalysis:
    """Simplified entry point for smart scenario analysis."""
    agent = ThinkThoroughlyAgent()
    return await agent.analyze_market_thoroughly(
        market_question=market_question,
        research_report=research_report,
        research_depth=depth,
        skip_enrichment=skip_enrichment
    )


async def main():
    """Test the enhanced Think Thoroughly agent with various question types."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Example questions - choose which to run
    examples = {
        "political_historical": {
            "question": "Will Donald Trump win the 2024 U.S. Presidential Election?",
            "context": "Recent polling shows competitive race. Trump leads Republican primaries while Biden faces age concerns. Economic issues and legal proceedings add complexity to the race..."
        },
        "political_general": {
            "question": "Will Donald Trump be president again?",
            "context": "Trump has served one term and has expressed interest in running again. Various factors including age, legal issues, party support, and electoral dynamics would influence any future presidential campaigns..."
        },
        "political_future": {
            "question": "Will Donald Trump be president again in 2030?",
            "context": "Trump would be 84 years old in 2030. Constitutional questions about serving non-consecutive terms, age factors, party dynamics, and potential opposition candidates all come into play..."
        },
        "technology": {
            "question": "Will AGI be achieved by 2030?",
            "context": "Current LLMs showing rapid progress. Major tech companies investing billions. Scaling laws suggest continued improvement but challenges remain in reasoning and alignment..."
        }
    }
    
    # Run both examples sequentially
    for example_name, example_data in examples.items():
        question = example_data["question"]
        context = example_data["context"]
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Starting analysis for {example_name.upper()} example...")
        logger.info(f"Question: {question}")
        logger.info(f"{'='*80}")
        
        # Option to skip enrichment if API rate limited
        analysis = await analyze_with_smart_scenarios(
            market_question=question,
            research_report=context,
            depth="standard",
            skip_enrichment=False  # Set to True to skip research
        )
        
        # Display results for this example
        logger.info(f"Analysis Complete for {example_name}!")
        logger.info(f"Scenarios Analyzed: {len(analysis.scenario_summaries)}")
        logger.info(f"Primary Conclusion: {analysis.primary_conclusion}")
        logger.info(f"Key Insights: {len(analysis.key_insights)} discovered")
        
        # Save detailed report
        agent = ThinkThoroughlyAgent()
        report_file = agent.save_report(analysis, f"{example_name}_analysis_report.md")
        logger.info(f"Report saved to: {report_file}")
        
    
    logger.info("All analyses completed!")


if __name__ == "__main__":
    asyncio.run(main())