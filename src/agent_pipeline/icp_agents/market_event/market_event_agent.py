from agents import Agent, function_tool, Runner, trace
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from tavily import AsyncTavilyClient
import asyncio
import logging
from agent_pipeline.config.env_config import config
from agent_pipeline.utils.simple_cache import cached

logger = logging.getLogger(__name__)

class EventStatus(BaseModel):
    """Statut d'un événement de marché"""
    event_occurred: bool
    date_occurred: Optional[str]
    confidence: float
    evidence: List[str]
    reasoning: str

class MarketEventAgent:
    """Agent qui vérifie si les événements de marché sont passés"""
    
    def __init__(self, tavily_api_key: str = None):
        self.tavily_client = AsyncTavilyClient(api_key=tavily_api_key or config.TAVILY_API_KEY)
        self.console = None
        
        self.agent = Agent(
            model=config.get_openai_model(),
            deps_type=type(self),
            system_prompt=self._get_system_prompt(),
            tools=[self.search_web],
        )
    
    def _get_system_prompt(self):
        return """Vous êtes un expert en vérification d'événements de marché.
        Votre rôle est de déterminer si un événement spécifique décrit dans une question de marché 
        s'est déjà produit ou non.
        
        Pour chaque événement, vous devez:
        1. Rechercher des informations récentes sur l'événement
        2. Déterminer si l'événement s'est produit avec certitude
        3. Fournir la date si disponible
        4. Évaluer votre niveau de confiance
        5. Présenter les preuves trouvées
        
        Soyez particulièrement attentif aux dates et aux détails spécifiques de l'événement."""
    
    @function_tool
    async def search_web(self, query: str) -> str:
        """Recherche des informations sur le web pour vérifier un événement"""
        try:
            if self.console:
                self.console.print(f"[dim]🔍 Searching: {query}[/dim]")
            
            response = await self.tavily_client.asearch(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_domains=["reuters.com", "bloomberg.com", "cnbc.com", "ft.com", "wsj.com"],
                include_answer=True
            )
            
            results = []
            if response.get('answer'):
                results.append(f"Summary: {response['answer']}")
            
            for result in response.get('results', [])[:3]:
                results.append(f"Source ({result.get('published_date', 'Unknown date')}): {result.get('content', '')}")
            
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return f"Search failed: {str(e)}"
    
    @cached(ttl_seconds=3600)
    async def check_event_status(self, event_description: str) -> EventStatus:
        """Vérifie si un événement décrit dans une question de marché s'est produit"""
        
        if self.console:
            self.console.print(f"[yellow]🔍 Checking event status: {event_description}[/yellow]")
        
        # Préparer le prompt pour l'agent
        prompt = f"""
        Vérifiez si l'événement suivant s'est déjà produit:
        "{event_description}"
        
        Recherchez des informations récentes et fiables pour déterminer:
        1. Si l'événement a eu lieu
        2. Quand il a eu lieu (si applicable)
        3. Votre niveau de confiance dans cette information
        4. Les preuves qui supportent votre conclusion
        
        Date actuelle pour référence: {datetime.now().strftime('%Y-%m-%d')}
        
        Retournez une réponse structurée avec votre analyse.
        """
        
        try:
            runner = Runner()
            result = await runner.run(self.agent, user_prompt=prompt, deps=self)
            
            # Parser la réponse de l'agent pour extraire les informations
            response_text = result.data if hasattr(result, 'data') else str(result)
            
            # Logique simple pour déterminer si l'événement s'est produit
            # (en production, ceci serait plus sophistiqué)
            event_occurred = any(
                keyword in response_text.lower() 
                for keyword in ['occurred', 'happened', 'took place', 'confirmed', 's\'est produit', 'eu lieu']
            )
            
            confidence = 0.8 if 'confirmed' in response_text.lower() else 0.6
            
            return EventStatus(
                event_occurred=event_occurred,
                date_occurred=self._extract_date(response_text) if event_occurred else None,
                confidence=confidence,
                evidence=[response_text[:500] + "..." if len(response_text) > 500 else response_text],
                reasoning=f"Analysis based on web search results for: {event_description}"
            )
            
        except Exception as e:
            logger.error(f"Error checking event status: {e}")
            return EventStatus(
                event_occurred=False,
                date_occurred=None,
                confidence=0.0,
                evidence=[f"Error occurred: {str(e)}"],
                reasoning="Could not verify event due to technical error"
            )
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extrait une date du texte (implémentation basique)"""
        # Implémentation simple - en production, utiliser une bibliothèque de parsing de dates
        import re
        
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY ou DD/MM/YYYY
            r'\d{1,2} \w+ \d{4}',  # DD Month YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        
        return None
    
    async def get_event_verification_prompt(self, market_question: str) -> str:
        """Génère un prompt pour vérifier si l'événement d'une question de marché s'est produit"""
        
        # Extraire l'événement principal de la question
        event_check = await self.check_event_status(market_question)
        
        if event_check.event_occurred:
            return f"""
            ⚠️  ATTENTION: L'événement décrit dans cette question semble s'être déjà produit!
            
            Question: {market_question}
            Statut: Événement probablement survenu le {event_check.date_occurred or 'date inconnue'}
            Confiance: {event_check.confidence:.1%}
            
            Cette question de marché pourrait ne plus être valide pour les prédictions futures.
            Considérez ajuster la question ou vérifier les sources récentes.
            """
        else:
            return f"""
            ✓ L'événement décrit semble être encore futur ou non confirmé.
            Question: {market_question}
            Statut: Événement à venir
            Confiance: {event_check.confidence:.1%}
            """