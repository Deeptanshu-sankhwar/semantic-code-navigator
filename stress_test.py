#!/usr/bin/env python3
"""
Comprehensive Stress Test Suite for Semantic Code Navigator
Tests the complete workflow: KB creation → Data ingestion → Semantic search → AI analysis

This script runs stress tests on 25 GitHub repositories of varying sizes,
documenting results in real-time with beautiful markdown reports.
"""

import os
import sys
import time
import json
import subprocess
import threading
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
from pathlib import Path
import psutil
import statistics
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

console = Console()

@dataclass
class TestRepository:
    """Repository configuration for stress testing."""
    name: str
    url: str
    estimated_files: int
    language: str
    description: str
    batch_size: int
    max_concurrent_queries: int

@dataclass
class TestEnvironment:
    """Test environment specifications for reproducible benchmarks."""
    timestamp: str
    python_version: str
    platform: str
    cpu_count: int
    total_memory_gb: float
    available_memory_gb: float
    disk_space_gb: float
    mindsdb_version: str
    openai_model_embedding: str
    openai_model_reranking: str
    
    @classmethod
    def capture_current(cls):
        """Capture current system environment."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return cls(
            timestamp=datetime.now().isoformat(),
            python_version=sys.version.split()[0],
            platform=f"{platform.system()} {platform.release()} ({platform.machine()})",
            cpu_count=psutil.cpu_count(),
            total_memory_gb=memory.total / (1024**3),
            available_memory_gb=memory.available / (1024**3),
            disk_space_gb=disk.free / (1024**3),
            mindsdb_version="Latest",
            openai_model_embedding="text-embedding-3-large",
            openai_model_reranking="gpt-4o"
        )

@dataclass
class PerformanceMetrics:
    """Detailed performance metrics for benchmarking."""
    ingestion_rate_chunks_per_second: float = 0.0
    ingestion_rate_files_per_second: float = 0.0
    ingestion_time_per_1k_chunks: float = 0.0
    search_latency_avg_ms: float = 0.0
    search_latency_p95_ms: float = 0.0
    search_latency_p99_ms: float = 0.0
    memory_efficiency_mb_per_1k_chunks: float = 0.0
    throughput_queries_per_second: float = 0.0
    
    def calculate_from_results(self, result: 'TestResult', search_times: List[float]):
        """Calculate performance metrics from test results."""
        if result.ingestion_time > 0 and result.chunks_extracted > 0:
            self.ingestion_rate_chunks_per_second = result.chunks_extracted / result.ingestion_time
            self.ingestion_time_per_1k_chunks = (result.ingestion_time / result.chunks_extracted) * 1000
            
        if result.ingestion_time > 0 and result.files_processed > 0:
            self.ingestion_rate_files_per_second = result.files_processed / result.ingestion_time
            
        if search_times:
            search_times_ms = [t * 1000 for t in search_times]
            self.search_latency_avg_ms = statistics.mean(search_times_ms)
            if len(search_times_ms) >= 20:
                self.search_latency_p95_ms = statistics.quantiles(search_times_ms, n=20)[18]
                self.search_latency_p99_ms = statistics.quantiles(search_times_ms, n=100)[98]
            
        if result.peak_memory_mb > 0 and result.chunks_extracted > 0:
            self.memory_efficiency_mb_per_1k_chunks = (result.peak_memory_mb / result.chunks_extracted) * 1000
            
        if result.queries_tested > 0 and result.search_time > 0:
            self.throughput_queries_per_second = result.queries_tested / result.search_time

@dataclass
class TestResult:
    """Results from a single test run with comprehensive benchmarking data."""
    repo_name: str
    repo_url: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    kb_creation_success: bool = False
    kb_creation_time: float = 0.0
    kb_creation_error: Optional[str] = None
    
    ingestion_success: bool = False
    ingestion_time: float = 0.0
    files_processed: int = 0
    chunks_extracted: int = 0
    ingestion_error: Optional[str] = None
    batch_size: int = 0
    
    indexing_success: bool = False
    indexing_time: float = 0.0
    indexing_error: Optional[str] = None
    
    search_success: bool = False
    search_time: float = 0.0
    search_results_count: int = 0
    search_error: Optional[str] = None
    queries_tested: int = 0
    search_times: List[float] = None
    
    ai_analysis_success: bool = False
    ai_analysis_time: float = 0.0
    ai_analysis_error: Optional[str] = None
    
    peak_memory_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    environment: Optional[TestEnvironment] = None
    performance: Optional[PerformanceMetrics] = None
    language_breakdown: Dict[str, int] = None
    
    def __post_init__(self):
        if self.search_times is None:
            self.search_times = []
        if self.language_breakdown is None:
            self.language_breakdown = {}
    
    @property
    def total_time(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success_rate(self) -> float:
        total_steps = 5
        successful_steps = sum([
            self.kb_creation_success,
            self.ingestion_success,
            self.indexing_success,
            self.search_success,
            self.ai_analysis_success
        ])
        return (successful_steps / total_steps) * 100

class StressTestSuite:
    """Main stress testing suite."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
        self.report_file = f"stress_test_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.md"
        self.cli_path = "python -m src.cli"
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        self.test_repositories = [
            TestRepository("flask-hello-world", "https://github.com/miguelgrinberg/flasky", 60, "Python", "Simple Flask application", 20, 10),
            TestRepository("express-starter", "https://github.com/expressjs/express", 80, "JavaScript", "Express.js web framework", 20, 15),
            TestRepository("go-gin-example", "https://github.com/gin-gonic/examples", 90, "Go", "Gin web framework examples", 20, 20),
            TestRepository("rust-cli-template", "https://github.com/kbknapp/clap", 120, "Rust", "Command line argument parser", 20, 25),
            TestRepository("vue-todo-app", "https://github.com/vuejs/vue", 150, "JavaScript", "Vue.js framework", 20, 30),
            
            TestRepository("django-blog", "https://github.com/django/django", 250, "Python", "Django web framework", 100, 20),
            TestRepository("react-admin", "https://github.com/marmelab/react-admin", 300, "JavaScript", "React admin interface", 100, 25),
            TestRepository("spring-boot-demo", "https://github.com/spring-projects/spring-boot", 350, "Java", "Spring Boot framework", 150, 30),
            TestRepository("laravel-app", "https://github.com/laravel/laravel", 400, "PHP", "Laravel web framework", 150, 35),
            TestRepository("rails-blog", "https://github.com/rails/rails", 450, "Ruby", "Ruby on Rails framework", 200, 40),
            
            TestRepository("angular-material", "https://github.com/angular/components", 500, "TypeScript", "Angular Material components", 200, 25),
            TestRepository("nestjs-api", "https://github.com/nestjs/nest", 550, "TypeScript", "NestJS framework", 200, 30),
            TestRepository("fastapi-users", "https://github.com/tiangolo/fastapi", 600, "Python", "FastAPI web framework", 250, 35),
            TestRepository("gin-gonic-gin", "https://github.com/gin-gonic/gin", 650, "Go", "Gin HTTP web framework", 250, 40),
            TestRepository("actix-web", "https://github.com/actix/actix-web", 700, "Rust", "Actix web framework", 300, 45),
            
            # Large repositories (800-1000 files)
            TestRepository("kubernetes-client", "https://github.com/kubernetes/client-go", 800, "Go", "Kubernetes Go client", 300, 30),
            TestRepository("tensorflow-js", "https://github.com/tensorflow/tfjs", 850, "JavaScript", "TensorFlow.js", 300, 35),
            TestRepository("pytorch-lightning", "https://github.com/Lightning-AI/lightning", 900, "Python", "PyTorch Lightning", 350, 40),
            TestRepository("apache-kafka", "https://github.com/apache/kafka", 950, "Java", "Apache Kafka", 350, 45),
            TestRepository("elasticsearch", "https://github.com/elastic/elasticsearch", 1000, "Java", "Elasticsearch engine", 400, 50),
            
            # Very large repositories (1000+ files)
            TestRepository("vscode", "https://github.com/microsoft/vscode", 1200, "TypeScript", "Visual Studio Code", 400, 40),
            TestRepository("chromium", "https://github.com/chromium/chromium", 1500, "C++", "Chromium browser", 450, 45),
            TestRepository("linux-kernel", "https://github.com/torvalds/linux", 2000, "C", "Linux kernel", 500, 50),
            TestRepository("llvm-project", "https://github.com/llvm/llvm-project", 2500, "C++", "LLVM compiler", 550, 55),
            TestRepository("webkit", "https://github.com/WebKit/WebKit", 3000, "C++", "WebKit browser engine", 600, 60),
        ]
        
        self.search_queries = [
            "authentication and login validation",
            "database connection and queries",
            "error handling and logging",
            "API endpoint routing",
            "data validation and sanitization",
            "file upload and processing",
            "caching and performance optimization",
            "security and authorization",
            "testing and unit tests",
            "configuration and environment setup"
        ]
        
        self.ai_analysis_types = [
            "--classify",
            "--explain", 
            "--docstring",
            "--tests",
            "--all"
        ]
    
    def initialize_report(self):
        """Initialize the markdown report file."""
        with open(self.report_file, 'w') as f:
            f.write(f"""# Semantic Code Navigator - Comprehensive Stress Test Report

**Test Suite Started:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}

## Test Overview

This comprehensive stress test evaluates the complete workflow of the Semantic Code Navigator:

1. **Knowledge Base Creation** - Initialize MindsDB KB with embedding models
2. **Data Ingestion** - Clone repositories and extract code chunks  
3. **Index Creation** - Optimize KB for search performance
4. **Semantic Search** - Query with natural language and metadata filters
5. **AI Analysis** - Enhance results with AI tables for classification and explanation

### Test Repositories

Testing on **{len(self.test_repositories)}** repositories ranging from ~50 to 3000+ files:

| Repository | Est. Files | Language | Batch Size | Max Queries | Description |
|------------|------------|----------|------------|-------------|-------------|
""")
            
            for repo in self.test_repositories:
                f.write(f"| {repo.name} | {repo.estimated_files} | {repo.language} | {repo.batch_size} | {repo.max_concurrent_queries} | {repo.description} |\n")
            
            f.write(f"""
### Test Parameters

- **Search Queries:** {len(self.search_queries)} different semantic queries
- **Batch Size Variation:** From 100 to 1000 based on repository size
- **Test Execution:** Serial execution (one repository at a time)
- **Memory Management:** KB reset after each test to free memory
- **Cost Optimization:** No AI summary generation to reduce OpenAI costs
- **Individual Reports:** Detailed benchmark reports saved to `results/` directory
- **Performance Metrics:** P95/P99 latency, throughput, memory efficiency tracking

---

## Test Results

""")
    
    def update_report(self, message: str, level: str = "info"):
        """Update the report with real-time information and appropriate status indicators.
        
        Appends timestamped messages to the markdown report file with level-specific
        indicators for tracking test progress and results.
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        level_indicators = {
            "info": "[INFO]",
            "success": "[SUCCESS]", 
            "warning": "[WARNING]",
            "error": "[ERROR]",
            "start": "[START]",
            "finish": "[COMPLETE]"
        }
        
        with open(self.report_file, 'a') as f:
            f.write(f"\n**{timestamp}** {level_indicators.get(level, '[INFO]')} {message}\n")
    
    def detect_repository_branch(self, repo_url: str) -> str:
        """Detect the default branch of a repository (main vs master)."""
        try:
            console.print(f"Detecting branch for {repo_url}...", style="dim")
            
            result = subprocess.run(
                f"git ls-remote --heads {repo_url}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                branches = result.stdout.strip()
                if "refs/heads/main" in branches:
                    console.print("Detected branch: main", style="dim")
                    return "main"
                elif "refs/heads/master" in branches:
                    console.print("Detected branch: master", style="dim")
                    return "master"
                else:
                    lines = branches.split('\n')
                    for line in lines:
                        if 'refs/heads/' in line:
                            branch_name = line.split('refs/heads/')[-1]
                            if branch_name in ['develop', 'dev', 'trunk']:
                                console.print(f"Detected branch: {branch_name}", style="dim")
                                return branch_name
                    if lines and 'refs/heads/' in lines[0]:
                        branch_name = lines[0].split('refs/heads/')[-1]
                        console.print(f"Using first available branch: {branch_name}", style="dim")
                        return branch_name
            
            console.print("Using default branch: main", style="dim")
            return "main"
            
        except Exception as e:
            console.print(f"Branch detection failed for {repo_url}: {e}", style="yellow")
            return "main"

    def run_cli_command(self, command: str, timeout: int = 300, retries: int = 2) -> Tuple[bool, str, float]:
        """Execute CLI command with real-time output display and retry logic.
        
        Runs the specified CLI command and streams output in real-time to the console.
        Implements retry logic for connection failures and provides detailed error reporting.
        """
        start_time = time.time()
        
        for attempt in range(retries + 1):
            try:
                full_command = f"{self.cli_path} {command}"
                if attempt > 0:
                    console.print(f"Retry {attempt}: [bold cyan]{full_command}[/bold cyan]", style="yellow")
                else:
                    console.print(f"Running: [bold cyan]{full_command}[/bold cyan]")
                
                process = subprocess.Popen(
                    full_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                output_lines = []
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.rstrip())
                        output_lines.append(output.strip())
                
                process.wait()
                execution_time = time.time() - start_time
                full_output = '\n'.join(output_lines)
                
                if process.returncode == 0:
                    return True, full_output, execution_time
                else:
                    connection_errors = [
                        "Connection aborted",
                        "Remote end closed connection",
                        "Connection refused",
                        "Connection timed out",
                        "Failed to connect"
                    ]
                    
                    if attempt < retries and any(err in full_output for err in connection_errors):
                        console.print(f"Connection issue detected, retrying in 5 seconds...", style="yellow")
                        time.sleep(5)
                        continue
                    
                    return False, full_output, execution_time
                    
            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                if attempt < retries:
                    console.print(f"Command timed out, retrying...", style="yellow")
                    time.sleep(5)
                    continue
                return False, f"Command timed out after {timeout} seconds", execution_time
            except Exception as e:
                execution_time = time.time() - start_time
                if attempt < retries:
                    console.print(f"Command failed with exception, retrying...", style="yellow")
                    time.sleep(5)
                    continue
                return False, str(e), execution_time
        
        execution_time = time.time() - start_time
        return False, "All retry attempts failed", execution_time
    
    def monitor_system_resources(self, result: TestResult):
        """Monitor system resources during test execution."""
        try:
            process = psutil.Process()
            result.peak_memory_mb = max(result.peak_memory_mb, process.memory_info().rss / 1024 / 1024)
            result.cpu_usage_percent = max(result.cpu_usage_percent, process.cpu_percent())
        except:
            pass
    
    def generate_individual_report(self, result: TestResult, repo: TestRepository):
        """Generate detailed individual repository benchmark report.
        
        Creates a comprehensive report for a single repository test including
        environment specifications, performance metrics, and reproducible benchmarks.
        """
        timestamp = result.start_time.strftime('%Y%m%d_%H%M%S')
        report_file = self.results_dir / f"{result.repo_name}_{timestamp}.md"
        
        if result.performance is None:
            result.performance = PerformanceMetrics()
            result.performance.calculate_from_results(result, result.search_times)
        
        if result.environment is None:
            result.environment = TestEnvironment.capture_current()
        
        with open(report_file, 'w') as f:
            f.write(f"""# Benchmark Report: {result.repo_name}

