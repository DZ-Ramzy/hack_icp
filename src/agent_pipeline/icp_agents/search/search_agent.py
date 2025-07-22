from agents import Agent, function_tool, Runner, trace
from datetime import datetime
from typing import List
from pydantic import BaseModel
from tavily import AsyncTavilyClient
import asyncio
import statistics
import logging
from agent_pipeline.config.env_config import config
from agent_pipeline.utils.simple_cache import cached

# Configuration du logger
logger = logging.getLogger(__name__)


FOLLOW_UP_DECISION_PROMPT = """
You are a researcher that decides whether we have enough information to stop 
researching or whether we need to generate follow-up queries. 
You will be given the original query and summaries of information found so far. 
IMPORTANT: For simple factual questions (e.g., 'How long do dogs live?', 'What is the height of Mount Everest?'), 
if the basic information is already present in the findings, you should NOT request follow-up queries. 
Complex questions about processes, comparisons, or multifaceted topics may need follow-ups, but simple factual 
questions rarely need more than one round of research. 
If you think we have enough information, return should_follow_up=False. If you think we need to generate follow-up queries, return should_follow_up=True. 
If you return True, you will also need to generate 2-3 follow-up queries that address specific gaps in the current findings. 
Always provide detailed reasoning for your decision. 
IMPORTANT: Only include dates or time references in your follow-up queries when they are specifically needed: 
- Use current date/year only for queries about 'latest', 'recent', 'current trends', '2025 developments', etc. 
- For general information queries, historical data, or conceptual questions, DO NOT include dates 
- For price data, use terms like 'current price' or 'latest price' rather than specific dates
"""

SUBQUERIES_PROMPT = """
You are an expert at breaking down complex market questions into specific, searchable sub-queries. 
Generate 3-5 focused search queries that will help gather comprehensive information about the main question.
Each subquery should be designed to extract specific information that will help in understanding the market dynamics.
Ensure that the subqueries are diverse and cover different aspects of the market.

IMPORTANT: Only include dates or time references in your queries when they are specifically needed:
- Use current date/year only for queries about "latest", "recent", "current trends", "2025 developments", etc.
- For general information queries, historical data, or conceptual questions, DO NOT include dates
- For price data, use terms like "current price" or "latest price" rather than specific dates
- Examples:
  * Good: "latest cryptocurrency market trends 2025" (when asking about recent trends)
  * Good: "Bitcoin price prediction methods" (general concept, no date needed)
  * Bad: "What is blockchain 2025" (general concept, date not needed)

Return your response as a JSON object with a 'queries' field containing an array of search query strings.
"""

SYNTHESIS_AGENT_PROMPT = """
You are a professional research report writer. You will receive an original query followed by multiple summaries 
of web search results. Your task is to create a comprehensive, detailed report that addresses the original query 
by combining the information from the search results into a coherent whole. 

REPORT REQUIREMENTS:
- Aim for 5-6 pages of content with substantial depth and analysis
- Use markdown formatting with clear headings and subheadings
- Include a table of contents at the beginning with anchor links
- Provide in-text citations using [Source Name] format and link to specific URLs when possible
- Include quantitative data, statistics, and specific numbers whenever available
- Add actionable insights and practical recommendations
- Create detailed analysis sections, not just summaries
- Include market forecasts and trend predictions when supported by data
- End with a comprehensive source list with full URLs

STRUCTURE GUIDELINES:
- Executive Summary (key findings and recommendations)
- Market Overview (current state with data)
- Detailed Analysis (multiple subsections with deep insights)
- Future Outlook (predictions and forecasts)
- Actionable Recommendations
- Risk Assessment
- Conclusion
- Complete Sources List

Focus on creating a report that provides genuine value to investors and decision-makers.
"""


# Modèles Pydantic pour structured outputs
class SubQueries(BaseModel):
    queries: List[str]

class FollowUpDecisionResponse(BaseModel):
    should_follow_up: bool
    reasoning: str
    queries: list[str]

class SearchResults(BaseModel):
    main_query: str
    search_results: List[str]

