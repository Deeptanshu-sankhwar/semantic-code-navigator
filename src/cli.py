"""Main CLI application for Semantic Code Navigator."""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from typing import Optional, Dict, Any
import json
import sys

from .config import config
from .mindsdb_client import MindsDBClient
from .agents import AgentManager, CodeReviewAgent, ArchitectureDiscoveryAgent, SecurityAuditAgent, AGENT_TEMPLATES

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Semantic Code Navigator - MindsDB Knowledge Base Stress Testing Tool
    
    A CLI tool for ingesting codebases and performing semantic navigation searches
    using MindsDB Knowledge Bases.
    """
    pass


@cli.command("kb:init")
@click.option("--force", is_flag=True, help="Force recreate knowledge base if exists")
@click.option("--validate-config", is_flag=True, help="Validate configuration before creating KB")
def init_kb(force: bool, validate_config: bool):
    """Initialize MindsDB Knowledge Base with embedding/reranking models for semantic code search.
    
    Creates a new knowledge base with configured OpenAI embedding and reranking models.
    Validates configuration if requested and displays schema information upon successful creation.
    """
    console.print(Panel.fit(
        "[bold blue]Semantic Code Navigator[/bold blue]\n"
        "Initializing MindsDB Knowledge Base",
        border_style="blue"
    ))
    
    try:
        if validate_config:
            console.print("Validating configuration...", style="blue")
            config.validate()
            console.print("Configuration is valid", style="green")
        
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            if force:
                console.print("Force flag detected, dropping existing KB...", style="yellow")
                client.drop_knowledge_base()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating knowledge base...", total=None)
                
                success = client.create_knowledge_base()
                
                if success:
                    progress.update(task, description="Knowledge base created successfully")
                    
                    console.print("\nKnowledge Base Configuration:", style="bold")
                    
                    config_table = Table(show_header=True, header_style="bold magenta")
                    config_table.add_column("Setting", style="cyan")
                    config_table.add_column("Value", style="green")
                    
                    config_table.add_row("KB Name", config.kb.name)
                    config_table.add_row("Embedding Model", config.kb.embedding_model)
                    config_table.add_row("Reranking Model", config.kb.reranking_model)
                    config_table.add_row("ID Column", config.kb.id_column)
                    
                    console.print(config_table)
                    
                    console.print("\nData Schema for Stress Testing:", style="bold")
                    
                    req_table = Table(title="Required Columns", show_header=True, header_style="bold green")
                    req_table.add_column("Column", style="cyan")
                    req_table.add_column("Purpose", style="white")
                    
                    column_purposes = {
                        'content': 'The actual function/class code to embed',
                        'filepath': 'Where in repo this code resides',
                        'language': 'Python, JavaScript, Go, etc.',
                        'function_name': 'Name of the function/class',
                        'repo': 'GitHub URL or repo name',
                        'last_modified': 'For freshness filters'
                    }
                    
                    for col in config.kb.required_columns:
                        req_table.add_row(col, column_purposes.get(col, "Required for stress testing"))
                    
                    console.print(req_table)
                    
                    opt_table = Table(title="Optional Columns (Enhanced Features)", show_header=True, header_style="bold yellow")
                    opt_table.add_column("Column", style="cyan")
                    opt_table.add_column("Purpose", style="white")
                    
                    optional_purposes = {
                        'author': 'From git log, helps with filters',
                        'line_range': 'e.g. "12-48" for locating in file',
                        'summary': 'Short LLM-generated TL;DR for AI Tables'
                    }
                    
                    for col in config.kb.optional_columns:
                        opt_table.add_row(col, optional_purposes.get(col, "Optional enhancement"))
                    
                    console.print(opt_table)
                    
                    console.print(f"\nKnowledge base '{config.kb.name}' is ready for ingestion", style="bold green")
                    console.print("Next step: Use 'kb:ingest <path>' to ingest your codebase", style="blue")
                else:
                    progress.update(task, description="Failed to create knowledge base")
                    sys.exit(1)
                    
    except Exception as e:
        console.print(f"Initialization failed: {e}", style="red")
        sys.exit(1)


@cli.command("kb:query")
@click.argument("query", required=True)
@click.option("--language", "-l", help="Filter by programming language")
@click.option("--filepath", "-f", help="Filter by file path pattern")
@click.option("--function", help="Filter by function name")
@click.option("--repo", "-r", help="Filter by repository name")
@click.option("--author", "-a", help="Filter by code author")
@click.option("--since", help="Filter by last modified date (YYYY-MM-DD)")
@click.option("--limit", default=10, help="Maximum number of results")
@click.option("--relevance-threshold", default=0.0, type=float, help="Minimum relevance score")
@click.option("--output-format", default="table", type=click.Choice(["table", "json", "compact"]), help="Output format")
@click.option("--ai-purpose", is_flag=True, help="Add AI purpose classification to results")
@click.option("--ai-explain", is_flag=True, help="Add AI code explanations to results")
@click.option("--ai-docstring", is_flag=True, help="Add AI-generated docstrings to results")
@click.option("--ai-tests", is_flag=True, help="Add AI test case suggestions to results")
@click.option("--ai-all", is_flag=True, help="Add all AI analysis to results")
def query_kb(query: str, language: Optional[str], filepath: Optional[str], 
             function: Optional[str], repo: Optional[str], author: Optional[str],
             since: Optional[str], limit: int, relevance_threshold: float, output_format: str,
             ai_purpose: bool, ai_explain: bool, ai_docstring: bool, ai_tests: bool, ai_all: bool):
    """Perform semantic search with natural language queries and optional metadata filtering."""
    console.print(Panel.fit(
        f"[bold blue]Semantic Search[/bold blue]\n"
        f"Query: [italic]{query}[/italic]",
        border_style="blue"
    ))
    
    use_ai_workflow = ai_purpose or ai_explain or ai_docstring or ai_tests or ai_all
    
    if use_ai_workflow:
        console.print("AI-Enhanced Search: Combining KB results with AI table analysis", style="blue")
    
    try:
        filters = {}
        if language:
            filters["language"] = language
        if filepath:
            filters["filepath"] = filepath
        if function:
            filters["function_name"] = function
        if repo:
            filters["repo"] = repo
        if author:
            filters["author"] = author
        if since:
            filters["last_modified"] = f"> '{since}'"
        
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Searching knowledge base...", total=None)
                
                if use_ai_workflow:
                    results = client.semantic_search_with_ai_analysis(
                        query=query,
                        filters=filters,
                        limit=limit,
                        relevance_threshold=relevance_threshold,
                        analyze_purpose=ai_purpose or ai_all,
                        analyze_explanation=ai_explain or ai_all,
                        analyze_docstring=ai_docstring or ai_all,
                        analyze_tests=ai_tests or ai_all
                    )
                    progress.update(task, description=f"Found {len(results)} results with AI analysis")
                else:
                    results = client.semantic_search(
                        query=query,
                        filters=filters,
                        limit=limit,
                        relevance_threshold=relevance_threshold
                    )
                    progress.update(task, description=f"Found {len(results)} results")
            
            if not results:
                console.print("No results found. Try adjusting your query or filters.", style="yellow")
                return
            
            _display_search_results(results, output_format, query, filters, relevance_threshold, use_ai_workflow)
            
    except Exception as e:
        console.print(f"Search failed: {e}", style="red")
        sys.exit(1)


@cli.command("kb:index")
@click.option("--show-stats", is_flag=True, help="Show knowledge base statistics after indexing")
def create_index(show_stats: bool):
    """Create database index on knowledge base to optimize search performance for large codebases."""
    console.print(Panel.fit(
        "[bold blue]Index Creation[/bold blue]\n"
        "Optimizing knowledge base for faster searches",
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
                task = progress.add_task("Creating index...", total=None)
                
                success = client.create_index()
                
                if success:
                    progress.update(task, description="Index created successfully")
                    console.print("Knowledge base is now optimized for faster searches", style="bold green")
                    
                    if show_stats:
                        stats = client.get_stats()
                        console.print(f"\nKnowledge Base Statistics:", style="bold")
                        console.print(f"   Total Records: {stats.get('total_records', 0):,}")
                        
                        kb_info = client.describe_knowledge_base()
                        if kb_info:
                            console.print(f"   KB Name: {config.kb.name}")
                            console.print(f"   Status: Indexed & Ready")
                else:
                    progress.update(task, description="Failed to create index")
                    sys.exit(1)
                    
    except Exception as e:
        console.print(f"Index creation failed: {e}", style="red")
        sys.exit(1)


@cli.command("kb:status")
def show_status():
    """Display current knowledge base status, record count, and configuration details."""
    console.print(Panel.fit(
        "[bold blue]Knowledge Base Status[/bold blue]\n"
        "Current status and statistics",
        border_style="blue"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            kb_info = client.describe_knowledge_base()
            stats = client.get_stats()
            
            status_table = Table(show_header=True, header_style="bold magenta")
            status_table.add_column("Property", style="cyan")
            status_table.add_column("Value", style="green")
            
            status_table.add_row("KB Name", config.kb.name)
            status_table.add_row("Total Records", f"{stats.get('total_records', 0):,}")
            status_table.add_row("Embedding Model", config.kb.embedding_model)
            status_table.add_row("Reranking Model", config.kb.reranking_model)
            status_table.add_row("Connection Status", "Connected")
            
            console.print(status_table)
            
            if kb_info:
                console.print(f"\nKnowledge base '{config.kb.name}' is active and ready", style="bold green")
            else:
                console.print(f"\nKnowledge base '{config.kb.name}' may not exist", style="yellow")
                console.print("Run 'kb:init' to create the knowledge base", style="blue")
                
    except Exception as e:
        console.print(f"Status check failed: {e}", style="red")
        sys.exit(1)


@cli.command("kb:reset")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def reset_knowledge_base(force: bool):
    """Drop existing knowledge base and recreate fresh instance, removing all ingested data.
    
    Provides confirmation prompt unless force flag is used. Displays current record count
    before deletion and recreates a clean knowledge base ready for new data ingestion.
    """
    console.print(Panel.fit(
        "[bold red]Knowledge Base Reset[/bold red]\n"
        "This will permanently delete all ingested data",
        border_style="red"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            stats = client.get_stats()
            total_records = stats.get('total_records', 0)
            
            if total_records == 0:
                console.print("Knowledge base is already empty", style="yellow")
                return
            
            if not force:
                console.print(f"\nCurrent knowledge base contains [bold red]{total_records:,}[/bold red] records")
                console.print("This action will permanently delete ALL data in the knowledge base.")
                
                if not click.confirm("\nAre you sure you want to proceed?"):
                    console.print("Reset cancelled", style="yellow")
                    return
            
            console.print(f"\nResetting knowledge base '{config.kb.name}'...", style="blue")
            
            drop_success = client.drop_knowledge_base()
            if not drop_success:
                console.print("Failed to drop existing knowledge base", style="red")
                sys.exit(1)
            
            create_success = client.create_knowledge_base()
            if not create_success:
                console.print("Failed to recreate knowledge base", style="red")
                sys.exit(1)
            
            console.print(f"Knowledge base reset completed successfully!", style="bold green")
            console.print(f"   Deleted {total_records:,} records")
            console.print(f"   Recreated fresh knowledge base")
            console.print(f"   Ready for new ingestion")
            console.print("\nNext step: Use 'kb:ingest <repo_url>' to ingest a repository", style="blue")
            
    except Exception as e:
        console.print(f"Reset failed: {e}", style="red")
        sys.exit(1)


@cli.command("kb:schema")
def show_schema():
    """Display knowledge base schema including column names, types, and purposes."""
    console.print(Panel.fit(
        "[bold blue]Knowledge Base Schema[/bold blue]\n"
        "Column information and structure",
        border_style="blue"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            schema_info = client.get_schema_info()
            
            console.print(f"\nKnowledge Base: [bold]{config.kb.name}[/bold]", style="blue")
            
            column_purposes = {
                'content': ('Content', 'The actual function/class code to embed'),
                'filepath': ('Metadata', 'Where in repo this code resides'),
                'language': ('Metadata', 'Python, JavaScript, Go, etc.'),
                'function_name': ('Metadata', 'Name of the function/class'),
                'repo': ('Metadata', 'GitHub URL or repo name'),
                'last_modified': ('Metadata', 'For freshness filters'),
                'author': ('Metadata', 'From git log, helps with filters'),
                'line_range': ('Metadata', 'e.g. "12-48" for locating in file'),
                'summary': ('Content', 'Short LLM-generated TL;DR'),
                'chunk_id': ('ID', 'Unique identifier for each chunk')
            }
            
            columns_table = Table(show_header=True, header_style="bold magenta")
            columns_table.add_column("Column Name", style="cyan")
            columns_table.add_column("Type", style="green")
            columns_table.add_column("Category", style="yellow")
            columns_table.add_column("Purpose", style="white")
            
            actual_columns = []
            if schema_info and 'columns' in schema_info and schema_info['columns']:
                for col_info in schema_info['columns']:
                    col_name = col_info.get('name', col_info.get('column', col_info.get('Field', '')))
                    if col_name:
                        actual_columns.append(col_info)
            
            if actual_columns:
                console.print(f"Status: [green]Active with {len(actual_columns)} columns[/green]\n")
                
                for col_info in actual_columns:
                    col_name = col_info.get('name', col_info.get('column', col_info.get('Field', '')))
                    col_type = col_info.get('type', col_info.get('Type', 'Unknown'))
                    
                    category, purpose = column_purposes.get(col_name, ('Other', 'Custom column'))
                    columns_table.add_row(col_name, col_type, category, purpose)
            else:
                console.print(f"Status: [yellow]Knowledge base exists but no data ingested yet[/yellow]")
                console.print(f"Showing expected schema based on configuration:\n")
                
                for col in config.kb.all_columns + [config.kb.id_column]:
                    category, purpose = column_purposes.get(col, ('Other', 'Custom column'))
                    columns_table.add_row(col, 'TEXT', category, purpose)
            
            console.print(columns_table)
            
            console.print(f"\nConfiguration Summary:", style="bold")
            
            config_table = Table(show_header=True, header_style="bold cyan")
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="green")
            
            config_table.add_row("Metadata Columns", str(len(config.kb.metadata_columns)))
            config_table.add_row("Content Columns", str(len(config.kb.content_columns)))
            config_table.add_row("ID Column", config.kb.id_column)
            config_table.add_row("Embedding Model", config.kb.embedding_model)
            config_table.add_row("Reranking Model", config.kb.reranking_model)
            
            console.print(config_table)
            
            if actual_columns:
                expected_cols = set(config.kb.all_columns + [config.kb.id_column])
                actual_cols = set(col.get('name', col.get('column', col.get('Field', ''))) for col in actual_columns)
                
                missing_cols = expected_cols - actual_cols
                extra_cols = actual_cols - expected_cols
                
                if missing_cols:
                    console.print(f"\nMissing columns: {', '.join(missing_cols)}", style="yellow")
                if extra_cols:
                    console.print(f"Extra columns: {', '.join(extra_cols)}", style="blue")
                if not missing_cols and not extra_cols:
                    console.print(f"\nSchema matches configuration perfectly", style="bold green")
            else:
                console.print(f"\nOnce data is ingested, this schema will be populated with actual column information.", style="dim")
                    
    except Exception as e:
        console.print(f"Schema retrieval failed: {e}", style="red")
        sys.exit(1)


@cli.command("kb:ingest")
@click.argument("repo_url", required=True)
@click.option("--branch", "-b", default="main", help="Git branch to clone (default: main)")
@click.option("--extensions", default="py,js,ts,java,go,rs,cpp,c,h", help="File extensions to ingest (comma-separated)")
@click.option("--exclude-dirs", default=".git,node_modules,__pycache__,.venv,venv,build,dist", help="Directories to exclude")
@click.option("--batch-size", default=None, type=int, help="Batch size for insertion")
@click.option("--extract-git-info", is_flag=True, help="Extract git author and commit info")
@click.option("--generate-summaries", is_flag=True, help="Generate AI summaries for functions")
@click.option("--dry-run", is_flag=True, help="Show what would be ingested without actually doing it")
@click.option("--cleanup", is_flag=True, default=True, help="Clean up temporary files after ingestion")
def ingest_codebase(repo_url: str, branch: str, extensions: str, exclude_dirs: str, 
                   batch_size: Optional[int], extract_git_info: bool, 
                   generate_summaries: bool, dry_run: bool, cleanup: bool):
    """Clone git repository and parse code files, extracting functions and classes for semantic search."""
    console.print(Panel.fit(
        f"[bold blue]Git Repository Ingestion[/bold blue]\n"
        f"Repository: [italic]{repo_url}[/italic]",
        border_style="blue"
    ))
    
    if not (repo_url.startswith("https://") or repo_url.startswith("git@")):
        console.print("Invalid repository URL. Must start with 'https://' or 'git@'", style="red")
        sys.exit(1)
    
    try:
        console.print("\nData Extraction Plan:", style="bold")
        
        extraction_table = Table(show_header=True, header_style="bold cyan")
        extraction_table.add_column("Data Type", style="yellow")
        extraction_table.add_column("Source", style="green")
        extraction_table.add_column("Status", style="white")
        
        extraction_table.add_row("content", "Function/class code", "✓ Always extracted")
        extraction_table.add_row("filepath", "File system path", "✓ Always extracted")
        extraction_table.add_row("language", "File extension", "✓ Always extracted")
        extraction_table.add_row("function_name", "AST parsing", "✓ Always extracted")
        extraction_table.add_row("repo", "Git remote URL", "✓ Always extracted")
        extraction_table.add_row("last_modified", "Git commit date", "✓ Always extracted")
        
        if extract_git_info:
            extraction_table.add_row("author", "Git commit author", "✓ Enabled")
            extraction_table.add_row("line_range", "AST + line numbers", "✓ Enabled")
        else:
            extraction_table.add_row("author", "Git commit author", "○ Disabled (use --extract-git-info)")
            extraction_table.add_row("line_range", "AST + line numbers", "○ Disabled (use --extract-git-info)")
        
        if generate_summaries:
            extraction_table.add_row("summary", "LLM generation", "✓ Enabled")
        else:
            extraction_table.add_row("summary", "LLM generation", "○ Disabled (use --generate-summaries)")
        
        console.print(extraction_table)
        
        console.print(f"\nIngestion Parameters:", style="bold")
        console.print(f"   Repository: {repo_url}")
        console.print(f"   Branch: {branch}")
        console.print(f"   Extensions: {extensions}")
        console.print(f"   Exclude dirs: {exclude_dirs}")
        console.print(f"   Batch size: {batch_size or config.stress_test.batch_size}")
        console.print(f"   Extract git info: {extract_git_info}")
        console.print(f"   Generate summaries: {generate_summaries}")
        console.print(f"   Cleanup temp files: {cleanup}")
        console.print(f"   Dry run: {dry_run}")
        
        if dry_run:
            console.print("\nDry run mode - no actual ingestion will occur", style="yellow")
            return
        
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            success = client.ingest_git_repository(
                repo_url=repo_url,
                branch=branch,
                extensions=extensions.split(','),
                exclude_dirs=exclude_dirs.split(','),
                batch_size=batch_size or config.stress_test.batch_size,
                extract_git_info=extract_git_info,
                generate_summaries=generate_summaries,
                cleanup=cleanup
            )
            
            if success:
                console.print(f"\nRepository ingestion completed successfully!", style="bold green")
                console.print("Use 'kb:query' to search the ingested code", style="blue")
            else:
                console.print(f"\nRepository ingestion failed", style="bold red")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Ingestion failed: {e}", style="red")
        sys.exit(1)


@cli.command("kb:sync")
@click.argument("repo_url", required=True)
@click.option("--branch", "-b", default="main", help="Git branch to sync (default: main)")
@click.option("--schedule", "-s", default="EVERY 6 HOURS", help="Job schedule (default: EVERY 6 HOURS)")
@click.option("--force", is_flag=True, help="Force recreate sync job if exists")
def create_sync_job(repo_url: str, branch: str, schedule: str, force: bool):
    """Create a scheduled job to sync repository changes every 6 hours."""
    console.print(Panel.fit(
        f"[bold blue]Repository Sync Job[/bold blue]\n"
        f"Repository: [italic]{repo_url}[/italic]\n"
        f"Schedule: [italic]{schedule}[/italic]",
        border_style="blue"
    ))
    
    if not (repo_url.startswith("https://") or repo_url.startswith("git@")):
        console.print("Invalid repository URL. Must start with 'https://' or 'git@'", style="red")
        sys.exit(1)
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            job_name = f"sync_{repo_url.replace('/', '_').replace(':', '_')}"
            
            if force:
                client.delete_sync_job(job_name)
            
            success = client.create_sync_job(
                repo_url=repo_url,
                branch=branch,
                schedule=schedule
            )
            
            if success:
                console.print(f"\nSync job created successfully!", style="bold green")
                console.print(f"Repository: {repo_url}")
                console.print(f"Branch: {branch}")
                console.print(f"Schedule: {schedule}")
                console.print("\nThe job will automatically sync new changes every 6 hours", style="blue")
            else:
                console.print(f"\nFailed to create sync job", style="bold red")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Sync job creation failed: {e}", style="red")
        sys.exit(1)


@cli.command("kb:sync:list")
def list_sync_jobs():
    """List all repository sync jobs and their status."""
    console.print(Panel.fit(
        "[bold blue]Repository Sync Jobs[/bold blue]\n"
        "List of active sync jobs",
        border_style="blue"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            jobs = client.list_sync_jobs()
            
            if not jobs:
                console.print("No sync jobs found", style="yellow")
                return
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Job Name", style="cyan")
            table.add_column("Schedule", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Last Run", style="blue")
            table.add_column("Next Run", style="magenta")
            
            for job in jobs:
                table.add_row(
                    job['name'],
                    job['schedule'],
                    job['status'],
                    job['last_run'],
                    job['next_run']
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"Failed to list sync jobs: {e}", style="red")
        sys.exit(1)


@cli.command("kb:sync:delete")
@click.argument("job_name", required=True)
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def delete_sync_job(job_name: str, force: bool):
    """Delete a repository sync job."""
    console.print(Panel.fit(
        f"[bold red]Delete Sync Job[/bold red]\n"
        f"Job: [italic]{job_name}[/italic]",
        border_style="red"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            if not force:
                if not click.confirm("\nAre you sure you want to delete this sync job?"):
                    console.print("Deletion cancelled", style="yellow")
                    return
            
            success = client.delete_sync_job(job_name)
            
            if success:
                console.print(f"\nSync job deleted successfully!", style="bold green")
            else:
                console.print(f"\nFailed to delete sync job", style="bold red")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Sync job deletion failed: {e}", style="red")
        sys.exit(1)

@cli.command("ai:init")
@click.option("--force", is_flag=True, help="Force recreate AI tables if they exist")
def init_ai_tables(force: bool):
    """Initialize AI tables for code analysis using OpenAI models."""
    console.print(Panel.fit(
        "[bold blue]AI Tables Initialization[/bold blue]\n"
        "Creating AI tables for code analysis",
        border_style="blue"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            if force:
                console.print("Force flag detected, dropping existing AI tables...", style="yellow")
                client.drop_ai_tables()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating AI tables...", total=None)
                
                success = client.create_ai_tables()
                
                if success:
                    progress.update(task, description="AI tables created successfully")
                    
                    console.print("\nAI Tables Created:", style="bold")
                    
                    ai_table_info = [
                        ("code_classifier", "Classifies code purpose (auth, utility, api handler, etc.)"),
                        ("code_explainer", "Explains functions in simple English"),
                        ("docstring_generator", "Generates docstrings for undocumented functions"),
                        ("test_case_outliner", "Suggests test cases for functions"),
                        ("result_rationale", "Explains why search results match queries")
                    ]
                    
                    ai_table = Table(show_header=True, header_style="bold magenta")
                    ai_table.add_column("AI Table", style="cyan")
                    ai_table.add_column("Purpose", style="green")
                    
                    for name, purpose in ai_table_info:
                        ai_table.add_row(name, purpose)
                    
                    console.print(ai_table)
                    
                    console.print(f"\nAI tables are ready for code analysis", style="bold green")
                    console.print("Next step: Use 'ai:analyze' to analyze code with AI", style="blue")
                else:
                    progress.update(task, description="Failed to create AI tables")
                    sys.exit(1)
                    
    except Exception as e:
        console.print(f"AI tables initialization failed: {e}", style="red")
        sys.exit(1)


@cli.command("ai:list")
def list_ai_tables():
    """List all AI tables and their status."""
    console.print(Panel.fit(
        "[bold blue]AI Tables Status[/bold blue]\n"
        "List of available AI tables",
        border_style="blue"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            existing_tables = client.list_ai_tables()
            
            all_tables = [
                ("code_classifier", "Classifies code purpose"),
                ("code_explainer", "Explains functions in simple English"),
                ("docstring_generator", "Generates docstrings"),
                ("test_case_outliner", "Suggests test cases"),
                ("result_rationale", "Explains search matches")
            ]
            
            status_table = Table(show_header=True, header_style="bold magenta")
            status_table.add_column("AI Table", style="cyan")
            status_table.add_column("Purpose", style="white")
            status_table.add_column("Status", style="green")
            
            for name, purpose in all_tables:
                status = "Available" if name in existing_tables else "Not Created"
                status_style = "green" if name in existing_tables else "red"
                status_table.add_row(name, purpose, f"[{status_style}]{status}[/{status_style}]")
            
            console.print(status_table)
            
            if len(existing_tables) == 0:
                console.print(f"\nNo AI tables found. Run 'ai:init' to create them.", style="yellow")
            elif len(existing_tables) < 5:
                console.print(f"\nSome AI tables are missing. Run 'ai:init --force' to recreate all.", style="yellow")
            else:
                console.print(f"\nAll AI tables are available!", style="bold green")
                
    except Exception as e:
        console.print(f"Failed to list AI tables: {e}", style="red")
        sys.exit(1)


@cli.command("ai:analyze")
@click.argument("code_chunk", required=True)
@click.option("--classify", is_flag=True, help="Classify the code purpose")
@click.option("--explain", is_flag=True, help="Explain the code in simple English")
@click.option("--docstring", is_flag=True, help="Generate a docstring")
@click.option("--tests", is_flag=True, help="Suggest test cases")
@click.option("--all", "analyze_all", is_flag=True, help="Run all analysis types")
def analyze_code(code_chunk: str, classify: bool, explain: bool, docstring: bool, tests: bool, analyze_all: bool):
    """Analyze code using AI tables for various insights."""
    console.print(Panel.fit(
        "[bold blue]AI Code Analysis[/bold blue]\n"
        "Analyzing code with AI tables",
        border_style="blue"
    ))
    
    if not any([classify, explain, docstring, tests, analyze_all]):
        console.print("Please specify at least one analysis type or use --all", style="yellow")
        console.print("Available options: --classify, --explain, --docstring, --tests, --all", style="blue")
        return
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            console.print(f"\nCode to analyze:", style="bold")
            console.print(f"```\n{code_chunk}\n```", style="dim")
            
            results_table = Table(show_header=True, header_style="bold magenta")
            results_table.add_column("Analysis Type", style="cyan", width=15)
            results_table.add_column("Result", style="green", width=60)
            
            if classify or analyze_all:
                with console.status("Classifying code purpose..."):
                    purpose = client.classify_code_purpose(code_chunk)
                    results_table.add_row("Purpose", purpose)
            
            if explain or analyze_all:
                with console.status("Explaining code..."):
                    explanation = client.explain_code(code_chunk)
                    results_table.add_row("Explanation", explanation)
            
            if docstring or analyze_all:
                with console.status("Generating docstring..."):
                    generated_docstring = client.generate_docstring(code_chunk)
                    results_table.add_row("Docstring", generated_docstring)
            
            if tests or analyze_all:
                with console.status("Suggesting test cases..."):
                    test_suggestions = client.suggest_test_cases(code_chunk)
                    results_table.add_row("Test Cases", test_suggestions)
            
            console.print("\nAI Analysis Results:", style="bold")
            console.print(results_table)
                    
    except Exception as e:
        console.print(f"Code analysis failed: {e}", style="red")
        sys.exit(1)


@cli.command("ai:reset")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def reset_ai_tables(force: bool):
    """Drop all AI tables and recreate them fresh."""
    console.print(Panel.fit(
        "[bold red]AI Tables Reset[/bold red]\n"
        "This will permanently delete all AI tables",
        border_style="red"
    ))
    
    try:
        with MindsDBClient() as client:
            if not client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            existing_tables = client.list_ai_tables()
            
            if len(existing_tables) == 0:
                console.print("No AI tables found to reset", style="yellow")
                return
            
            if not force:
                console.print(f"\nFound {len(existing_tables)} AI tables: {', '.join(existing_tables)}")
                console.print("This action will permanently delete ALL AI tables.")
                
                if not click.confirm("\nAre you sure you want to proceed?"):
                    console.print("Reset cancelled", style="yellow")
                    return
            
            console.print(f"\nResetting AI tables...", style="blue")
            
            drop_success = client.drop_ai_tables()
            if not drop_success:
                console.print("Failed to drop existing AI tables", style="red")
                sys.exit(1)
            
            create_success = client.create_ai_tables()
            if not create_success:
                console.print("Failed to recreate AI tables", style="red")
                sys.exit(1)
            
            console.print(f"AI tables reset completed successfully!", style="bold green")
            console.print(f"All 5 AI tables have been recreated and are ready for use", style="green")
            
    except Exception as e:
        console.print(f"Reset failed: {e}", style="red")
        sys.exit(1)


@cli.group("agent")
def agent_commands():
    """Agent management and interaction commands for specialized AI assistance."""
    pass


@agent_commands.command("create")
@click.argument("agent_name", required=True)
@click.option("--template", "-t", required=True, help="Agent template to use", 
              type=click.Choice(['code-reviewer', 'architect', 'security-auditor']))
@click.option("--model", help="Override the default model")
@click.option("--force", is_flag=True, help="Recreate agent if it already exists")
def create_agent(agent_name: str, template: str, model: Optional[str], force: bool):
    """Create a specialized agent using a predefined template.
    
    Creates an AI agent that has access to your knowledge base and can provide
    expert analysis in specific domains like code review, architecture, or security.
    """
    console.print(Panel.fit(
        f"[bold blue]Creating Agent: {agent_name}[/bold blue]\n"
        f"Template: {template}\n"
        f"Model: {model or 'default (gpt-4o)'}",
        border_style="blue"
    ))
    
    try:
        with AgentManager() as agent_manager:
            if not agent_manager.client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            if force:
                console.print("Force flag detected, deleting existing agent...", style="yellow")
                agent_manager.delete_agent(agent_name)
            
            kwargs = {}
            if model:
                kwargs['model'] = model
            
            success = agent_manager.create_agent(agent_name, template, **kwargs)
            
            if success:
                console.print(f"\n[bold green]Agent '{agent_name}' created successfully![/bold green]")
                console.print(f"Template: {template}")
                console.print(f"Knowledge Base Access: {config.kb.name}")
                console.print(f"\nUse 'agent ask {agent_name} \"<question>\"' to interact with the agent")
            else:
                console.print(f"Failed to create agent '{agent_name}'", style="red")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Agent creation failed: {e}", style="red")
        sys.exit(1)


@agent_commands.command("list")
@click.option("--show-templates", is_flag=True, help="Show available templates instead of created agents")
def list_agents(show_templates: bool):
    """List all created agents or available agent templates."""
    console.print(Panel.fit(
        "[bold blue]Agent Management[/bold blue]\n" +
        ("Available Templates" if show_templates else "Created Agents"),
        border_style="blue"
    ))
    
    try:
        with AgentManager() as agent_manager:
            if show_templates:
                console.print("\n[bold]Available Agent Templates:[/bold]")
                agent_manager.display_templates_table()
                
                console.print(f"\n[bold blue]Usage:[/bold blue]")
                console.print("python main.py agent create <name> --template <template>")
                console.print("Example: python main.py agent create my-reviewer --template code-reviewer")
                
            else:
                if not agent_manager.client.server:
                    console.print("Failed to connect to MindsDB", style="red")
                    sys.exit(1)
                
                agents = agent_manager.list_agents()
                
                if agents:
                    console.print(f"\n[bold]Created Agents ({len(agents)}):[/bold]")
                    agent_manager.display_agents_table(agents)
                    
                    console.print(f"\n[bold blue]Usage:[/bold blue]")
                    console.print("python main.py agent ask <agent-name> \"<question>\"")
                    console.print("python main.py agent delete <agent-name>")
                else:
                    console.print("No agents created yet", style="yellow")
                    console.print("\nCreate an agent with: python main.py agent create <name> --template <template>")
                    console.print("See available templates with: python main.py agent list --show-templates")
                
    except Exception as e:
        console.print(f"Failed to list agents: {e}", style="red")
        sys.exit(1)


@agent_commands.command("ask")
@click.argument("agent_name", required=True)
@click.argument("question", required=True)
@click.option("--format", "output_format", default="formatted", 
              type=click.Choice(["formatted", "raw", "json"]), 
              help="Output format for the response")
def ask_agent(agent_name: str, question: str, output_format: str):
    """Ask a question to a specialized agent.
    
    Query an agent with natural language questions. The agent will use its
    specialized knowledge and access to your codebase to provide expert answers.
    """
    console.print(Panel.fit(
        f"[bold blue]Querying Agent: {agent_name}[/bold blue]\n"
        f"Question: [italic]{question}[/italic]",
        border_style="blue"
    ))
    
    try:
        with AgentManager() as agent_manager:
            if not agent_manager.client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            agent_info = agent_manager.get_agent_info(agent_name)
            if not agent_info:
                console.print(f"Agent '{agent_name}' not found", style="red")
                console.print("List available agents with: python main.py agent list")
                sys.exit(1)
            
            response = agent_manager.query_agent(agent_name, question)
            
            if response:
                console.print(f"\n[bold green]Agent Response:[/bold green]")
                
                if output_format == "json":
                    console.print(json.dumps({"agent": agent_name, "question": question, "response": response}, indent=2))
                elif output_format == "raw":
                    console.print(response)
                else:
                    console.print(Panel(response, title=f"[bold cyan]{agent_name}[/bold cyan]", 
                                      border_style="green", expand=False))
            else:
                console.print("No response received from agent", style="red")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Agent query failed: {e}", style="red")
        sys.exit(1)


@agent_commands.command("delete")
@click.argument("agent_name", required=True)
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def delete_agent(agent_name: str, force: bool):
    """Delete a created agent."""
    console.print(Panel.fit(
        f"[bold red]Delete Agent: {agent_name}[/bold red]\n"
        "This will permanently remove the agent",
        border_style="red"
    ))
    
    try:
        with AgentManager() as agent_manager:
            if not agent_manager.client.server:
                console.print("Failed to connect to MindsDB", style="red")
                sys.exit(1)
            
            agent_info = agent_manager.get_agent_info(agent_name)
            if not agent_info:
                console.print(f"Agent '{agent_name}' not found", style="yellow")
                return
            
            if not force:
                if not click.confirm(f"\nAre you sure you want to delete agent '{agent_name}'?"):
                    console.print("Deletion cancelled", style="yellow")
                    return
            
            success = agent_manager.delete_agent(agent_name)
            
            if success:
                console.print(f"Agent '{agent_name}' deleted successfully!", style="green")
            else:
                console.print(f"Failed to delete agent '{agent_name}'", style="red")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Agent deletion failed: {e}", style="red")
        sys.exit(1)


@agent_commands.command("review")
@click.argument("code_input", required=True)
@click.option("--agent", default="code_reviewer", help="Name of the code review agent to use")
@click.option("--context", help="Additional context about the code")
@click.option("--focus", help="Comma-separated focus areas (security,performance,style)")
@click.option("--create-agent", is_flag=True, help="Create the code review agent if it doesn't exist")
def review_code(code_input: str, agent: str, context: Optional[str], 
                focus: Optional[str], create_agent: bool):
    """Perform comprehensive code review using the specialized code review agent.
    
    This command uses the CodeReviewAgent to provide detailed code analysis with
    full codebase context. The code_input can be actual code or a function name
    to search for in the knowledge base.
    """
    console.print(Panel.fit(
        "[bold blue]AI Code Review[/bold blue]\n"
        "Analyzing code with full codebase context...",
        border_style="blue"
    ))
    
    try:
        with CodeReviewAgent(agent) as reviewer:
            if create_agent:
                if not reviewer.ensure_agent_exists():
                    console.print("Failed to create code review agent", style="red")
                    sys.exit(1)
            
            focus_areas = []
            if focus:
                focus_areas = [area.strip() for area in focus.split(',')]
            
            if len(code_input.split('\n')) > 1 or any(char in code_input for char in ['{', '}', '(', ')']):
                review_results = reviewer.review_code(code_input, context, focus_areas)
            else:
                console.print(f"Searching for function: [cyan]{code_input}[/cyan]")
                review_results = reviewer.review_function(code_input)
            
            if review_results:
                reviewer.display_review_results(review_results)
            else:
                console.print("Code review failed or returned no results", style="red")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Code review failed: {e}", style="red")
        sys.exit(1)


@agent_commands.command("architecture")
@click.option("--focus", help="Focus area for analysis (patterns, scalability, dependencies)")
@click.option("--agent", default="architecture_analyzer", help="Name of the architecture agent to use")
@click.option("--create-agent", is_flag=True, help="Create the architecture agent if it doesn't exist")
@click.option("--discover-patterns", is_flag=True, help="Focus on design pattern discovery")
def analyze_architecture(focus: Optional[str], agent: str, create_agent: bool, discover_patterns: bool):
    """Perform deep architecture analysis and system understanding.
    
    This command uses the Architecture Discovery Agent to analyze system architecture,
    discover design patterns, assess component dependencies, and evaluate scalability.
    """
    console.print(Panel.fit(
        "[bold blue]Architecture Discovery Analysis[/bold blue]\n"
        "Analyzing system architecture and design patterns...",
        border_style="blue"
    ))
    
    try:
        with ArchitectureDiscoveryAgent(agent) as analyzer:
            if create_agent:
                if not analyzer.ensure_agent_exists():
                    console.print("Failed to create architecture discovery agent", style="red")
                    sys.exit(1)
            
            if discover_patterns:
                console.print("Discovering design patterns in codebase...", style="blue")
                patterns_result = analyzer.discover_design_patterns()
                if patterns_result:
                    console.print("\n[bold green]Design Patterns Discovery Results[/bold green]")
                    
                    if "patterns_by_category" in patterns_result:
                        for pattern_category in patterns_result["patterns_by_category"]:
                            console.print(Panel(
                                pattern_category["details"],
                                title=f"[bold cyan]{pattern_category['category']} Patterns[/bold cyan]",
                                border_style="cyan"
                            ))
                else:
                    console.print("Design pattern discovery failed", style="red")
                    sys.exit(1)
            else:
                console.print(f"Performing architecture analysis...", style="blue")
                if focus:
                    console.print(f"Focus area: [cyan]{focus}[/cyan]")
                
                analysis_result = analyzer.analyze_system_architecture(focus)
                if analysis_result:
                    analyzer.display_architecture_analysis(analysis_result)
                else:
                    console.print("Architecture analysis failed", style="red")
                    sys.exit(1)
                
    except Exception as e:
        console.print(f"Architecture analysis failed: {e}", style="red")
        sys.exit(1)


@agent_commands.command("security")
@click.option("--audit-type", type=click.Choice(["comprehensive", "authentication", "input-validation"]), 
              default="comprehensive", help="Type of security audit to perform")
@click.option("--agent", default="security_auditor", help="Name of the security agent to use")
@click.option("--create-agent", is_flag=True, help="Create the security agent if it doesn't exist")
@click.option("--format", "output_format", default="formatted", 
              type=click.Choice(["formatted", "raw", "json"]), 
              help="Output format for the results")
def security_audit(audit_type: str, agent: str, create_agent: bool, output_format: str):
    """Perform automated security analysis and vulnerability assessment.
    
    This command uses the Security Audit Agent to perform comprehensive security
    analysis including OWASP Top 10 vulnerability detection, authentication review,
    and input validation assessment.
    """
    console.print(Panel.fit(
        f"[bold red]Security Audit Analysis[/bold red]\n"
        f"Audit Type: [italic]{audit_type}[/italic]\n"
        "Analyzing codebase for security vulnerabilities...",
        border_style="red"
    ))
    
    try:
        with SecurityAuditAgent(agent) as auditor:
            if create_agent:
                if not auditor.ensure_agent_exists():
                    console.print("Failed to create security audit agent", style="red")
                    sys.exit(1)
            
            audit_result = None
            
            if audit_type == "comprehensive":
                console.print("Performing comprehensive security audit...", style="blue")
                audit_result = auditor.perform_comprehensive_security_audit()
            elif audit_type == "authentication":
                console.print("Auditing authentication systems...", style="blue")
                audit_result = auditor.audit_authentication_system()
            elif audit_type == "input-validation":
                console.print("Auditing input validation...", style="blue")
                audit_result = auditor.audit_input_validation()
            
            if audit_result:
                if output_format == "json":
                    import json
                    console.print(json.dumps(audit_result, indent=2, default=str))
                elif output_format == "raw":
                    console.print(audit_result.get("raw_response", "No raw response available"))
                else:
                    auditor.display_security_audit_results(audit_result)
            else:
                console.print("Security audit failed or returned no results", style="red")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"Security audit failed: {e}", style="red")
        sys.exit(1)


@agent_commands.command("comprehensive")
@click.option("--include-architecture", is_flag=True, default=True, help="Include architecture analysis")
@click.option("--include-security", is_flag=True, default=True, help="Include security audit")
@click.option("--include-code-review", is_flag=True, default=True, help="Include code review")
@click.option("--sample-function", help="Sample function to review for demonstration")
def comprehensive_analysis(include_architecture: bool, include_security: bool, 
                          include_code_review: bool, sample_function: Optional[str]):
    """Perform comprehensive analysis using all specialized agents.
    
    This command demonstrates the full power of the agent system by running
    architecture discovery, security audit, and code review analysis on the codebase.
    """
    console.print(Panel.fit(
        "[bold magenta]Comprehensive Multi-Agent Analysis[/bold magenta]\n"
        "Running architecture, security, and code review analysis...",
        border_style="magenta"
    ))
    
    results = {
        "architecture": None,
        "security": None,
        "code_review": None
    }
    
    try:
        if include_architecture:
            console.print("\n[bold blue]1. Architecture Discovery Analysis[/bold blue]")
            with ArchitectureDiscoveryAgent() as analyzer:
                if analyzer.ensure_agent_exists():
                    arch_result = analyzer.analyze_system_architecture()
                    if arch_result:
                        analyzer.display_architecture_analysis(arch_result)
                        results["architecture"] = arch_result
                    else:
                        console.print("Architecture analysis failed", style="yellow")
                else:
                    console.print("Failed to create architecture agent", style="yellow")
        
        if include_security:
            console.print("\n[bold red]2. Security Audit Analysis[/bold red]")
            with SecurityAuditAgent() as auditor:
                if auditor.ensure_agent_exists():
                    security_result = auditor.perform_comprehensive_security_audit()
                    if security_result:
                        auditor.display_security_audit_results(security_result)
                        results["security"] = security_result
                    else:
                        console.print("Security audit failed", style="yellow")
                else:
                    console.print("Failed to create security agent", style="yellow")
        
        if include_code_review:
            console.print("\n[bold green]3. Code Review Analysis[/bold green]")
            with CodeReviewAgent() as reviewer:
                if reviewer.ensure_agent_exists():
                    if sample_function:
                        review_result = reviewer.review_function(sample_function)
                    else:
                        sample_code = "def authenticate_user(username, password): return username == 'admin'"
                        console.print(f"Reviewing sample code: [dim]{sample_code}[/dim]")
                        review_result = reviewer.review_code(sample_code)
                    
                    if review_result:
                        reviewer.display_review_results(review_result)
                        results["code_review"] = review_result
                    else:
                        console.print("Code review failed", style="yellow")
                else:
                    console.print("Failed to create code review agent", style="yellow")
        
        console.print("\n[bold magenta]Analysis Summary[/bold magenta]")
        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Analysis Type", style="cyan")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Key Findings", style="white")
        
        for analysis_type, result in results.items():
            if result:
                status = "✓ Completed"
                if analysis_type == "architecture":
                    findings = "System patterns and components analyzed"
                elif analysis_type == "security":
                    total_issues = result.get("total_issues", 0)
                    findings = f"{total_issues} security issues found"
                elif analysis_type == "code_review":
                    findings = "Code quality and security reviewed"
                else:
                    findings = "Analysis completed"
            else:
                status = "✗ Failed"
                findings = "No results generated"
            
            summary_table.add_row(analysis_type.title(), status, findings)
        
        console.print(summary_table)
        
    except Exception as e:
        console.print(f"Comprehensive analysis failed: {e}", style="red")
        sys.exit(1)


def _display_search_results(results: list, output_format: str, query: str, 
                          filters: Dict[str, Any], relevance_threshold: float, use_ai_workflow: bool = False):
    """Display search results in the specified format."""
    from rich.text import Text
    
    if output_format == "json":
        console.print(json.dumps(results, indent=2, default=str))
    elif output_format == "compact":
        for i, result in enumerate(results, 1):
            console.print(f"{i}. [bold]{result.get('filepath', 'N/A')}[/bold]")
            console.print(f"   {result.get('chunk_content', '')[:100]}...")
            console.print(f"   Relevance: {result.get('relevance', 0):.3f}")
            
            if use_ai_workflow:
                if 'ai_purpose' in result:
                    console.print(f"   Purpose: {result['ai_purpose']}")
                if 'ai_explanation' in result:
                    console.print(f"   Explanation: {result['ai_explanation'][:60]}...")
                if 'ai_docstring' in result:
                    console.print(f"   Docstring: {result['ai_docstring'][:60]}...")
                if 'ai_test_cases' in result:
                    console.print(f"   Test Cases: {result['ai_test_cases'][:60]}...")
                if 'ai_match_rationale' in result:
                    console.print(f"   Match Rationale: {result['ai_match_rationale'][:60]}...")
            console.print()
    else:
        terminal_width = console.size.width
        
        if use_ai_workflow:            
            table = Table(show_header=True, header_style="bold magenta", width=terminal_width)
            table.add_column("Rank", style="cyan", min_width=4, max_width=6)
            table.add_column("File", style="green", min_width=20, ratio=2)
            table.add_column("Function", style="blue", min_width=15, ratio=1)
            table.add_column("AI Purpose", style="yellow", min_width=12, ratio=1)
            table.add_column("AI Explanation", style="blue", min_width=30, ratio=3)
            table.add_column("AI Tests", style="magenta", min_width=20, ratio=2)
            table.add_column("Relevance", style="red", min_width=8, max_width=10)
            
            for i, result in enumerate(results, 1):
                filepath = result.get('filepath', 'N/A')
                filepath_text = Text(filepath)
                filepath_text.overflow = "fold"
                    
                function_name = result.get('function_name', 'N/A')
                function_text = Text(function_name)
                function_text.overflow = "fold"
                
                ai_purpose = result.get('ai_purpose', 'N/A')
                purpose_text = Text(ai_purpose)
                purpose_text.overflow = "fold"
                
                ai_explanation = result.get('ai_explanation', 'N/A')
                explanation_text = Text(ai_explanation)
                explanation_text.overflow = "fold"
                
                ai_tests = result.get('ai_test_cases', 'N/A')
                tests_text = Text(ai_tests)
                tests_text.overflow = "fold"
                
                table.add_row(
                    str(i),
                    filepath_text,
                    function_text,
                    purpose_text,
                    explanation_text,
                    tests_text,
                    f"{result.get('relevance', 0):.3f}"
                )
            
            console.print(table)
            
            console.print(f"\nAdditional AI Analysis:", style="bold blue")
            for i, result in enumerate(results, 1):
                console.print(f"\n[bold cyan]Result {i} - {result.get('function_name', 'N/A')}:[/bold cyan]")
                
                if 'ai_docstring' in result and result['ai_docstring'] != 'N/A':
                    docstring = result['ai_docstring']
                    console.print(f"  [green]Generated Docstring:[/green] {docstring}")
                
                if 'ai_match_rationale' in result and result['ai_match_rationale'] != 'N/A':
                    rationale = result['ai_match_rationale']
                    console.print(f"  [cyan]Match Rationale:[/cyan] {rationale}")
        else:
            table = Table(show_header=True, header_style="bold magenta", width=terminal_width)
            table.add_column("Rank", style="cyan", min_width=4, max_width=6)
            table.add_column("File", style="green", min_width=25, ratio=2)
            table.add_column("Function", style="blue", min_width=15, ratio=1)
            table.add_column("Content", style="white", min_width=40, ratio=4)
            table.add_column("Relevance", style="yellow", min_width=8, max_width=10)
            table.add_column("Language", style="magenta", min_width=8, max_width=12)
            
            for i, result in enumerate(results, 1):
                content = result.get('chunk_content', '')
                content_text = Text(content)
                content_text.overflow = "fold"
                
                filepath = result.get('filepath', 'N/A')
                filepath_text = Text(filepath)
                filepath_text.overflow = "fold"
                
                function_name = result.get('function_name', 'N/A')
                function_text = Text(function_name)
                function_text.overflow = "fold"
                
                language = result.get('language', 'N/A')
                
                table.add_row(
                    str(i),
                    filepath_text,
                    function_text,
                    content_text,
                    f"{result.get('relevance', 0):.3f}",
                    language
                )
            
            console.print(table)
    
    console.print(f"\nSearch Summary:", style="bold")
    console.print(f"   Query: {query}")
    console.print(f"   Results: {len(results)}")
    console.print(f"   Filters: {filters if filters else 'None'}")
    console.print(f"   Min Relevance: {relevance_threshold}")
    if use_ai_workflow:
        console.print(f"   AI Enhancement: Enabled", style="green")
    else:
        console.print(f"   AI Enhancement: Disabled (use --ai-* flags)", style="dim")


if __name__ == "__main__":
    cli() 