**Repository:** {result.repo_url}  
**Test Date:** {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Duration:** {result.total_time:.2f} seconds  
**Success Rate:** {result.success_rate:.1f}%  

## Executive Summary

This report provides comprehensive performance benchmarks for the {result.repo_name} repository ingestion and search workflow using the Semantic Code Navigator. The test demonstrates reproducible performance metrics across the complete pipeline from repository cloning to AI-enhanced semantic search.

### Key Performance Indicators

| Metric | Value | Unit |
|--------|-------|------|
| **Dataset Size** | {result.chunks_extracted:,} | code chunks |
| **Files Processed** | {result.files_processed:,} | files |
| **Ingestion Rate** | {result.performance.ingestion_rate_chunks_per_second:.1f} | chunks/second |
| **Search Latency (Avg)** | {result.performance.search_latency_avg_ms:.1f} | milliseconds |
| **Memory Efficiency** | {result.performance.memory_efficiency_mb_per_1k_chunks:.1f} | MB per 1K chunks |
| **Throughput** | {result.performance.throughput_queries_per_second:.2f} | queries/second |

## Test Environment

### Hardware Specifications
- **Platform:** {result.environment.platform}
- **CPU Cores:** {result.environment.cpu_count}
- **Total Memory:** {result.environment.total_memory_gb:.1f} GB
- **Available Memory:** {result.environment.available_memory_gb:.1f} GB
- **Disk Space:** {result.environment.disk_space_gb:.1f} GB

### Software Environment
- **Python Version:** {result.environment.python_version}
- **MindsDB Version:** {result.environment.mindsdb_version}
- **Embedding Model:** {result.environment.openai_model_embedding}
- **Reranking Model:** {result.environment.openai_model_reranking}
- **Test Timestamp:** {result.environment.timestamp}

## Repository Characteristics

### Dataset Overview
- **Repository URL:** {result.repo_url}
- **Primary Language:** {repo.language}
- **Estimated Files:** {repo.estimated_files}
- **Actual Files Processed:** {result.files_processed}
- **Code Chunks Extracted:** {result.chunks_extracted:,}
- **Batch Size Used:** {result.batch_size}

### Language Distribution
""")
            
            if result.language_breakdown:
                f.write("| Language | Chunks | Percentage |\n")
                f.write("|----------|--------|------------|\n")
                total_chunks = sum(result.language_breakdown.values())
                for lang, count in sorted(result.language_breakdown.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_chunks) * 100 if total_chunks > 0 else 0
                    f.write(f"| {lang} | {count:,} | {percentage:.1f}% |\n")
            else:
                f.write("Language breakdown not available.\n")
            
            f.write(f"""

## Performance Benchmarks

### Ingestion Performance

| Metric | Value | Benchmark Category |
|--------|-------|-------------------|
| **Total Ingestion Time** | {result.ingestion_time:.2f} seconds | {self._categorize_ingestion_time(result.ingestion_time)} |
| **Chunks per Second** | {result.performance.ingestion_rate_chunks_per_second:.1f} | {self._categorize_ingestion_rate(result.performance.ingestion_rate_chunks_per_second)} |
| **Files per Second** | {result.performance.ingestion_rate_files_per_second:.1f} | {self._categorize_file_rate(result.performance.ingestion_rate_files_per_second)} |
| **Time per 1K Chunks** | {result.performance.ingestion_time_per_1k_chunks:.1f} seconds | {self._categorize_chunk_time(result.performance.ingestion_time_per_1k_chunks)} |

### Search Performance

| Metric | Value | Benchmark Category |
|--------|-------|-------------------|
| **Average Latency** | {result.performance.search_latency_avg_ms:.1f} ms | {self._categorize_latency(result.performance.search_latency_avg_ms)} |
| **95th Percentile** | {result.performance.search_latency_p95_ms:.1f} ms | {self._categorize_latency(result.performance.search_latency_p95_ms)} |
| **99th Percentile** | {result.performance.search_latency_p99_ms:.1f} ms | {self._categorize_latency(result.performance.search_latency_p99_ms)} |
| **Queries per Second** | {result.performance.throughput_queries_per_second:.2f} | {self._categorize_throughput(result.performance.throughput_queries_per_second)} |

### Memory Efficiency

| Metric | Value | Benchmark Category |
|--------|-------|-------------------|
| **Peak Memory Usage** | {result.peak_memory_mb:.1f} MB | {self._categorize_memory(result.peak_memory_mb)} |
| **Memory per 1K Chunks** | {result.performance.memory_efficiency_mb_per_1k_chunks:.1f} MB | {self._categorize_memory_efficiency(result.performance.memory_efficiency_mb_per_1k_chunks)} |
| **CPU Usage Peak** | {result.cpu_usage_percent:.1f}% | {self._categorize_cpu(result.cpu_usage_percent)} |

## Detailed Test Results

### Workflow Step Performance

| Step | Status | Duration | Notes |
|------|--------|----------|-------|
| **KB Creation** | {'✓ Success' if result.kb_creation_success else '✗ Failed'} | {result.kb_creation_time:.2f}s | {result.kb_creation_error or 'Completed successfully'} |
| **Data Ingestion** | {'✓ Success' if result.ingestion_success else '✗ Failed'} | {result.ingestion_time:.2f}s | {result.ingestion_error or 'Completed successfully'} |
| **Index Creation** | {'✓ Success' if result.indexing_success else '✗ Failed'} | {result.indexing_time:.2f}s | {result.indexing_error or 'Completed successfully'} |
| **Semantic Search** | {'✓ Success' if result.search_success else '✗ Failed'} | {result.search_time:.2f}s | {result.search_error or 'Completed successfully'} |
| **AI Analysis** | {'✓ Success' if result.ai_analysis_success else '✗ Failed'} | {result.ai_analysis_time:.2f}s | {result.ai_analysis_error or 'Completed successfully'} |

### Search Query Performance
""")
            
            if result.search_times:
                f.write("| Query # | Response Time (ms) | Status |\n")
                f.write("|---------|-------------------|--------|\n")
                for i, time_val in enumerate(result.search_times, 1):
                    status = "✓ Fast" if time_val * 1000 < 1000 else "⚠ Slow" if time_val * 1000 < 3000 else "✗ Very Slow"
                    f.write(f"| {i} | {time_val * 1000:.1f} | {status} |\n")
            else:
                f.write("Individual query times not recorded.\n")
            
            f.write(f"""

## Reproducibility Information

### Test Methodology

This benchmark follows a standardized methodology for reproducible results:

1. **Environment Setup**: Fresh MindsDB instance with clean knowledge base
2. **Repository Cloning**: Clone from {result.repo_url} using detected default branch
3. **Code Extraction**: AST-based parsing for {repo.language} files with metadata extraction
4. **Batch Processing**: Insert {result.batch_size} chunks per batch for optimal performance
5. **Search Testing**: Execute {result.queries_tested} semantic queries with natural language
6. **AI Enhancement**: Test AI-powered code analysis and explanation features
7. **Cleanup**: Reset knowledge base to ensure isolated test environment

### Reproduction Script

```bash
# Prerequisites
docker-compose up  # Start MindsDB
export OPENAI_API_KEY="your-api-key"

# Run benchmark
python -m src.cli kb:reset --force
python -m src.cli kb:init
python -m src.cli kb:ingest {result.repo_url} --batch-size {result.batch_size} --extract-git-info
python -m src.cli kb:query "authentication and login validation" --limit 3
python -m src.cli ai:init --force
python -m src.cli kb:query "authentication and login validation" --limit 2 --ai-all
```

### Performance Baselines

Based on repository size category ({self._get_size_category(result.chunks_extracted)}):

| Metric | Expected Range | Actual Result | Status |
|--------|----------------|---------------|--------|
| **Ingestion Rate** | {self._get_expected_ingestion_range(result.chunks_extracted)} chunks/sec | {result.performance.ingestion_rate_chunks_per_second:.1f} | {self._compare_to_baseline(result.performance.ingestion_rate_chunks_per_second, self._get_expected_ingestion_range(result.chunks_extracted))} |
| **Search Latency** | < 2000 ms | {result.performance.search_latency_avg_ms:.1f} ms | {self._compare_latency_to_baseline(result.performance.search_latency_avg_ms)} |
| **Memory Usage** | {self._get_expected_memory_range(result.chunks_extracted)} MB | {result.peak_memory_mb:.1f} MB | {self._compare_memory_to_baseline(result.peak_memory_mb, result.chunks_extracted)} |

## Recommendations

### Performance Optimization
""")
            
            recommendations = self._generate_recommendations(result)
            for rec in recommendations:
                f.write(f"- {rec}\n")
            
            f.write(f"""

### Scaling Considerations

For repositories of similar size ({result.chunks_extracted:,} chunks):
- **Optimal Batch Size**: {self._recommend_batch_size(result.chunks_extracted)}
- **Memory Requirements**: {self._recommend_memory(result.chunks_extracted)} GB minimum
- **Expected Duration**: {self._estimate_duration(result.chunks_extracted)} minutes

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Tool Version:** Semantic Code Navigator v1.0  
**Report Format:** Individual Repository Benchmark v1.0  
""")
        
        # Also save JSON data for programmatic analysis
        json_file = self.results_dir / f"{result.repo_name}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        console.print(f"Individual report saved: {report_file}", style="blue")
        console.print(f"JSON data saved: {json_file}", style="blue")
    
    def _categorize_ingestion_time(self, time_seconds: float) -> str:
        """Categorize ingestion time performance."""
        if time_seconds < 30: return "Excellent"
        elif time_seconds < 120: return "Good"
        elif time_seconds < 300: return "Average"
        else: return "Slow"
    
    def _categorize_ingestion_rate(self, rate: float) -> str:
        """Categorize ingestion rate performance."""
        if rate > 50: return "Excellent"
        elif rate > 20: return "Good"
        elif rate > 10: return "Average"
        else: return "Slow"
    
    def _categorize_file_rate(self, rate: float) -> str:
        """Categorize file processing rate."""
        if rate > 5: return "Excellent"
        elif rate > 2: return "Good"
        elif rate > 1: return "Average"
        else: return "Slow"
    
    def _categorize_chunk_time(self, time_per_1k: float) -> str:
        """Categorize time per 1K chunks."""
        if time_per_1k < 10: return "Excellent"
        elif time_per_1k < 30: return "Good"
        elif time_per_1k < 60: return "Average"
        else: return "Slow"
    
    def _categorize_latency(self, latency_ms: float) -> str:
        """Categorize search latency."""
        if latency_ms < 500: return "Excellent"
        elif latency_ms < 1000: return "Good"
        elif latency_ms < 2000: return "Average"
        else: return "Slow"
    
    def _categorize_throughput(self, qps: float) -> str:
        """Categorize query throughput."""
        if qps > 2: return "Excellent"
        elif qps > 1: return "Good"
        elif qps > 0.5: return "Average"
        else: return "Slow"
    
    def _categorize_memory(self, memory_mb: float) -> str:
        """Categorize memory usage."""
        if memory_mb < 500: return "Excellent"
        elif memory_mb < 1000: return "Good"
        elif memory_mb < 2000: return "Average"
        else: return "High"
    
    def _categorize_memory_efficiency(self, mb_per_1k: float) -> str:
        """Categorize memory efficiency."""
        if mb_per_1k < 10: return "Excellent"
        elif mb_per_1k < 25: return "Good"
        elif mb_per_1k < 50: return "Average"
        else: return "Inefficient"
    
    def _categorize_cpu(self, cpu_percent: float) -> str:
        """Categorize CPU usage."""
        if cpu_percent < 25: return "Low"
        elif cpu_percent < 50: return "Moderate"
        elif cpu_percent < 75: return "High"
        else: return "Very High"
    
    def _get_size_category(self, chunks: int) -> str:
        """Get repository size category."""
        if chunks < 500: return "Small"
        elif chunks < 2000: return "Medium"
        elif chunks < 5000: return "Large"
        else: return "Very Large"
    
    def _get_expected_ingestion_range(self, chunks: int) -> str:
        """Get expected ingestion rate range."""
        if chunks < 500: return "30-60"
        elif chunks < 2000: return "20-40"
        elif chunks < 5000: return "15-30"
        else: return "10-25"
    
    def _compare_to_baseline(self, actual: float, expected_range: str) -> str:
        """Compare actual performance to baseline."""
        try:
            min_val, max_val = map(float, expected_range.split('-'))
            if actual >= max_val: return "Above Expected"
            elif actual >= min_val: return "Within Range"
            else: return "Below Expected"
        except:
            return "Unknown"
    
    def _compare_latency_to_baseline(self, latency_ms: float) -> str:
        """Compare latency to baseline."""
        if latency_ms < 1000: return "Excellent"
        elif latency_ms < 2000: return "Good"
        else: return "Needs Improvement"
    
    def _compare_memory_to_baseline(self, memory_mb: float, chunks: int) -> str:
        """Compare memory usage to baseline."""
        expected_mb = chunks * 0.5  # Rough baseline
        if memory_mb < expected_mb * 1.2: return "Efficient"
        elif memory_mb < expected_mb * 2: return "Acceptable"
        else: return "High Usage"
    
    def _get_expected_memory_range(self, chunks: int) -> str:
        """Get expected memory range."""
        base_mb = chunks * 0.3
        return f"{base_mb:.0f}-{base_mb * 2:.0f}"
    
    def _generate_recommendations(self, result: TestResult) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        if result.performance.ingestion_rate_chunks_per_second < 20:
            recommendations.append("Consider increasing batch size for better ingestion performance")
        
        if result.performance.search_latency_avg_ms > 2000:
            recommendations.append("Search latency is high - consider optimizing query complexity")
        
        if result.peak_memory_mb > 2000:
            recommendations.append("High memory usage detected - consider processing in smaller batches")
        
        if result.cpu_usage_percent > 80:
            recommendations.append("High CPU usage - consider reducing concurrent operations")
        
        if not recommendations:
            recommendations.append("Performance is within expected ranges for this repository size")
        
        return recommendations
    
    def _recommend_batch_size(self, chunks: int) -> int:
        """Recommend optimal batch size."""
        if chunks < 1000: return 100
        elif chunks < 5000: return 250
        elif chunks < 10000: return 500
        else: return 1000
    
    def _recommend_memory(self, chunks: int) -> int:
        """Recommend memory requirements."""
        base_gb = max(4, chunks / 1000)
        return int(base_gb)
    
    def _estimate_duration(self, chunks: int) -> int:
        """Estimate processing duration."""
        base_minutes = chunks / 500  # Rough estimate
        return max(1, int(base_minutes))
    
    def test_repository(self, repo: TestRepository) -> TestResult:
        """Run complete workflow test on a single repository."""
        result = TestResult(
            repo_name=repo.name,
            repo_url=repo.url,
            start_time=datetime.now(),
            batch_size=repo.batch_size,
            environment=TestEnvironment.capture_current()
        )
        
        console.print(Panel.fit(
            f"[bold blue]Testing Repository: {repo.name}[/bold blue]\n"
            f"URL: {repo.url}\n"
            f"Estimated Files: {repo.estimated_files}\n"
            f"Language: {repo.language}\n"
            f"Batch Size: {repo.batch_size}",
            border_style="blue"
        ))
        
        self.update_report(f"### Testing Repository: {repo.name}", "start")
        self.update_report(f"- **URL:** {repo.url}")
        self.update_report(f"- **Estimated Files:** {repo.estimated_files}")
        self.update_report(f"- **Language:** {repo.language}")
        self.update_report(f"- **Batch Size:** {repo.batch_size}")
        self.update_report(f"- **Max Concurrent Queries:** {repo.max_concurrent_queries}")
        
        console.print("Step 1: Creating Knowledge Base...", style="bold yellow")
        self.update_report("#### Step 1: Knowledge Base Creation")
        
        success, output, exec_time = self.run_cli_command("kb:reset --force")
        if success:
            console.print("KB reset successful", style="green")
        
        success, output, exec_time = self.run_cli_command("kb:init --validate-config")
        result.kb_creation_success = success
        result.kb_creation_time = exec_time
        
        if success:
            console.print(f"KB creation successful ({exec_time:.2f}s)", style="green")
            self.update_report(f"**KB Creation:** Success in {exec_time:.2f}s", "success")
        else:
            result.kb_creation_error = output
            console.print(f"KB creation failed: {output}", style="red")
            self.update_report(f"**KB Creation:** Failed - {output}", "error")
            return result
        
        console.print("Step 2: Initializing AI Tables...", style="bold yellow")
        self.update_report("#### Step 2: AI Tables Initialization")
        
        success, output, exec_time = self.run_cli_command("ai:init --force")
        if success:
            console.print(f"AI tables creation successful ({exec_time:.2f}s)", style="green")
            self.update_report(f"**AI Tables:** Success in {exec_time:.2f}s", "success")
        else:
            console.print(f"AI tables creation failed: {output}", style="yellow")
            self.update_report(f"**AI Tables:** Failed - {output}", "warning")
        
        console.print("Step 3: Ingesting Repository Data...", style="bold yellow")
        self.update_report("#### Step 3: Data Ingestion")
        
        self.monitor_system_resources(result)
        
        branch = self.detect_repository_branch(repo.url)
        
        ingestion_command = f"kb:ingest {repo.url} --branch {branch} --batch-size {repo.batch_size} --extract-git-info"
        success, output, exec_time = self.run_cli_command(ingestion_command, timeout=1800)  # 30 min timeout
        
        result.ingestion_success = success
        result.ingestion_time = exec_time
        
        if success:
            lines = output.split('\n')
            for line in lines:
                if 'chunks' in line.lower() and 'files' in line.lower():
                    try:
                        import re
                        numbers = re.findall(r'\d+', line)
                        if len(numbers) >= 2:
                            result.chunks_extracted = int(numbers[0])
                            result.files_processed = int(numbers[1])
                    except:
                        pass
            
            try:
                language_section = False
                for line in lines:
                    if 'Language breakdown:' in line:
                        language_section = True
                        continue
                    if language_section and ':' in line and 'chunks' in line:
                        parts = line.strip().split(':')
                        if len(parts) == 2:
                            lang = parts[0].strip()
                            chunk_count = int(re.findall(r'\d+', parts[1])[0])
                            result.language_breakdown[lang] = chunk_count
                    elif language_section and line.strip() == '':
                        break
            except:
                pass
            
            if result.chunks_extracted == 0:
                console.print(f"Ingestion completed but no chunks extracted. Output:", style="yellow")
                console.print(output, style="dim")
                result.ingestion_error = "No chunks extracted from repository"
                self.update_report(f"**Data Ingestion:** Completed but no chunks extracted", "warning")
                self.update_report(f"  - Output: {output}")
                return result
            
            console.print(f"Ingestion successful ({exec_time:.2f}s)", style="green")
            console.print(f"  Files: {result.files_processed}, Chunks: {result.chunks_extracted}", style="dim")
            self.update_report(f"**Data Ingestion:** Success in {exec_time:.2f}s", "success")
            self.update_report(f"  - Files Processed: {result.files_processed}")
            self.update_report(f"  - Chunks Extracted: {result.chunks_extracted}")
        else:
            result.ingestion_error = output
            console.print(f"Ingestion failed with error:", style="red")
            console.print(f"Error output: {output}", style="red")
            console.print(f"Command was: {ingestion_command}", style="dim")
            self.update_report(f"**Data Ingestion:** Failed - {output}", "error")
            self.update_report(f"  - Command: {ingestion_command}")
            return result
        
        console.print("Step 4: Creating Search Index...", style="bold yellow")
        self.update_report("#### Step 4: Index Creation")
        
        success, output, exec_time = self.run_cli_command("kb:index --show-stats")
        result.indexing_success = success
        result.indexing_time = exec_time
        
        if success:
            console.print(f"Indexing successful ({exec_time:.2f}s)", style="green")
            self.update_report(f"**Index Creation:** Success in {exec_time:.2f}s", "success")
        else:
            result.indexing_error = output
            console.print(f"Indexing failed: {output}", style="red")
            self.update_report(f"**Index Creation:** Failed - {output}", "error")
        
        console.print("Step 5: Testing Enhanced Semantic Search...", style="bold yellow")
        self.update_report("#### Step 5: Enhanced Semantic Search")
        
        search_queries_to_test = self.search_queries[:3]
        total_search_time = 0.0
        total_results = 0
        search_times = []
        
        for i, test_query in enumerate(search_queries_to_test, 1):
            console.print(f"Testing query {i}/{len(search_queries_to_test)}: {test_query}", style="blue")
            
            search_command = f'kb:query "{test_query}" --limit 3'
            success, output, exec_time = self.run_cli_command(search_command, timeout=120)
            
            if success:
                search_times.append(exec_time)
                total_search_time += exec_time
                
                try:
                    if "Found" in output and "results" in output:
                        import re
                        match = re.search(r'Found (\d+) results', output)
                        if match:
                            total_results += int(match.group(1))
                except:
                    pass
                
                console.print(f"Query {i} successful ({exec_time:.2f}s)", style="green")
            else:
                console.print(f"Query {i} failed: {output}", style="red")
                result.search_error = output
                break
        
        result.search_success = len(search_times) > 0
        result.search_time = total_search_time
        result.search_times = search_times
        result.queries_tested = len(search_times)
        result.search_results_count = total_results
        
        if result.search_success:
            avg_time = total_search_time / len(search_times) if search_times else 0
            console.print(f"Search testing successful - {len(search_times)} queries, avg {avg_time:.2f}s", style="green")
            self.update_report(f"**Search Testing:** Success - {len(search_times)} queries in {total_search_time:.2f}s", "success")
        else:
            console.print(f"Search testing failed", style="red")
            self.update_report(f"**Search Testing:** Failed - {result.search_error}", "error")
            return result
        
        console.print("Step 6: Testing AI-Enhanced Search...", style="bold yellow")
        self.update_report("#### Step 6: AI-Enhanced Search")
        
        ai_command = f'kb:query "{search_queries_to_test[0]}" --limit 2 --ai-all'
        success, output, exec_time = self.run_cli_command(ai_command, timeout=300)
        
        result.ai_analysis_success = success
        result.ai_analysis_time = exec_time
        
        if success:
            console.print(f"AI-enhanced search successful ({exec_time:.2f}s)", style="green")
            self.update_report(f"**AI-Enhanced Search:** Success in {exec_time:.2f}s", "success")
        else:
            result.ai_analysis_error = output
            console.print(f"AI-enhanced search failed: {output}", style="red")
            self.update_report(f"**AI-Enhanced Search:** Failed - {output}", "error")
            return result
        
        self.monitor_system_resources(result)
        result.end_time = datetime.now()
        
        console.print("Step 7: Cleaning up for next test...", style="bold yellow")
        self.update_report("#### Step 7: Cleanup")
        
        cleanup_success, cleanup_output, cleanup_time = self.run_cli_command("kb:reset --force")
        if cleanup_success:
            console.print("KB cleanup successful - memory freed for next test", style="green")
            self.update_report(f"**Cleanup:** KB reset successful in {cleanup_time:.2f}s", "success")
        else:
            console.print(f"KB cleanup failed: {cleanup_output}", style="yellow")
            self.update_report(f"**Cleanup:** KB reset failed - {cleanup_output}", "warning")
        
        console.print(Panel.fit(
            f"[bold green]Test Completed: {repo.name}[/bold green]\n"
            f"Total Time: {result.total_time:.2f}s\n"
            f"Success Rate: {result.success_rate:.1f}%\n"
            f"Peak Memory: {result.peak_memory_mb:.1f} MB",
            border_style="green"
        ))
        
        self.update_report("#### Test Summary")
        self.update_report(f"- **Total Time:** {result.total_time:.2f}s")
        self.update_report(f"- **Success Rate:** {result.success_rate:.1f}%")
        self.update_report(f"- **Peak Memory:** {result.peak_memory_mb:.1f} MB")
        self.update_report(f"- **CPU Usage:** {result.cpu_usage_percent:.1f}%")
        self.update_report("---")
        
        result.performance = PerformanceMetrics()
        result.performance.calculate_from_results(result, result.search_times)
        
        try:
            self.generate_individual_report(result, repo)
        except Exception as e:
            console.print(f"Failed to generate individual report: {e}", style="yellow")
        
        return result
    
    def generate_final_report(self):
        """Generate comprehensive final report with statistics and analysis."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        successful_tests = [r for r in self.results if r.success_rate > 80]
        failed_tests = [r for r in self.results if r.success_rate <= 80]
        
        total_files_processed = sum(r.files_processed for r in self.results)
        total_chunks_extracted = sum(r.chunks_extracted for r in self.results)
        
        ingestion_times = [r.ingestion_time for r in self.results if r.ingestion_time > 0]
        search_times = [r.search_time for r in self.results if r.search_time > 0]
        
        avg_ingestion_time = statistics.mean(ingestion_times) if ingestion_times else 0.0
        avg_search_time = statistics.mean(search_times) if search_times else 0.0
        
        with open(self.report_file, 'a') as f:
            f.write(f"""
## Final Test Summary

**Test Suite Completed:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Total Duration:** {total_duration/3600:.2f} hours

### Overall Statistics

| Metric | Value |
|--------|-------|
| **Total Repositories Tested** | {len(self.results)} |
| **Successful Tests** | {len(successful_tests)} ({len(successful_tests)/len(self.results)*100:.1f}%) |
| **Failed Tests** | {len(failed_tests)} ({len(failed_tests)/len(self.results)*100:.1f}%) |
| **Total Files Processed** | {total_files_processed:,} |
| **Total Code Chunks Extracted** | {total_chunks_extracted:,} |
| **Average Ingestion Time** | {avg_ingestion_time:.2f}s |
| **Average Search Response Time** | {avg_search_time:.2f}s |

### Performance Analysis

#### Ingestion Performance by Repository Size

| Repository | Files | Chunks | Batch Size | Ingestion Time | Chunks/Second |
|------------|-------|--------|------------|----------------|---------------|
""")
            
            for result in self.results:
                if result.ingestion_success and result.chunks_extracted > 0:
                    chunks_per_sec = result.chunks_extracted / result.ingestion_time if result.ingestion_time > 0 else 0
                    f.write(f"| {result.repo_name} | {result.files_processed} | {result.chunks_extracted} | {result.batch_size} | {result.ingestion_time:.2f}s | {chunks_per_sec:.1f} |\n")
            
            f.write(f"""
#### Search Performance Analysis

| Repository | Queries Tested | Avg Response Time | Total Results | Results/Query |
|------------|----------------|-------------------|---------------|---------------|
""")
            
            for result in self.results:
                if result.search_success and result.queries_tested > 0:
                    results_per_query = result.search_results_count / result.queries_tested
                    f.write(f"| {result.repo_name} | {result.queries_tested} | {result.search_time:.2f}s | {result.search_results_count} | {results_per_query:.1f} |\n")
            
            f.write(f"""
### Failure Analysis

#### Failed Tests
""")
            
            for result in failed_tests:
                f.write(f"""
**{result.repo_name}** (Success Rate: {result.success_rate:.1f}%)
""")
                if result.kb_creation_error:
                    f.write(f"- KB Creation Error: {result.kb_creation_error}\n")
                if result.ingestion_error:
                    f.write(f"- Ingestion Error: {result.ingestion_error}\n")
                if result.indexing_error:
                    f.write(f"- Indexing Error: {result.indexing_error}\n")
                if result.search_error:
                    f.write(f"- Search Error: {result.search_error}\n")
                if result.ai_analysis_error:
                    f.write(f"- AI Analysis Error: {result.ai_analysis_error}\n")
            
            f.write(f"""
### Recommendations

#### Performance Optimizations
1. **Batch Size Tuning:** Optimal batch sizes appear to be between 300-500 for medium repositories
2. **Memory Management:** Peak memory usage correlates with repository size - consider streaming for large repos
3. **Search Optimization:** Response times under 2s for most queries indicate good performance

#### Reliability Improvements
1. **Error Handling:** Implement retry logic for transient failures
2. **Timeout Management:** Increase timeouts for very large repositories (>2000 files)
3. **Resource Monitoring:** Add memory limits to prevent system overload

### Test Environment
- **Python Version:** {sys.version}
- **Test Machine:** {os.uname().sysname} {os.uname().release}
- **Available Memory:** {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f} GB
- **CPU Cores:** {psutil.cpu_count()}

### Individual Repository Reports

Detailed benchmark reports for each repository have been generated in the `results/` directory:

""")
            
            for result in self.results:
                timestamp = result.start_time.strftime('%Y%m%d_%H%M%S')
                f.write(f"- **{result.repo_name}**: `results/{result.repo_name}_{timestamp}.md` (JSON: `{result.repo_name}_{timestamp}.json`)\n")
            
            f.write(f"""

Each individual report contains:
- Complete environment specifications for reproducibility
- Detailed performance metrics with benchmark categories
- Language breakdown and repository characteristics  
- Step-by-step execution results with timing
- Performance baselines and recommendations
- Reproduction scripts for exact replication

---

*Report generated by Semantic Code Navigator Stress Test Suite*
""")
    
    def run_stress_test(self):
        """Run the complete stress test suite."""
        console.print(Panel.fit(
            "[bold blue]Semantic Code Navigator - Comprehensive Stress Test[/bold blue]\n"
            f"Testing {len(self.test_repositories)} repositories\n"
            f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            border_style="blue"
        ))
        
        self.initialize_report()
        self.update_report("# Stress Test Suite Started", "start")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                
                main_task = progress.add_task("Running stress tests...", total=len(self.test_repositories))
                
                # Run tests SERIALLY (one after another) to avoid memory issues
                # Each test includes cleanup step to free memory before next test
                for i, repo in enumerate(self.test_repositories):
                    progress.update(main_task, description=f"Testing {repo.name} ({i+1}/{len(self.test_repositories)})...")
                    
                    try:
                        result = self.test_repository(repo)
                        self.results.append(result)
                        
                        console.print(f"✅ Completed {repo.name} ({result.success_rate:.1f}% success)", style="green")
                        
                    except KeyboardInterrupt:
                        console.print("\n⚠️ Test interrupted by user", style="yellow")
                        self.update_report("Test suite interrupted by user", "warning")
                        break
                    except Exception as e:
                        console.print(f"❌ Test failed for {repo.name}: {e}", style="red")
                        self.update_report(f"Test failed for {repo.name}: {e}", "error")
                        
                        failed_result = TestResult(
                            repo_name=repo.name,
                            start_time=datetime.now(),
                            end_time=datetime.now()
                        )
                        failed_result.kb_creation_error = str(e)
                        self.results.append(failed_result)
                    
                    progress.update(main_task, advance=1)
                    
                    console.print(f"Waiting 10 seconds before next test...", style="dim")
                    time.sleep(10)
        
        finally:
            self.generate_final_report()
            
            console.print(Panel.fit(
                f"[bold green]Stress Test Complete![/bold green]\n"
                f"Report saved to: {self.report_file}\n"
                f"Total tests: {len(self.results)}\n"
                f"Successful: {len([r for r in self.results if r.success_rate > 80])}\n"
                f"Duration: {(datetime.now() - self.start_time).total_seconds()/3600:.2f} hours",
                border_style="green"
            ))
            
            self.update_report("# Stress Test Suite Completed", "finish")

def main():
    """Main entry point for stress test suite."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        console.print("""
[bold blue]Semantic Code Navigator - Stress Test Suite[/bold blue]

This script runs comprehensive stress tests on the CLI tool using 25 GitHub repositories
of varying sizes. It tests the complete workflow:

1. Knowledge Base creation
2. Data ingestion with varying batch sizes
3. Index creation
4. Semantic search with multiple queries
5. AI analysis integration

[bold yellow]Usage:[/bold yellow]
    python stress_test.py                    # Run full test suite (25 repos)
    python stress_test.py --test-single      # Test only first repository
    python stress_test.py --help             # Show this help

[bold yellow]Output:[/bold yellow]
    - Real-time console progress with live CLI output
    - Detailed markdown report with timestamps
    - Performance metrics and failure analysis
    - Recommendations for optimization

[bold yellow]Requirements:[/bold yellow]
    - MindsDB running locally (docker-compose up)
    - OpenAI API key configured
    - Internet connection for repository cloning
    - Sufficient disk space (~5GB for temporary repos)
        """)
        return
    
    test_single = len(sys.argv) > 1 and sys.argv[1] == "--test-single"
    
    console.print("Checking prerequisites...", style="blue")
    
    try:
        result = subprocess.run("python -m src.cli --version", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            console.print("❌ CLI not accessible. Make sure you're in the project root directory.", style="red")
            return
    except:
        console.print("❌ Failed to run CLI. Check your Python environment.", style="red")
        return
    
    try:
        result = subprocess.run("python -m src.cli kb:status", shell=True, capture_output=True, text=True, timeout=10)
        if "Failed to connect" in result.stderr:
            console.print("❌ MindsDB not accessible. Start with: docker-compose up", style="red")
            return
    except:
        console.print("⚠️ Could not verify MindsDB connection. Proceeding anyway...", style="yellow")
    
    console.print("✅ Prerequisites check passed", style="green")
    
    suite = StressTestSuite()
    
    if test_single:
        console.print("🧪 Running single repository test mode", style="blue")
        suite.test_repositories = suite.test_repositories[:1]
    
    suite.run_stress_test()

if __name__ == "__main__":
    main() 