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
    """Initialize MindsDB Knowledge Base with embedding/reranking models for semantic code search."""
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
def query_kb(query: str, language: Optional[str], filepath: Optional[str], 
             function: Optional[str], repo: Optional[str], author: Optional[str],
             since: Optional[str], limit: int, relevance_threshold: float, output_format: str):
    """Perform semantic search with natural language queries and optional metadata filtering."""
    console.print(Panel.fit(
        f"[bold blue]Semantic Search[/bold blue]\n"
        f"Query: [italic]{query}[/italic]",
        border_style="blue"
    ))
    
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
            
            _display_search_results(results, output_format, query, filters, relevance_threshold)
            
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
    """Drop existing knowledge base and recreate fresh instance, removing all ingested data."""
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
                
                import click
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
            
            console.print(f"✅ Knowledge base reset completed successfully!", style="bold green")
            console.print(f"   • Deleted {total_records:,} records")
            console.print(f"   • Recreated fresh knowledge base")
            console.print(f"   • Ready for new ingestion")
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


def _display_search_results(results: list, output_format: str, query: str, 
                          filters: Dict[str, Any], relevance_threshold: float):
    """Display search results in the specified format."""
    if output_format == "json":
        console.print(json.dumps(results, indent=2, default=str))
    elif output_format == "compact":
        for i, result in enumerate(results, 1):
            console.print(f"{i}. [bold]{result.get('filepath', 'N/A')}[/bold]")
            console.print(f"   {result.get('chunk_content', '')[:100]}...")
            console.print(f"   Relevance: {result.get('relevance', 0):.3f}\n")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="cyan", width=4)
        table.add_column("File", style="green", width=25)
        table.add_column("Function", style="blue", width=15)
        table.add_column("Content", style="white", width=40)
        table.add_column("Relevance", style="yellow", width=8)
        table.add_column("Language", style="magenta", width=8)
        
        for i, result in enumerate(results, 1):
            content = result.get('chunk_content', '')
            if len(content) > 37:
                content = content[:37] + "..."
            
            filepath = result.get('filepath', 'N/A')
            function_name = result.get('function_name', 'N/A')
            language = result.get('language', 'N/A')
            
            table.add_row(
                str(i),
                filepath,
                function_name,
                content,
                f"{result.get('relevance', 0):.3f}",
                language
            )
        
        console.print(table)
    
    console.print(f"\nSearch Summary:", style="bold")
    console.print(f"   Query: {query}")
    console.print(f"   Results: {len(results)}")
    console.print(f"   Filters: {filters if filters else 'None'}")
    console.print(f"   Min Relevance: {relevance_threshold}")


if __name__ == "__main__":
    cli() 