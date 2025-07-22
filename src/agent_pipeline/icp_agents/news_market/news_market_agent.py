from agents import Agent, function_tool, Runner
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
from tavily import AsyncTavilyClient
import logging
from agent_pipeline.config.env_config import config
from agent_pipeline.utils.simple_cache import cached

logger = logging.getLogger(__name__)

class MarketQuestion(BaseModel):
    """Structure d'une question de marché générée"""
    question: str
    category: str
    deadline: str
    reasoning: str
    confidence: float
    relevant_keywords: List[str]

class NewsMarketAgent:
    """Agent qui crée de nouveaux marchés basés sur les actualités"""
    
    MARKET_CATEGORIES = [
        "Technology",
        "Politics", 
        "Economics",
        "Sports",
        "Entertainment",
        "Climate",
        "Healthcare",
        "Crypto",
        "Business",
        "Science"
    ]
    
    def __init__(self, tavily_api_key: str = None):
        self.tavily_client = AsyncTavilyClient(api_key=tavily_api_key or config.TAVILY_API_KEY)
        self.console = None
        
        self.agent = Agent(
            model=config.get_openai_model(),
            deps_type=type(self),
            system_prompt=self._get_system_prompt(),
            tools=[self.search_trending_news, self.validate_market_question],
        )
    
    def _get_system_prompt(self):
        return f"""Vous êtes un expert en création de marchés de prédiction basés sur les actualités.
        Votre rôle est d'analyser les tendances d'actualités et de générer des questions de marché 
        pertinentes et mesurables.
        
        Catégories disponibles: {', '.join(self.MARKET_CATEGORIES)}
        
        Pour chaque actualité, vous devez:
        1. Identifier les événements futurs mesurables
        2. Formuler des questions claires avec des échéances précises
        3. Éviter les sujets controversés ou sensibles
        4. Assurer que la question a une réponse binaire claire (Oui/Non)
        5. Fournir un raisonnement sur pourquoi cette question est pertinente
        
        Exemples de bonnes questions:
        - "Tesla dépassera-t-il 500 milliards de capitalisation avant fin 2025?"
        - "L'inflation US sera-t-elle sous les 3% en décembre 2025?"
        - "Bitcoin atteindra-t-il 200 000$ avant juillet 2025?"
        
        Évitez:
        - Questions subjectives ou d'opinion
        - Événements déjà passés
        - Questions sans échéance claire
        - Sujets politiques controversés"""
    
    @function_tool
    async def search_trending_news(self, category: str = "general") -> str:
        """Recherche les actualités tendance dans une catégorie"""
        try:
            if self.console:
                self.console.print(f"[dim]📰 Searching trending news in: {category}[/dim]")
            
            query = f"trending news {category} {datetime.now().strftime('%Y-%m')}"
            
            response = await self.tavily_client.asearch(
                query=query,
                search_depth="basic",
                max_results=8,
                include_domains=["reuters.com", "bloomberg.com", "techcrunch.com", "cnn.com"],
                include_answer=True
            )
            
            results = []
            if response.get('answer'):
                results.append(f"Trending Summary: {response['answer']}")
            
            for result in response.get('results', [])[:5]:
                title = result.get('title', 'No title')
                content = result.get('content', '')[:200] + "..."
                date = result.get('published_date', 'Unknown date')
                results.append(f"• {title} ({date}): {content}")
            
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"Error searching trending news: {e}")
            return f"News search failed: {str(e)}"
    
    @function_tool
    async def validate_market_question(self, question: str) -> str:
        """Valide si une question est appropriée pour un marché de prédiction"""
        validation_criteria = [
            "Has clear binary outcome (Yes/No)",
            "Has specific deadline",
            "Is measurable and verifiable", 
            "Is about future event",
            "Avoids controversial topics"
        ]
        
        # Logique basique de validation
        score = 0
        feedback = []
        
        if "?" in question and ("will" in question.lower() or "sera" in question.lower()):
            score += 1
            feedback.append("✓ Clear question format")
        
        if any(word in question.lower() for word in ["by", "before", "end of", "until", "avant", "fin"]):
            score += 1
            feedback.append("✓ Has deadline")
        
        if any(word in question.lower() for word in ["reach", "exceed", "above", "below", "atteindra", "dépasser"]):
            score += 1
            feedback.append("✓ Measurable outcome")
        
        # Années futures
        current_year = datetime.now().year
        if str(current_year + 1) in question or str(current_year + 2) in question:
            score += 1
            feedback.append("✓ Future-focused")
        
        validation_result = f"Score: {score}/4\n" + "\n".join(feedback)
        return validation_result
    
    @cached(ttl_seconds=1800)  # 30 minutes cache
    async def generate_market_questions(self, category: str = "general", count: int = 3) -> List[MarketQuestion]:
        """Génère des questions de marché basées sur les actualités d'une catégorie"""
        
        if self.console:
            self.console.print(f"[yellow]📈 Generating {count} market questions for category: {category}[/yellow]")
        
        prompt = f"""
        Analysez les actualités récentes dans la catégorie "{category}" et générez {count} questions 
        de marché de prédiction pertinentes.
        
        Chaque question doit:
        1. Être basée sur des actualités récentes et tendances
        2. Avoir une échéance claire dans les 12 prochains mois
        3. Être mesurable et vérifiable
        4. Avoir une réponse binaire (Oui/Non)
        5. Être d'intérêt public
        
        Format de réponse souhaité pour chaque question:
        - Question: [la question complète]
        - Catégorie: {category}
        - Échéance: [date limite]
        - Raisonnement: [pourquoi cette question est pertinente]
        - Mots-clés: [mots-clés pour le suivi]
        
        Générez maintenant {count} questions basées sur les actualités récentes.
        """
        
        try:
            runner = Runner()
            result = await runner.run(self.agent, user_prompt=prompt, deps=self)
            
            # Parser la réponse (implémentation simplifiée)
            response_text = result.data if hasattr(result, 'data') else str(result)
            
            # Logique basique pour extraire les questions
            questions = []
            lines = response_text.split('\n')
            current_question = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Question:'):
                    if current_question:
                        questions.append(self._create_market_question(current_question, category))
                    current_question = {'question': line.replace('Question:', '').strip()}
                elif line.startswith('Échéance:') or line.startswith('Deadline:'):
                    current_question['deadline'] = line.split(':', 1)[1].strip()
                elif line.startswith('Raisonnement:') or line.startswith('Reasoning:'):
                    current_question['reasoning'] = line.split(':', 1)[1].strip()
                elif line.startswith('Mots-clés:') or line.startswith('Keywords:'):
                    keywords = line.split(':', 1)[1].strip()
                    current_question['keywords'] = [k.strip() for k in keywords.split(',')]
            
            # Ajouter la dernière question
            if current_question:
                questions.append(self._create_market_question(current_question, category))
            
            # Si parsing échoue, créer des questions par défaut
            if not questions:
                questions = self._create_fallback_questions(category, count)
            
            return questions[:count]
            
        except Exception as e:
            logger.error(f"Error generating market questions: {e}")
            return self._create_fallback_questions(category, count)
    
    def _create_market_question(self, data: Dict, category: str) -> MarketQuestion:
        """Crée un objet MarketQuestion à partir des données parsées"""
        return MarketQuestion(
            question=data.get('question', 'Generated market question'),
            category=category,
            deadline=data.get('deadline', f'End of {datetime.now().year + 1}'),
            reasoning=data.get('reasoning', 'Based on current market trends'),
            confidence=0.7,
            relevant_keywords=data.get('keywords', [category])
        )
    
    def _create_fallback_questions(self, category: str, count: int) -> List[MarketQuestion]:
        """Crée des questions de secours si la génération échoue"""
        fallback_templates = {
            "Technology": [
                "Will Apple reach a $4 trillion market cap by end of 2025?",
                "Will OpenAI release GPT-5 before July 2025?",
                "Will Tesla deliver 3 million vehicles in 2025?"
            ],
            "Crypto": [
                "Will Bitcoin reach $200,000 by end of 2025?",
                "Will Ethereum surpass $10,000 before December 2025?",
                "Will a Bitcoin ETF reach $100B AUM by end of 2025?"
            ],
            "Economics": [
                "Will US inflation rate drop below 2% by end of 2025?",
                "Will the Fed cut rates below 3% in 2025?",
                "Will US GDP growth exceed 3% in 2025?"
            ]
        }
        
        templates = fallback_templates.get(category, [
            f"Will a major {category.lower()} event occur by end of 2025?",
            f"Will {category.lower()} markets reach new highs in 2025?",
            f"Will {category.lower()} innovation accelerate in 2025?"
        ])
        
        questions = []
        for i, template in enumerate(templates[:count]):
            questions.append(MarketQuestion(
                question=template,
                category=category,
                deadline=f"December 31, 2025",
                reasoning=f"Fallback question for {category} category",
                confidence=0.5,
                relevant_keywords=[category.lower()]
            ))
        
        return questions
    
    async def monitor_category_trends(self, category: str) -> str:
        """Surveille les tendances d'une catégorie et suggère de nouveaux marchés"""
        questions = await self.generate_market_questions(category, 5)
        
        if self.console:
            self.console.print(f"\n[bold cyan]📊 New Market Opportunities in {category}:[/bold cyan]")
            for i, q in enumerate(questions, 1):
                self.console.print(f"{i}. {q.question}")
                self.console.print(f"   └─ Deadline: {q.deadline}")
                self.console.print(f"   └─ Confidence: {q.confidence:.1%}")
        
        summary = f"Generated {len(questions)} potential market questions for {category}:\n"
        for q in questions:
            summary += f"• {q.question} (by {q.deadline})\n"
        
        return summary