class SearchAgent:
    """Agent to build a complete context around a market question."""

    def __init__(self, question: str):
        self.question = question
        api_key = config.tavily_api_key
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required") 
        self.tavily_client = AsyncTavilyClient(api_key)

        self.sub_query_agent = Agent(
            name="SubQueryAgent",
            instructions=SUBQUERIES_PROMPT,
            output_type=SubQueries,
            model="gpt-4.1-mini"
        )

        self.synthesis_agent = Agent(
            name="SynthesisAgent",
            instructions=SYNTHESIS_AGENT_PROMPT,
            model="gpt-4.1-mini"
        )

        self.follow_up_decision_agent = Agent(
            name="FollowUpDecisionAgent",
            instructions=FOLLOW_UP_DECISION_PROMPT,
            output_type=FollowUpDecisionResponse,
            model="gpt-4.1-mini"
        )

    async def generate_subqueries(self, main_query: str) -> SubQueries:
        """Generate sub-questions from the main question."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subqueries_result = await Runner.run(
            self.sub_query_agent,
            input=f"Main question: {main_query} \nCurrent time: {current_time}"
        )
        return subqueries_result.final_output

    async def perform_research(self, subqueries: List[str]) -> SearchResults:
        """Perform research for each sub-question and collect results with async parallelization."""
        
        @cached(ttl_seconds=1800)  # Cache for 30 minutes
        async def _safe_search(query: str) -> dict:
            """Perform a single search with error handling and retry logic."""
            # Limiter la longueur des requêtes (max 400 caractères)
            trimmed_query = query[:400] if len(query) > 400 else query
            
            # Déterminer les paramètres adaptés selon le type de requête
            search_params = self._get_search_parameters(query)
            
            for attempt in range(3):  # Retry logic
                try:
                    response = await self.tavily_client.search(
                        trimmed_query,
                        max_results=10,
                        include_answer=True,
                        auto_parameters=True,  # Tuning automatique BETA
                        **search_params
                    )
                    return {"query": query, "response": response, "success": True}
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for query '{query[:50]}...': {e}")
                    if attempt < 2:  # Back-off exponential
                        await asyncio.sleep(2 ** attempt)
                    else:
                        logger.error(f"All attempts failed for query '{query[:50]}...': {str(e)}")
                        return {"query": query, "response": None, "success": False, "error": str(e)}
        
        # Exécution parallèle des recherches
        logger.info(f"Processing {len(subqueries)} sub-queries in parallel...")
        tasks = [_safe_search(query) for query in subqueries]
        raw_results = await asyncio.gather(*tasks)
        
        # Traitement des résultats
        search_results = []
        for result in raw_results:
            if result["success"] and result["response"]:
                formatted_result = self._format_tavily_response(result["query"], result["response"])
                search_results.append(formatted_result)
            else:
                logger.warning(f"Failed to process query: {result['query'][:50]}...")

        results = SearchResults(
            main_query=self.question,
            search_results=search_results,
        )

        return results

    def _get_search_parameters(self, query: str) -> dict:
        """Déterminer les paramètres optimaux selon le type de requête."""
        params = {}
        
        # Requêtes récentes/actuelles
        recent_keywords = ["latest", "recent", "current", "today", "2025", "trends"]
        if any(keyword in query.lower() for keyword in recent_keywords):
            params.update({
                "topic": "news",
                "search_depth": "advanced"
            })
        
        # Requêtes d'analyse approfondie
        analysis_keywords = ["analysis", "detailed", "comprehensive", "in-depth"]
        if any(keyword in query.lower() for keyword in analysis_keywords):
            params.update({
                "search_depth": "advanced",
                "include_raw_content": True
            })
        
        return params

    def _format_tavily_response(self, query: str, response: dict) -> str:
        """Format Tavily response to extract key information with adaptive filtering."""
        formatted = f"Query: {query}\n\n"
        
        # Add answer if available
        if response.get('answer'):
            formatted += f"Summary: {response['answer']}\n\n"
        
        # Add detailed results with adaptive scoring
        if response.get('results'):
            # Calcul du seuil adaptatif
            scores = [result.get('score', 0) for result in response['results']]
            if scores:
                median_score = statistics.median(scores)
                adaptive_threshold = max(0.5, median_score * 0.8)  # Au moins 80% du score médian
            else:
                adaptive_threshold = 0.7  # Fallback
            
            formatted += f"Detailed Sources (threshold: {adaptive_threshold:.2f}):\n"
            quality_results = []
            
            for i, result in enumerate(response['results'][:8], 1):  # Limite à 8 résultats
                title = result.get('title', 'No title')
                url = result.get('url', 'No URL')
                content = result.get('content', 'No content')
                score = result.get('score', 0)
                
                # Filtrage adaptatif basé sur le score
                if score >= adaptive_threshold:
                    quality_results.append({
                        'title': title,
                        'url': url,
                        'content': content[:500],
                        'score': score
                    })
            
            # Formatage des résultats de qualité
            for i, result in enumerate(quality_results, 1):
                formatted += f"[{i}] Title: {result['title']}\n"
                formatted += f"    URL: {result['url']}\n"
                formatted += f"    Content: {result['content']}...\n"
                formatted += f"    Relevance Score: {result['score']:.3f}\n\n"
            
            formatted += f"Quality sources found: {len(quality_results)}/{len(response['results'])}\n"
            
            # Métriques de performance
            if 'response_time' in response:
                formatted += f"Response time: {response['response_time']}ms\n"
        
        return formatted

    async def synthesize_report(self, main_query: str, search_results: List[str]) -> str:
        """Synthesize research results into a complete report."""
        # Validate and enrich search results before synthesis
        enriched_results = self._enrich_search_results(search_results)
        
        synthesis_input = f"Main query: {main_query}\nEnriched search results: {enriched_results}"
        synthesis_result = await Runner.run(
            self.synthesis_agent,
            input=synthesis_input
        )
        return synthesis_result.final_output

    def _enrich_search_results(self, search_results: List[str]) -> str:
        """Enrich search results with metadata and quality indicators."""
        enriched = "=== RESEARCH FINDINGS ===\n\n"
        
        for i, result in enumerate(search_results, 1):
            enriched += f"## Research Finding #{i}\n"
            enriched += f"{result}\n"
            enriched += "---\n\n"
        
        # Add metadata about the research process
        enriched += f"=== RESEARCH METADATA ===\n"
        enriched += f"Total queries processed: {len(search_results)}\n"
        enriched += f"Research timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        enriched += f"Research depth: Multi-iteration with follow-up queries\n"
        enriched += f"API: Tavily (Async + Auto-parameters)\n"
        enriched += f"Quality filtering: Adaptive threshold\n"
        enriched += f"Parallelization: Enabled\n\n"
        
        return enriched

    async def research(self, main_query: str) -> str:
        """
        Main function orchestrating sub-question generation,
        research, and report synthesis.
        Stops after 3 follow-up iterations maximum.
        """

        with trace("Deep Research Workflows"):
            # 1. Generate sub-questions
            if hasattr(self, 'console'):
                self.console.print("[dim]→ Generating specialized research sub-questions[/dim]")
            subqueries = (await self.generate_subqueries(main_query)).queries

            # 2. Perform research
            if hasattr(self, 'console'):
                self.console.print(f"[dim]→ Executing parallel research on {len(subqueries)} specialized queries[/dim]")
            initial_results = await self.perform_research(subqueries)
            all_search_results = initial_results.search_results

            # 3. Decide if follow-up is needed (uses search_results, not report)
            iteration = 0
            max_iterations = 2
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if hasattr(self, 'console'):
                self.console.print("[dim]→ Evaluating need for follow-up research[/dim]")
            follow_up_decision = await Runner.run(
                self.follow_up_decision_agent,
                input=f"Main query: {main_query}\nCurrent time: {current_time}\nSearch results so far: {all_search_results}"
            )
            follow_up_decision = follow_up_decision.final_output

            while follow_up_decision.should_follow_up and iteration < max_iterations:
                if hasattr(self, 'console'):
                    self.console.print(f"[dim]→ Follow-up research needed (iteration {iteration + 1})[/dim]")
                logger.info(f"Follow-up needed: {follow_up_decision.reasoning}")
                new_subqueries = follow_up_decision.queries
                if not new_subqueries:
                    logger.info("No follow-up queries generated, stopping.")
                    break

                # Perform research for new sub-questions
                if hasattr(self, 'console'):
                    self.console.print(f"[dim]→ Executing {len(new_subqueries)} targeted additional research queries[/dim]")
                new_results = await self.perform_research(new_subqueries)
                all_search_results.extend(new_results.search_results)

                # Decide again if follow-up is needed (uses all_search_results)
                follow_up_decision = await Runner.run(
                    self.follow_up_decision_agent,
                    input=f"Main query: {main_query}\nCurrent time: {current_time}\nSearch results so far: {all_search_results}"
                )
                follow_up_decision = follow_up_decision.final_output

                iteration += 1

            # 4. Synthesize the report at the end, using all search results
            if hasattr(self, 'console'):
                self.console.print("[dim]→ Synthesizing and compiling comprehensive research report[/dim]")
            report = await self.synthesize_report(main_query, all_search_results)
            
            # Note: Auto-save disabled to avoid unwanted files

        return report

    async def _save_report(self, report: str, query: str) -> None:
        """Save the generated report to a file (disabled by default to avoid unwanted files)."""
        # Auto-save disabled - uncomment below to re-enable
        # 
        # safe_filename = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        # safe_filename = safe_filename.replace(' ', '_')[:50]  # Limit length
        # 
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"research_report_{safe_filename}_{timestamp}.md"
        # 
        # try:
        #     with open(filename, 'w', encoding='utf-8') as f:
        #         f.write(report)
        #     
        #     # Performance metrics
        #     file_size = len(report.encode('utf-8'))
        #     logger.info(f"Report saved to: {filename}")
        #     logger.info(f"Report size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        #     
        # except Exception as e:
        #     logger.error(f"Failed to save report: {e}")
        #     logger.info(f"Report length: {len(report)} characters")
        pass

async def main():
    question = "What are the latest trends in the cryptocurrency market?"
    search_agent = SearchAgent(question)

    main_query = await search_agent.research(question)

    if main_query:
        logger.info(f"Main query processed: {main_query}")
    else:
        logger.error("Failed to generate main query.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())