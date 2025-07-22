#!/usr/bin/env python3
"""
Script de lancement simple pour le pipeline ICP Agents
Permet de lancer le programme sans utiliser -m
"""

import sys
import os
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import logging
from datetime import datetime

# Ajouter le répertoire parent au Python path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Configuration de Rich Console
console = Console()

# Configuration du logging - DESACTIVE pour CLI
# Les logs sont gardés pour debug mais pas affichés dans le CLI
logging.basicConfig(
    level=logging.CRITICAL,  # Désactive tous les logs sauf CRITICAL
    format="%(message)s"
)

# Maintenant on peut importer l'orchestrator avec la nouvelle structure
from agent_pipeline.core.orchestrator import PipelineOrchestrator, PipelineConfig
from agent_pipeline.icp_agents.search import SearchAgent

async def run_pipeline_with_interface():
    """Launch the pipeline with a Rich interface structured by phases."""
    
    # Header
    console.print(Panel(
        Text("ICP Agents - Market Analysis Pipeline", style="bold blue"),
        subtitle=f"Directory: {current_dir}"
    ))
    
    # API keys verification
    required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        console.print(f"[red]Missing API keys: {', '.join(missing_keys)}[/red]")
        console.print("[yellow]Configure them with:[/yellow]")
        for key in missing_keys:
            console.print(f"   export {key}=\"your_key_here\"")
        sys.exit(1)
    
    # Configuration du pipeline
    config = PipelineConfig(
        research_depth="standard",
        use_scenario_analysis=True,
        timeout_seconds=300
    )
    
    # Interface de sélection des questions
    console.print("\n[bold cyan]Available Questions:[/bold cyan]")
    default_questions = [
        "Will Bitcoin reach $400,000 by end of 2035?"
    ]
    
    table = Table(title="Select a Question")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Question", style="white")
    
    for i, question in enumerate(default_questions, 1):
        table.add_row(str(i), question)
    
    table.add_row(str(len(default_questions) + 1), "[italic]Enter a custom question[/italic]")
    
    console.print(table)
    
    # Sélection interactive de la question
    max_choice = len(default_questions) + 1
    while True:
        try:
            choice = input(f"\nSelect a question (1-{max_choice}): ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(default_questions):
                    selected_question = default_questions[choice_num - 1]
                    break
                elif choice_num == max_choice:
                    selected_question = input("Enter your custom question: ").strip()
                    if selected_question:
                        break
                    else:
                        console.print("[red]Please enter a valid question.[/red]")
                else:
                    console.print(f"[red]Please enter a number between 1 and {max_choice}.[/red]")
            else:
                console.print(f"[red]Please enter a number between 1 and {max_choice}.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled by user[/yellow]")
            sys.exit(0)
        except Exception:
            console.print("[red]Invalid input. Please try again.[/red]")
    
    console.print(f"\n[green]Selected question:[/green] {selected_question}")
    
    # Saisie du prix de marché
    console.print("\n[bold cyan]Market Price Configuration:[/bold cyan]")
    console.print("Enter the current market price (implied probability) for this question.")
    console.print("Example: 0.45 means 45% probability according to the market")
    console.print("Press Enter to skip (no market price)")
    
    while True:
        try:
            market_price_input = input("Market price (0.01-0.99 or press Enter to skip): ").strip()
            if not market_price_input:
                market_price = None
                console.print("[yellow]No market price provided - Kelly calculation will show 0%[/yellow]")
                break
            else:
                market_price = float(market_price_input)
                if 0.01 <= market_price <= 0.99:
                    console.print(f"[green]Market price set to: {market_price:.1%}[/green]")
                    break
                else:
                    console.print("[red]Please enter a value between 0.01 and 0.99[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled by user[/yellow]")
            sys.exit(0)
        except ValueError:
            console.print("[red]Please enter a valid number (e.g., 0.45)[/red]")
    
    selected_questions = [selected_question]
    
    orchestrator = PipelineOrchestrator()
    
    for i, question in enumerate(selected_questions, 1):
        console.print(f"\n[bold cyan]Question {i}/{len(selected_questions)}:[/bold cyan] {question}")
        
        start_time = datetime.now()
        
        try:
            # PHASE 1: RESEARCH
            console.print("\n[bold yellow]📊 PHASE 1: MARKET DATA RESEARCH[/bold yellow]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False
            ) as progress:
                research_task = progress.add_task("[cyan]Collecting and analyzing market data...[/cyan]", total=None)
                search_agent = SearchAgent(question)
                search_agent.console = console
                research_result = await search_agent.research(question)
                progress.update(research_task, description="[green]✓ Research completed - data collected and analyzed[/green]")
                progress.stop_task(research_task)
            
            # PHASE 2: SCENARIO ANALYSIS
            console.print("\n[bold yellow]🎯 PHASE 2: SCENARIO ANALYSIS[/bold yellow]")
            if config.use_scenario_analysis:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=False
                ) as progress:
                    scenario_task = progress.add_task("[cyan]Generating and evaluating market scenarios...[/cyan]", total=None)
                    orchestrator.think_thoroughly_agent.console = console
                    scenario_report = await orchestrator._do_scenario_analysis(question, research_result, config.research_depth)
                    progress.update(scenario_task, description="[green]✓ Scenario analysis completed - probabilities calculated[/green]")
                    progress.stop_task(scenario_task)
            else:
                scenario_report = None
                console.print("[dim]Scenario analysis disabled[/dim]")
            
            # PHASE 3: PREDICTIONS
            console.print("\n[bold yellow]🔮 PHASE 3: PREDICTION GENERATION[/bold yellow]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False
            ) as progress:
                prediction_task = progress.add_task("[cyan]Calculating probabilities and position recommendations...[/cyan]", total=None)
                orchestrator.analysis_agent.console = console
                orchestrator.prediction_agent.console = console
                
                prediction_result = await orchestrator._generate_prediction(research_result, question, scenario_report, market_price)
                progress.update(prediction_task, description="[green]✓ Predictions generated - probabilities and Kelly fraction calculated[/green]")
                progress.stop_task(prediction_task)
            
            # PHASE 4: FINAL ADVICE
            console.print("\n[bold yellow]💡 PHASE 4: SYNTHESIS & ADVICE[/bold yellow]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False
            ) as progress:
                advice_task = progress.add_task("[cyan]Final synthesis and recommendation generation...[/cyan]", total=None)
                orchestrator.advice_agent.console = console
                advice_result = await orchestrator._generate_advice(prediction_result, research_result, scenario_report, question)
                progress.update(advice_task, description="[green]✓ Market advice ready - recommendations finalized[/green]")
                progress.stop_task(advice_task)
            
            # Construire le résultat final
            duration = (datetime.now() - start_time).total_seconds()
            result = type('PipelineResult', (), {
                'success': True,
                'recommendation': advice_result.advice.primary_recommendation,
                'probability': prediction_result.prediction.probability,
                'confidence': prediction_result.prediction.confidence_level,
                'risk_level': advice_result.risk_assessment.overall_risk_level,
                'reasoning': advice_result.advice.reasoning,
                'duration_seconds': duration,
                'errors': [],
                'market_price': market_price,
                'kelly_fraction': prediction_result.kelly_fraction if hasattr(prediction_result, 'kelly_fraction') else 0.0
            })()
            
        except Exception as e:
            console.print(f"\n[red]✗ Error during analysis: {str(e)}[/red]")
            continue
        
        # Affichage des résultats dans un layout structuré
        duration = (datetime.now() - start_time).total_seconds()
        
        # Main results table
        results_table = Table(title="Analysis Results", show_header=True, header_style="bold magenta")
        results_table.add_column("Metric", style="cyan", width=22)
        results_table.add_column("Value", style="white", width=35)
        results_table.add_column("Details", style="dim", width=25)
        
        # Recommendation with color coding
        rec_color = "green" if result.recommendation in ["BUY_YES", "BUY"] else "red" if result.recommendation in ["SELL", "SHORT"] else "yellow"
        results_table.add_row("Recommendation", f"[{rec_color}]{result.recommendation}[/{rec_color}]", "Suggested action")
        
        # Probability with visual progress bar
        prob_bar = "█" * int(result.probability * 10) + "░" * (10 - int(result.probability * 10))
        results_table.add_row("Probability", f"{result.probability:.1%} {prob_bar}", "Statistical certainty")
        
        # Confidence with indicator
        conf_color = "green" if result.confidence.upper() == "HIGH" else "yellow" if result.confidence.upper() == "MEDIUM" else "red"
        results_table.add_row("Confidence", f"[{conf_color}]{result.confidence.upper()}[/{conf_color}]", "Analysis reliability")
        
        # Risk with appropriate color
        risk_color = "red" if result.risk_level == "HIGH" else "yellow" if result.risk_level == "MEDIUM" else "green"
        results_table.add_row("Risk Level", f"[{risk_color}]{result.risk_level}[/{risk_color}]", "Risk exposure")
        
        # Kelly Fraction
        if hasattr(result, 'kelly_fraction') and result.market_price is not None:
            kelly_color = "green" if result.kelly_fraction > 0.05 else "yellow" if result.kelly_fraction > 0.02 else "dim"
            results_table.add_row("Kelly Fraction", f"[{kelly_color}]{result.kelly_fraction:.1%}[/{kelly_color}]", "Optimal bet size")
        elif result.market_price is None:
            results_table.add_row("Kelly Fraction", "[dim]N/A (no market price)[/dim]", "Need market price")
        
        # Market Price
        if result.market_price is not None:
            results_table.add_row("Market Price", f"[cyan]{result.market_price:.1%}[/cyan]", "Implied probability")
        
        # Performance
        perf_color = "green" if duration < 120 else "yellow" if duration < 300 else "red"
        results_table.add_row("Execution Time", f"[{perf_color}]{duration:.1f}s[/{perf_color}]", "Processing duration")
        
        if result.errors:
            results_table.add_row("Errors", f"[red]{len(result.errors)} error(s)[/red]", "Issues encountered")
        
        console.print(results_table)
        
        # Detailed reasoning panel
        if result.reasoning:
            reasoning_text = result.reasoning[:800] + "\n[dim]...(truncated for display)[/dim]" if len(result.reasoning) > 800 else result.reasoning
            console.print(Panel(
                reasoning_text,
                title="Detailed Reasoning",
                border_style="blue",
                expand=False
            ))
    
    console.print("\n[bold green]Analysis completed![/bold green]")


if __name__ == "__main__":
    try:
        asyncio.run(run_pipeline_with_interface())
    except KeyboardInterrupt:
        console.print("\n[yellow]Program interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)