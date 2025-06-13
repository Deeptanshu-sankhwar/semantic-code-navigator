"""Demo module for showcasing MindsDB semantic code navigator workflow capabilities."""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from typing import Dict, Any
import sys

from src.mindsdb_client import MindsDBClient

console = Console()


@click.group()
def demo():
    """Demo commands for showcasing AI workflow capabilities."""
    pass


@demo.command("workflow")
@click.argument("query", required=True)
@click.option("--limit", default=5, help="Maximum number of results")
def demo_ai_workflow(query: str, limit: int):
    """Demonstrate the complete AI workflow: KB search followed by AI table analysis."""
    console.print(Panel.fit(
        f"[bold blue]AI Workflow Demo[/bold blue]\n"
        f"Query: [italic]{query}[/italic]\n"
        f"Workflow: KB Search → AI Analysis",
        border_style="blue"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            console.print("\nStep 1: Semantic Search in Knowledge Base", style="bold blue")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Performing semantic search...", total=None)
                
                results = client.semantic_search_with_ai_analysis(
                    query=query,
                    limit=limit,
                    analyze_purpose=True,
                    analyze_explanation=True,
                    analyze_docstring=True,
                    analyze_tests=True
                )
                
                progress.update(task, description=f"Completed workflow with {len(results)} results")
            
            if not results:
                console.print("No results found for the query.", style="yellow")
                return
            
            console.print(f"\nStep 2: AI Analysis Complete", style="bold green")
            console.print(f"Enhanced {len(results)} search results with AI insights\n")
            
            for i, result in enumerate(results, 1):
                console.print(f"[bold cyan]Result {i}:[/bold cyan]")
                
                console.print(f"  File: {result.get('filepath', 'N/A')}")
                console.print(f"  Function: {result.get('function_name', 'N/A')}")
                console.print(f"  Language: {result.get('language', 'N/A')}")
                console.print(f"  Relevance: {result.get('relevance', 0):.3f}")
                
                if 'ai_purpose' in result:
                    console.print(f"  AI Purpose: [green]{result['ai_purpose']}[/green]")
                
                if 'ai_explanation' in result:
                    explanation = result['ai_explanation'][:100] + "..." if len(result['ai_explanation']) > 100 else result['ai_explanation']
                    console.print(f"  AI Explanation: [yellow]{explanation}[/yellow]")
                
                if 'ai_test_cases' in result:
                    tests = result['ai_test_cases'][:80] + "..." if len(result['ai_test_cases']) > 80 else result['ai_test_cases']
                    console.print(f"  AI Test Ideas: [blue]{tests}[/blue]")
                
                code = result.get('chunk_content', '')[:150] + "..." if len(result.get('chunk_content', '')) > 150 else result.get('chunk_content', '')
                console.print(f"  Code: [dim]{code}[/dim]")
                console.print()
            
            console.print("AI Workflow Complete: Semantic search results enhanced with AI analysis!", style="bold green")
            
    except Exception as e:
        console.print(f"Workflow demo failed: {e}", style="red")
        sys.exit(1)


@demo.command("create-view")
def create_workflow_view():
    """Create a SQL view that demonstrates KB and AI table integration."""
    console.print(Panel.fit(
        "[bold blue]AI Workflow View Creation[/bold blue]\n"
        "Creating SQL view that joins KB with AI tables",
        border_style="blue"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating workflow view...", total=None)
                
                success = client.create_ai_workflow_view()
                
                if success:
                    progress.update(task, description="Workflow view created successfully")
                    
                    console.print("\nCreated SQL View: code_analysis_workflow", style="bold green")
                    console.print("\nThis view demonstrates the integration by joining:", style="bold")
                    console.print("  • Knowledge Base (semantic search results)")
                    console.print("  • code_classifier (AI purpose classification)")
                    console.print("  • code_explainer (AI explanations)")
                    console.print("  • docstring_generator (AI documentation)")
                    console.print("  • test_case_outliner (AI test suggestions)")
                    
                    console.print(f"\nQuery the view with: demo query-view", style="blue")
                else:
                    progress.update(task, description="Failed to create workflow view")
                    sys.exit(1)
                    
    except Exception as e:
        console.print(f"View creation failed: {e}", style="red")
        sys.exit(1)


@demo.command("query-view")
@click.option("--limit", default=5, help="Maximum number of results")
def query_workflow_view(limit: int):
    """Query the AI workflow view to see integrated KB and AI table results."""
    console.print(Panel.fit(
        "[bold blue]AI Workflow View Query[/bold blue]\n"
        "Querying integrated KB + AI tables view",
        border_style="blue"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Querying workflow view...", total=None)
                
                results = client.query_ai_workflow_view(limit=limit)
                
                progress.update(task, description=f"Retrieved {len(results)} integrated results")
            
            if not results:
                console.print("No results found in workflow view.", style="yellow")
                console.print("Make sure you have:", style="blue")
                console.print("  1. Ingested some code: kb:ingest <repo_url>")
                console.print("  2. Created AI tables: ai:init")
                console.print("  3. Created the view: demo create-view")
                return
            
            console.print(f"\nIntegrated Results from AI Workflow View:", style="bold")
            
            workflow_table = Table(show_header=True, header_style="bold magenta")
            workflow_table.add_column("Function", style="cyan", width=15)
            workflow_table.add_column("Language", style="green", width=8)
            workflow_table.add_column("AI Purpose", style="yellow", width=12)
            workflow_table.add_column("AI Explanation", style="blue", width=30)
            workflow_table.add_column("Code Preview", style="white", width=25)
            
            for result in results:
                function_name = result.get('function_name', 'N/A')[:14]
                language = result.get('language', 'N/A')
                ai_purpose = result.get('ai_purpose', 'N/A')[:11]
                ai_explanation = result.get('ai_explanation', 'N/A')[:29]
                code_preview = result.get('chunk_content', '')[:24] + "..." if len(result.get('chunk_content', '')) > 24 else result.get('chunk_content', 'N/A')
                
                workflow_table.add_row(
                    function_name,
                    language,
                    ai_purpose,
                    ai_explanation,
                    code_preview
                )
            
            console.print(workflow_table)
            
            console.print(f"\nSuccessfully demonstrated KB + AI table integration!", style="bold green")
            console.print(f"This view shows how MindsDB can chain operations:", style="blue")
            console.print(f"  KB Search → AI Classification → AI Explanation → Unified Results", style="dim")
            
    except Exception as e:
        console.print(f"View query failed: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    demo() 