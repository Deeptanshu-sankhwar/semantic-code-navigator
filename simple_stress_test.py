#!/usr/bin/env python3
"""
Simple Stress Test for Semantic Code Navigator
Does exactly what it should: ingest -> query -> AI -> reset -> next repo
"""

import subprocess
import time
from rich.console import Console
from rich.panel import Panel

console = Console()

# Simple list of repos to test
REPOS = [
    ("https://github.com/miguelgrinberg/flasky", "master", 20),
    ("https://github.com/gin-gonic/examples", "master", 20), 
    ("https://github.com/expressjs/express", "main", 25),
    ("https://github.com/kbknapp/clap", "master", 25),
    ("https://github.com/vuejs/vue", "main", 30),
]

# Test queries
QUERIES = [
    "authentication and login",
    "database connection", 
    "error handling",
    "API routing",
    "validation"
]

def run_command(cmd):
    """Execute command and display output in real-time.
    
    Runs the specified command and streams all output directly to the console
    in real-time, providing immediate feedback on command execution progress.
    """
    console.print(f"\nRunning: [bold cyan]{cmd}[/bold cyan]")
    
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.rstrip())
    
    return_code = process.poll()
    return return_code == 0

def test_repo(repo_url, branch, batch_size):
    """Execute complete workflow test on a single repository.
    
    Performs the full semantic code navigator workflow: KB reset, initialization,
    repository ingestion, basic search, AI table setup, and AI-enhanced search.
    """
    repo_name = repo_url.split('/')[-1]
    
    console.print(Panel.fit(
        f"[bold blue]Testing Repository: {repo_name}[/bold blue]\n"
        f"URL: {repo_url}\n"
        f"Branch: {branch}\n"
        f"Batch Size: {batch_size}",
        border_style="blue"
    ))
    
    console.print("\n[bold yellow]Step 1: Reset Knowledge Base[/bold yellow]")
    if not run_command("python -m src.cli kb:reset --force"):
        console.print("KB reset failed", style="red")
        return False
    
    console.print("\n[bold yellow]Step 2: Initialize Knowledge Base[/bold yellow]")
    if not run_command("python -m src.cli kb:init"):
        console.print("KB init failed", style="red")
        return False
    
    console.print("\n[bold yellow]Step 3: Ingest Repository[/bold yellow]")
    ingest_cmd = f"python -m src.cli kb:ingest {repo_url} --branch {branch} --batch-size {batch_size} --extract-git-info"
    if not run_command(ingest_cmd):
        console.print("Ingestion failed", style="red")
        return False
    
    console.print("\n[bold yellow]Step 4: Test Basic Search[/bold yellow]")
    query = QUERIES[0]
    search_cmd = f'python -m src.cli kb:query "{query}" --limit 3'
    if not run_command(search_cmd):
        console.print("Search failed", style="red")
        return False
    
    console.print("\n[bold yellow]Step 5: Initialize AI Tables[/bold yellow]")
    if not run_command("python -m src.cli ai:init --force"):
        console.print("AI tables init failed", style="red")
        return False
    
    console.print("\n[bold yellow]Step 6: Test AI-Enhanced Search[/bold yellow]")
    ai_search_cmd = f'python -m src.cli kb:query "{query}" --limit 2 --ai-all'
    if not run_command(ai_search_cmd):
        console.print("AI search failed", style="red")
        return False
    
    console.print(f"\n[bold green]Successfully completed {repo_name}![/bold green]")
    return True

def main():
    """Execute the complete simple stress test suite.
    
    Runs the semantic code navigator workflow on multiple repositories
    and provides summary statistics on completion rates and performance.
    """
    console.print(Panel.fit(
        "[bold blue]Simple Semantic Code Navigator Stress Test[/bold blue]\n"
        f"Testing {len(REPOS)} repositories with full CLI output",
        border_style="blue"
    ))
    
    successful = 0
    total = len(REPOS)
    
    for i, (repo_url, branch, batch_size) in enumerate(REPOS, 1):
        console.print(f"\n{'='*60}")
        console.print(f"[bold cyan]Repository {i}/{total}[/bold cyan]")
        console.print(f"{'='*60}")
        
        if test_repo(repo_url, branch, batch_size):
            successful += 1
        else:
            console.print(f"[bold red]Failed repository {i}/{total}[/bold red]")
        
        if i < total:
            console.print(f"\nWaiting 5 seconds before next repository...")
            time.sleep(5)
    
    console.print(f"\n{'='*60}")
    console.print(Panel.fit(
        f"[bold blue]Stress Test Complete![/bold blue]\n"
        f"Successful: {successful}/{total}\n"
        f"Success Rate: {(successful/total)*100:.1f}%",
        border_style="green" if successful == total else "yellow"
    ))

if __name__ == "__main__":
    main() 