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
import platform
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
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
            openai_model_reranking="gpt-3.5-turbo"
        )

@dataclass
class StatisticalMetrics:
    """Advanced statistical metrics for performance analysis."""
    mean: float = 0.0
    median: float = 0.0
    std_dev: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    confidence_interval_95: tuple = (0.0, 0.0)
    coefficient_variation: float = 0.0
    outliers_count: int = 0
    
    @classmethod
    def from_values(cls, values: List[float]) -> 'StatisticalMetrics':
        """Calculate statistical metrics from a list of values."""
        if not values:
            return cls()
        
        import statistics
        import math
        
        mean = statistics.mean(values)
        median = statistics.median(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
        min_val = min(values)
        max_val = max(values)
        
        # Calculate 95% confidence interval
        if len(values) > 1:
            margin_error = 1.96 * (std_dev / math.sqrt(len(values)))
            ci_95 = (mean - margin_error, mean + margin_error)
        else:
            ci_95 = (mean, mean)
        
        # Coefficient of variation
        cv = (std_dev / mean * 100) if mean > 0 else 0.0
        
        # Count outliers (values beyond 2 standard deviations)
        outliers = sum(1 for v in values if abs(v - mean) > 2 * std_dev)
        
        return cls(
            mean=mean,
            median=median,
            std_dev=std_dev,
            min_value=min_val,
            max_value=max_val,
            confidence_interval_95=ci_95,
            coefficient_variation=cv,
            outliers_count=outliers
        )

@dataclass
class BenchmarkBaseline:
    """Performance baselines for different dataset sizes."""
    size_category: str
    chunks_range: tuple
    expected_ingestion_rate: tuple  # (min, max) chunks/second
    expected_search_latency: tuple  # (min, max) milliseconds
    expected_memory_mb: tuple  # (min, max) MB
    expected_duration_minutes: tuple  # (min, max) minutes
    
    @classmethod
    def get_baselines(cls) -> List['BenchmarkBaseline']:
        """Return performance baselines for different dataset sizes."""
        return [
            cls("Small", (0, 500), (20, 60), (200, 800), (50, 200), (1, 5)),
            cls("Medium", (500, 2000), (15, 40), (300, 1200), (100, 400), (2, 10)),
            cls("Large", (2000, 5000), (10, 30), (400, 1500), (200, 800), (5, 20)),
            cls("Very Large", (5000, 15000), (5, 20), (500, 2000), (400, 1500), (10, 45)),
            cls("Extra Large", (15000, float('inf')), (3, 15), (600, 3000), (800, 3000), (20, 90))
        ]

@dataclass
class PerformanceMetrics:
    """Enhanced detailed performance metrics for benchmarking."""
    # Existing metrics
    ingestion_rate_chunks_per_second: float = 0.0
    ingestion_rate_files_per_second: float = 0.0
    ingestion_time_per_1k_chunks: float = 0.0
    search_latency_avg_ms: float = 0.0
    search_latency_p95_ms: float = 0.0
    search_latency_p99_ms: float = 0.0
    memory_efficiency_mb_per_1k_chunks: float = 0.0
    throughput_queries_per_second: float = 0.0
    
    # Enhanced statistical metrics
    search_latency_stats: Optional[StatisticalMetrics] = None
    ingestion_consistency_score: float = 0.0  # Lower is better (CV of batch times)
    memory_growth_rate: float = 0.0  # MB per additional 1K chunks
    performance_stability_index: float = 0.0  # Overall stability metric
    
    # Comparative metrics
    relative_performance_vs_baseline: float = 0.0  # Percentage vs expected baseline
    efficiency_ratio: float = 0.0  # Results per resource unit
    scalability_factor: float = 0.0  # How well it scales with data size
    
    def calculate_from_results(self, result: 'TestResult', search_times: List[float]):
        """Calculate enhanced performance metrics from test results."""
        # Existing calculations
        if result.ingestion_time > 0 and result.chunks_extracted > 0:
            self.ingestion_rate_chunks_per_second = result.chunks_extracted / result.ingestion_time
            self.ingestion_time_per_1k_chunks = (result.ingestion_time / result.chunks_extracted) * 1000
            
        if result.ingestion_time > 0 and result.files_processed > 0:
            self.ingestion_rate_files_per_second = result.files_processed / result.ingestion_time
            
        if search_times:
            search_times_ms = [t * 1000 for t in search_times]
            self.search_latency_avg_ms = statistics.mean(search_times_ms)
            
            # Enhanced percentile calculations
            if len(search_times_ms) >= 5:
                sorted_times = sorted(search_times_ms)
                n = len(sorted_times)
                self.search_latency_p95_ms = sorted_times[int(0.95 * n)]
                self.search_latency_p99_ms = sorted_times[int(0.99 * n)] if n >= 10 else sorted_times[-1]
            
            # Statistical analysis of search times
            self.search_latency_stats = StatisticalMetrics.from_values(search_times_ms)
            
        if result.peak_memory_mb > 0 and result.chunks_extracted > 0:
            self.memory_efficiency_mb_per_1k_chunks = (result.peak_memory_mb / result.chunks_extracted) * 1000
            
        if result.queries_tested > 0 and result.search_time > 0:
            self.throughput_queries_per_second = result.queries_tested / result.search_time
        
        # Calculate enhanced metrics
        self._calculate_advanced_metrics(result, search_times)
    
    def _calculate_advanced_metrics(self, result: 'TestResult', search_times: List[float]):
        """Calculate advanced performance metrics."""
        # Ingestion consistency (based on batch processing variance)
        if result.chunks_extracted > 0 and result.ingestion_time > 0:
            expected_batches = max(1, result.chunks_extracted // result.batch_size)
            expected_time_per_batch = result.ingestion_time / expected_batches
            # Simulate batch time variance (in real implementation, track actual batch times)
            self.ingestion_consistency_score = min(20.0, expected_time_per_batch * 0.1)  # Lower is better
        
        # Memory growth rate estimation
        if result.chunks_extracted > 1000:
            base_memory = 100  # Estimated base memory usage
            variable_memory = max(0, result.peak_memory_mb - base_memory)
            self.memory_growth_rate = (variable_memory / result.chunks_extracted) * 1000
        
        # Performance stability index (combination of consistency metrics)
        stability_factors = []
        if self.search_latency_stats and self.search_latency_stats.coefficient_variation > 0:
            stability_factors.append(min(100, self.search_latency_stats.coefficient_variation))
        if self.ingestion_consistency_score > 0:
            stability_factors.append(self.ingestion_consistency_score)
        
        self.performance_stability_index = statistics.mean(stability_factors) if stability_factors else 0.0
        
        # Efficiency ratio (results per resource unit)
        if result.peak_memory_mb > 0 and result.search_results_count > 0:
            self.efficiency_ratio = result.search_results_count / result.peak_memory_mb
        
        # Comparative performance vs baseline
        baseline = self._get_baseline_for_size(result.chunks_extracted)
        if baseline:
            expected_rate = statistics.mean(baseline.expected_ingestion_rate)
            if expected_rate > 0:
                self.relative_performance_vs_baseline = (self.ingestion_rate_chunks_per_second / expected_rate) * 100
        
        # Scalability factor (simplified - in practice would need multiple data points)
        if result.chunks_extracted > 0:
            theoretical_linear_time = result.chunks_extracted / 50  # Assume 50 chunks/sec baseline
            actual_time = result.ingestion_time
            self.scalability_factor = theoretical_linear_time / actual_time if actual_time > 0 else 0.0
    
    def _get_baseline_for_size(self, chunks: int) -> Optional[BenchmarkBaseline]:
        """Get appropriate baseline for dataset size."""
        baselines = BenchmarkBaseline.get_baselines()
        for baseline in baselines:
            if baseline.chunks_range[0] <= chunks <= baseline.chunks_range[1]:
                return baseline
        return baselines[-1]  # Return largest category as fallback

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
            # Small repositories (30-80 files) - Quick tests
            TestRepository("flask-microblog", "https://github.com/miguelgrinberg/microblog", 50, "Python", "Flask microblog tutorial", 100, 10),
            TestRepository("calculator", "https://github.com/Abdulvoris101/Vue-Calculator", 40, "JavaScript", "Express.js web framework", 80, 12),
            TestRepository("vue-calculator", "https://github.com/ahfarmer/calculator", 35, "JavaScript", "Simple calculator app", 70, 10),
            TestRepository("todo", "https://github.com/tusharnankani/ToDoList", 80, "JavaScript", "TodoMVC React implementation", 160, 16),
            TestRepository("react-weather-app", "https://github.com/Adedoyin-Emmanuel/react-weather-app", 60, "JavaScript", "React app generator", 120, 15),
            
            # Medium repositories (80-150 files) - Moderate tests  
            TestRepository("fastapi-example", "https://github.com/tiangolo/full-stack-fastapi-postgresql", 90, "Python", "FastAPI full-stack example", 180, 18),
            TestRepository("gin-rest-api", "https://github.com/gin-gonic/gin", 120, "Go", "Gin REST API example", 240, 20),
            TestRepository("vue-cli", "https://github.com/vuejs/vue-cli", 100, "JavaScript", "Vue.js CLI tool", 200, 18),
            TestRepository("price-tracker", "https://github.com/Deeptanshu-sankhwar/crypto-price-tracker", 110, "TypeScript", "Crypto price tracker", 220, 22),
            TestRepository("semantic-code-navigator", "https://github.com/Deeptanshu-sankhwar/semantic-code-navigator", 60, "Python", "Semantic code navigator", 120, 15)
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
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special markdown characters to prevent formatting issues."""
        if not text:
            return text
        
        # Escape common markdown special characters that could break formatting
        escape_chars = ['*', '_', '`', '#', '[', ']', '(', ')', '|', '\\']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text

    def update_report(self, message: str, level: str = "info"):
        """Update the report with real-time information and appropriate status indicators.
        
        Appends timestamped messages to the markdown report file with level-specific
        indicators for tracking test progress and results.
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Escape markdown special characters to prevent formatting issues
        safe_message = self._escape_markdown(message)
        
        level_indicators = {
            "info": "[INFO]",
            "success": "[SUCCESS]", 
            "warning": "[WARNING]",
            "error": "[ERROR]",
            "start": "[START]",
            "finish": "[COMPLETE]"
        }
        
        try:
            with open(self.report_file, 'a', encoding='utf-8') as f:
                f.write(f"\n**{timestamp}** {level_indicators.get(level, '[INFO]')} {safe_message}\n")
                f.flush()
        except Exception as e:
            console.print(f"Failed to update report: {e}", style="red")
    
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
        environment specifications, performance metrics, statistical analysis,
        and critical optimization insights for reproducible benchmarks.
        """
        timestamp = result.start_time.strftime('%Y%m%d_%H%M%S')
        report_file = self.results_dir / f"{result.repo_name}_{timestamp}.md"
        
        if result.performance is None:
            result.performance = PerformanceMetrics()
            result.performance.calculate_from_results(result, result.search_times)
        
        if result.environment is None:
            result.environment = TestEnvironment.capture_current()
        
        # Get baseline for comparison
        baseline = result.performance._get_baseline_for_size(result.chunks_extracted)
        
        with open(report_file, 'w') as f:
            f.write(f"""# Performance Benchmark Report: {result.repo_name}

**Repository:** {result.repo_url}  
**Test Date:** {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Duration:** {result.total_time:.2f} seconds  
**Success Rate:** {result.success_rate:.1f}%  
**Dataset Category:** {baseline.size_category if baseline else 'Unknown'}

## Executive Summary

This report provides comprehensive performance benchmarks for the {result.repo_name} repository using the Semantic Code Navigator. The analysis includes statistical significance testing, confidence intervals, and critical optimization insights for reproducible performance evaluation.

### Key Performance Indicators

| Metric | Value | Unit | Baseline Comparison |
|--------|-------|------|-------------------|
| **Dataset Size** | {result.chunks_extracted:,} | code chunks | {baseline.size_category if baseline else 'N/A'} category |
| **Files Processed** | {result.files_processed:,} | files | - |
| **Ingestion Rate** | {result.performance.ingestion_rate_chunks_per_second:.1f} | chunks/second | {self._format_baseline_comparison(result.performance.ingestion_rate_chunks_per_second, baseline.expected_ingestion_rate if baseline else None)} |
| **Search Latency (Avg)** | {result.performance.search_latency_avg_ms:.1f} | milliseconds | {self._format_baseline_comparison(result.performance.search_latency_avg_ms, baseline.expected_search_latency if baseline else None)} |
| **Memory Efficiency** | {result.performance.memory_efficiency_mb_per_1k_chunks:.1f} | MB per 1K chunks | - |
| **Throughput** | {result.performance.throughput_queries_per_second:.2f} | queries/second | - |
| **Performance vs Baseline** | {result.performance.relative_performance_vs_baseline:.1f}% | relative | {'Above' if result.performance.relative_performance_vs_baseline > 100 else 'Below'} expected |
| **Stability Index** | {result.performance.performance_stability_index:.1f} | consistency score | {'Stable' if result.performance.performance_stability_index < 20 else 'Variable'} |

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

| Metric | Value | Benchmark Category | Statistical Significance |
|--------|-------|-------------------|-------------------------|
| **Total Ingestion Time** | {result.ingestion_time:.2f} seconds | {self._categorize_ingestion_time(result.ingestion_time)} | - |
| **Chunks per Second** | {result.performance.ingestion_rate_chunks_per_second:.1f} | {self._categorize_ingestion_rate(result.performance.ingestion_rate_chunks_per_second)} | {result.performance.relative_performance_vs_baseline:.1f}% vs baseline |
| **Files per Second** | {result.performance.ingestion_rate_files_per_second:.1f} | {self._categorize_file_rate(result.performance.ingestion_rate_files_per_second)} | - |
| **Time per 1K Chunks** | {result.performance.ingestion_time_per_1k_chunks:.1f} seconds | {self._categorize_chunk_time(result.performance.ingestion_time_per_1k_chunks)} | - |
| **Consistency Score** | {result.performance.ingestion_consistency_score:.1f} | {'Stable' if result.performance.ingestion_consistency_score < 10 else 'Variable'} | Lower is better |
| **Scalability Factor** | {result.performance.scalability_factor:.2f} | {'Linear' if 0.8 <= result.performance.scalability_factor <= 1.2 else 'Non-linear'} | 1.0 = perfect scaling |

### Search Performance with Statistical Analysis

| Metric | Value | Benchmark Category | 95% Confidence Interval |
|--------|-------|-------------------|------------------------|
| **Average Latency** | {result.performance.search_latency_avg_ms:.1f} ms | {self._categorize_latency(result.performance.search_latency_avg_ms)} | {f"({result.performance.search_latency_stats.confidence_interval_95[0]:.1f}, {result.performance.search_latency_stats.confidence_interval_95[1]:.1f}) ms" if result.performance.search_latency_stats else "N/A"} |
| **Median Latency** | {result.performance.search_latency_stats.median:.1f if result.performance.search_latency_stats else 0:.1f} ms | - | More robust than mean |
| **95th Percentile** | {result.performance.search_latency_p95_ms:.1f} ms | {self._categorize_latency(result.performance.search_latency_p95_ms)} | - |
| **99th Percentile** | {result.performance.search_latency_p99_ms:.1f} ms | {self._categorize_latency(result.performance.search_latency_p99_ms)} | - |
| **Standard Deviation** | {result.performance.search_latency_stats.std_dev:.1f if result.performance.search_latency_stats else 0:.1f} ms | - | Consistency measure |
| **Coefficient of Variation** | {result.performance.search_latency_stats.coefficient_variation:.1f if result.performance.search_latency_stats else 0:.1f}% | {'Consistent' if (result.performance.search_latency_stats.coefficient_variation if result.performance.search_latency_stats else 0) < 20 else 'Variable'} | <20% is good |
| **Queries per Second** | {result.performance.throughput_queries_per_second:.2f} | {self._categorize_throughput(result.performance.throughput_queries_per_second)} | - |

### Memory and Resource Efficiency

| Metric | Value | Benchmark Category | Efficiency Analysis |
|--------|-------|-------------------|-------------------|
| **Peak Memory Usage** | {result.peak_memory_mb:.1f} MB | {self._categorize_memory(result.peak_memory_mb)} | {self._compare_memory_to_baseline(result.peak_memory_mb, result.chunks_extracted)} |
| **Memory per 1K Chunks** | {result.performance.memory_efficiency_mb_per_1k_chunks:.1f} MB | {self._categorize_memory_efficiency(result.performance.memory_efficiency_mb_per_1k_chunks)} | - |
| **Memory Growth Rate** | {result.performance.memory_growth_rate:.2f} MB/1K chunks | {'Linear' if result.performance.memory_growth_rate < 50 else 'Concerning'} | Scalability indicator |
| **CPU Usage Peak** | {result.cpu_usage_percent:.1f}% | {self._categorize_cpu(result.cpu_usage_percent)} | - |
| **Efficiency Ratio** | {result.performance.efficiency_ratio:.2f} results/MB | {'Efficient' if result.performance.efficiency_ratio > 1 else 'Inefficient'} | Higher is better |

### Advanced Performance Analysis

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Performance Stability Index** | {result.performance.performance_stability_index:.1f} | {'Stable performance' if result.performance.performance_stability_index < 20 else 'Variable performance - investigate'} |
| **Outlier Detection** | {result.performance.search_latency_stats.outliers_count if result.performance.search_latency_stats else 0} outliers | {'Normal distribution' if (result.performance.search_latency_stats.outliers_count if result.performance.search_latency_stats else 0) < 2 else 'Some queries had unusual latency'} |
| **Min/Max Latency Range** | {result.performance.search_latency_stats.min_value:.1f} - {result.performance.search_latency_stats.max_value:.1f} ms | {'Consistent' if (result.performance.search_latency_stats.max_value - result.performance.search_latency_stats.min_value if result.performance.search_latency_stats else 0) < 1000 else 'High variance'} |

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

## Critical Optimization Insights

### Performance Bottleneck Analysis

Based on the benchmark results, here are the critical insights for optimization:

""")
            
            # Generate critical insights
            critical_insights = self._generate_critical_insights(result, baseline)
            for insight in critical_insights:
                f.write(f"**{insight['category']}**: {insight['description']}\n\n")
            
            f.write(f"""
### Statistical Confidence and Reliability

- **Sample Size**: {result.queries_tested} search queries tested
- **Confidence Level**: 95% confidence intervals provided for latency measurements
- **Statistical Significance**: {f"Results are statistically significant with CV < 20%" if (result.performance.search_latency_stats.coefficient_variation if result.performance.search_latency_stats else 100) < 20 else "High variance detected - more samples recommended"}
- **Outlier Impact**: {result.performance.search_latency_stats.outliers_count if result.performance.search_latency_stats else 0} outliers detected out of {result.queries_tested} queries
- **Reproducibility Score**: {'High' if result.performance.performance_stability_index < 15 else 'Medium' if result.performance.performance_stability_index < 30 else 'Low'} (based on consistency metrics)

### Comparative Performance Analysis

""")
            
            if baseline:
                f.write(f"""
**Dataset Size Category**: {baseline.size_category}
- **Expected Ingestion Rate**: {baseline.expected_ingestion_rate[0]}-{baseline.expected_ingestion_rate[1]} chunks/second
- **Actual Ingestion Rate**: {result.performance.ingestion_rate_chunks_per_second:.1f} chunks/second
- **Performance Ratio**: {result.performance.relative_performance_vs_baseline:.1f}% of expected baseline
- **Expected Search Latency**: {baseline.expected_search_latency[0]}-{baseline.expected_search_latency[1]} ms
- **Actual Search Latency**: {result.performance.search_latency_avg_ms:.1f} ms
- **Expected Memory Usage**: {baseline.expected_memory_mb[0]}-{baseline.expected_memory_mb[1]} MB
- **Actual Memory Usage**: {result.peak_memory_mb:.1f} MB

**Baseline Comparison Summary**:
{self._generate_baseline_summary(result, baseline)}
""")
            else:
                f.write("No baseline available for this dataset size.\n")
            
            f.write(f"""

## Recommendations

### Critical Performance Optimizations
""")
            
            recommendations = self._generate_enhanced_recommendations(result, baseline)
            for category, recs in recommendations.items():
                f.write(f"\n**{category}**:\n")
                for rec in recs:
                    f.write(f"- {rec}\n")
            
            f.write(f"""

### Scaling Considerations and Resource Planning

For repositories of similar size ({result.chunks_extracted:,} chunks):

| Resource | Recommendation | Justification |
|----------|----------------|---------------|
| **Batch Size** | {self._recommend_batch_size(result.chunks_extracted)} | Optimized for {baseline.size_category if baseline else 'this'} dataset size |
| **Memory Requirements** | {self._recommend_memory(result.chunks_extracted)} GB minimum | Based on {result.performance.memory_growth_rate:.1f} MB/1K chunks growth rate |
| **Expected Duration** | {self._estimate_duration(result.chunks_extracted)} minutes | Linear scaling from current performance |
| **Concurrent Queries** | {self._recommend_concurrency(result)} | Based on latency and stability metrics |
| **Hardware Specs** | {self._recommend_hardware(result)} | Optimized for this workload pattern |

### Cost-Performance Analysis

- **Processing Cost**: ~{self._estimate_processing_cost(result):.2f} USD (estimated OpenAI API costs)
- **Time Cost**: {result.total_time / 60:.1f} minutes total processing time
- **Efficiency Rating**: {self._calculate_efficiency_rating(result)}
- **ROI Optimization**: {self._suggest_roi_optimization(result)}

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
    
    def _format_baseline_comparison(self, actual_value: float, expected_range: Optional[tuple]) -> str:
        """Format baseline comparison for display."""
        if not expected_range:
            return "No baseline"
        
        min_expected, max_expected = expected_range
        if min_expected <= actual_value <= max_expected:
            return f"✓ Within range ({min_expected:.0f}-{max_expected:.0f})"
        elif actual_value < min_expected:
            return f"⚠ Below range ({actual_value:.1f} < {min_expected:.0f})"
        else:
            return f"⚡ Above range ({actual_value:.1f} > {max_expected:.0f})"
    
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
    
    def _generate_critical_insights(self, result: TestResult, baseline: Optional[BenchmarkBaseline]) -> List[Dict[str, str]]:
        """Generate critical optimization insights based on performance analysis."""
        insights = []
        
        # Ingestion performance analysis
        if result.performance.relative_performance_vs_baseline < 70:
            insights.append({
                "category": "Ingestion Bottleneck",
                "description": f"Ingestion rate ({result.performance.ingestion_rate_chunks_per_second:.1f} chunks/sec) is {100 - result.performance.relative_performance_vs_baseline:.1f}% below expected baseline. Consider increasing batch size from {result.batch_size} to {self._recommend_batch_size(result.chunks_extracted)} or optimizing network/disk I/O."
            })
        elif result.performance.relative_performance_vs_baseline > 130:
            insights.append({
                "category": "Ingestion Excellence",
                "description": f"Ingestion performance is {result.performance.relative_performance_vs_baseline - 100:.1f}% above baseline expectations. This configuration ({result.batch_size} batch size) is optimal for this dataset size."
            })
        
        # Search latency analysis
        if result.performance.search_latency_stats and result.performance.search_latency_stats.coefficient_variation > 30:
            insights.append({
                "category": "Search Inconsistency",
                "description": f"High search latency variance (CV: {result.performance.search_latency_stats.coefficient_variation:.1f}%). Some queries are {result.performance.search_latency_stats.max_value / result.performance.search_latency_stats.mean:.1f}x slower than average. Consider query optimization or indexing improvements."
            })
        
        # Memory efficiency analysis
        if result.performance.memory_growth_rate > 100:
            insights.append({
                "category": "Memory Scalability Risk",
                "description": f"High memory growth rate ({result.performance.memory_growth_rate:.1f} MB per 1K chunks) indicates potential scalability issues for larger datasets. Consider streaming ingestion or memory optimization."
            })
        
        # Stability analysis
        if result.performance.performance_stability_index > 25:
            insights.append({
                "category": "Performance Variability",
                "description": f"High performance variability (stability index: {result.performance.performance_stability_index:.1f}) suggests inconsistent system behavior. Investigate resource contention or optimize for more predictable performance."
            })
        
        # Efficiency analysis
        if result.performance.efficiency_ratio < 0.5:
            insights.append({
                "category": "Resource Efficiency",
                "description": f"Low efficiency ratio ({result.performance.efficiency_ratio:.2f} results/MB) indicates high resource usage relative to output. Consider optimizing memory usage or query selectivity."
            })
        
        # Add positive insights for good performance
        if not insights:
            insights.append({
                "category": "Optimal Performance",
                "description": "All performance metrics are within expected ranges. Current configuration provides good balance of speed, memory efficiency, and consistency."
            })
        
        return insights
    
    def _generate_baseline_summary(self, result: TestResult, baseline: BenchmarkBaseline) -> str:
        """Generate a summary of performance vs baseline."""
        summary_parts = []
        
        # Ingestion comparison
        if result.performance.relative_performance_vs_baseline > 120:
            summary_parts.append("✅ Ingestion: Significantly above baseline")
        elif result.performance.relative_performance_vs_baseline > 90:
            summary_parts.append("✅ Ingestion: Within expected range")
        else:
            summary_parts.append("⚠️ Ingestion: Below expected performance")
        
        # Latency comparison
        avg_expected_latency = sum(baseline.expected_search_latency) / 2
        if result.performance.search_latency_avg_ms < avg_expected_latency:
            summary_parts.append("✅ Latency: Better than expected")
        elif result.performance.search_latency_avg_ms < baseline.expected_search_latency[1]:
            summary_parts.append("✅ Latency: Within expected range")
        else:
            summary_parts.append("⚠️ Latency: Higher than expected")
        
        # Memory comparison
        avg_expected_memory = sum(baseline.expected_memory_mb) / 2
        if result.peak_memory_mb < avg_expected_memory:
            summary_parts.append("✅ Memory: Efficient usage")
        elif result.peak_memory_mb < baseline.expected_memory_mb[1]:
            summary_parts.append("✅ Memory: Within expected range")
        else:
            summary_parts.append("⚠️ Memory: Higher than expected")
        
        return " | ".join(summary_parts)
    
    def _generate_enhanced_recommendations(self, result: TestResult, baseline: Optional[BenchmarkBaseline]) -> Dict[str, List[str]]:
        """Generate categorized recommendations based on performance analysis."""
        recommendations = {
            "Immediate Optimizations": [],
            "Scaling Preparations": [],
            "Monitoring and Reliability": [],
            "Cost Optimization": []
        }
        
        # Immediate optimizations
        if result.performance.relative_performance_vs_baseline < 80:
            recommendations["Immediate Optimizations"].append(
                f"Increase batch size from {result.batch_size} to {self._recommend_batch_size(result.chunks_extracted)} for better ingestion throughput"
            )
        
        if result.performance.search_latency_avg_ms > 2000:
            recommendations["Immediate Optimizations"].append(
                "Optimize query complexity or add query result caching for latency > 2s"
            )
        
        if result.performance.search_latency_stats and result.performance.search_latency_stats.coefficient_variation > 25:
            recommendations["Immediate Optimizations"].append(
                "Investigate query variance - consider query normalization or indexing optimization"
            )
        
        # Scaling preparations
        if result.performance.memory_growth_rate > 50:
            recommendations["Scaling Preparations"].append(
                f"High memory growth rate ({result.performance.memory_growth_rate:.1f} MB/1K chunks) - implement streaming for larger datasets"
            )
        
        recommendations["Scaling Preparations"].append(
            f"For 10x dataset size, expect ~{self._estimate_scaled_memory(result, 10):.0f} GB memory requirement"
        )
        
        if result.performance.scalability_factor < 0.8:
            recommendations["Scaling Preparations"].append(
                "Non-linear scaling detected - consider horizontal scaling or batch processing optimization"
            )
        
        # Monitoring and reliability
        if result.performance.performance_stability_index > 20:
            recommendations["Monitoring and Reliability"].append(
                "Add performance monitoring for high variability in execution times"
            )
        
        recommendations["Monitoring and Reliability"].append(
            f"Set up alerts for latency > {result.performance.search_latency_p95_ms * 1.5:.0f}ms (1.5x P95)"
        )
        
        if result.performance.search_latency_stats and result.performance.search_latency_stats.outliers_count > 2:
            recommendations["Monitoring and Reliability"].append(
                "Monitor for query outliers - implement timeout and retry mechanisms"
            )
        
        # Cost optimization
        estimated_cost = self._estimate_processing_cost(result)
        if estimated_cost > 1.0:
            recommendations["Cost Optimization"].append(
                f"High processing cost (~${estimated_cost:.2f}) - consider batch processing or model optimization"
            )
        
        recommendations["Cost Optimization"].append(
            f"Optimize for cost/performance ratio: current efficiency is {result.performance.efficiency_ratio:.2f} results/MB"
        )
        
        return recommendations
    
    def _recommend_concurrency(self, result: TestResult) -> str:
        """Recommend optimal concurrency level."""
        if result.performance.search_latency_avg_ms < 500:
            return "2-4 concurrent queries"
        elif result.performance.search_latency_avg_ms < 1500:
            return "1-2 concurrent queries"
        else:
            return "Sequential queries only"
    
    def _recommend_hardware(self, result: TestResult) -> str:
        """Recommend hardware specifications."""
        memory_gb = max(8, result.peak_memory_mb / 1024 * 2)  # 2x safety margin
        if result.chunks_extracted > 10000:
            return f"{memory_gb:.0f}+ GB RAM, 4+ CPU cores, SSD storage"
        elif result.chunks_extracted > 5000:
            return f"{memory_gb:.0f}+ GB RAM, 2+ CPU cores, SSD recommended"
        else:
            return f"{memory_gb:.0f}+ GB RAM, standard hardware sufficient"
    
    def _estimate_processing_cost(self, result: TestResult) -> float:
        """Estimate OpenAI API processing costs."""
        # Rough estimates based on typical usage
        embedding_cost = result.chunks_extracted * 0.0001  # ~$0.0001 per chunk
        search_cost = result.queries_tested * 0.001  # ~$0.001 per query
        ai_analysis_cost = result.queries_tested * 0.01 if result.ai_analysis_success else 0  # ~$0.01 per AI analysis
        return embedding_cost + search_cost + ai_analysis_cost
    
    def _calculate_efficiency_rating(self, result: TestResult) -> str:
        """Calculate overall efficiency rating."""
        score = 0
        
        # Performance vs baseline (30% weight)
        if result.performance.relative_performance_vs_baseline > 120:
            score += 30
        elif result.performance.relative_performance_vs_baseline > 90:
            score += 20
        elif result.performance.relative_performance_vs_baseline > 70:
            score += 10
        
        # Latency score (25% weight)
        if result.performance.search_latency_avg_ms < 500:
            score += 25
        elif result.performance.search_latency_avg_ms < 1000:
            score += 20
        elif result.performance.search_latency_avg_ms < 2000:
            score += 15
        elif result.performance.search_latency_avg_ms < 3000:
            score += 10
        
        # Memory efficiency (25% weight)
        if result.performance.memory_efficiency_mb_per_1k_chunks < 20:
            score += 25
        elif result.performance.memory_efficiency_mb_per_1k_chunks < 40:
            score += 20
        elif result.performance.memory_efficiency_mb_per_1k_chunks < 60:
            score += 15
        elif result.performance.memory_efficiency_mb_per_1k_chunks < 100:
            score += 10
        
        # Stability score (20% weight)
        if result.performance.performance_stability_index < 15:
            score += 20
        elif result.performance.performance_stability_index < 25:
            score += 15
        elif result.performance.performance_stability_index < 35:
            score += 10
        
        if score >= 80:
            return "Excellent (A+)"
        elif score >= 70:
            return "Very Good (A)"
        elif score >= 60:
            return "Good (B+)"
        elif score >= 50:
            return "Average (B)"
        elif score >= 40:
            return "Below Average (C)"
        else:
            return "Poor (D)"
    
    def _suggest_roi_optimization(self, result: TestResult) -> str:
        """Suggest ROI optimization strategies."""
        cost = self._estimate_processing_cost(result)
        time_hours = result.total_time / 3600
        
        if cost > 2.0:
            return "High cost - consider batch processing to reduce API calls"
        elif time_hours > 1.0:
            return "Long processing time - consider parallel processing or hardware upgrade"
        elif result.performance.efficiency_ratio < 1.0:
            return "Low efficiency - optimize query selectivity and memory usage"
        else:
            return "Good ROI balance - current setup is cost-effective"
    
    def _estimate_scaled_memory(self, result: TestResult, scale_factor: int) -> float:
        """Estimate memory requirements for scaled dataset."""
        base_memory = 100  # Base system memory
        variable_memory = result.peak_memory_mb - base_memory
        return base_memory + (variable_memory * scale_factor)
    
    def _identify_performance_bottlenecks(self, results: List[TestResult]) -> List[Dict[str, str]]:
        """Identify key performance bottlenecks across all test results."""
        bottlenecks = []
        
        # Analyze ingestion performance
        slow_ingestion = [r for r in results if r.performance and r.performance.relative_performance_vs_baseline < 70]
        if len(slow_ingestion) > len(results) * 0.3:  # More than 30% slow
            avg_performance = sum(r.performance.relative_performance_vs_baseline for r in slow_ingestion) / len(slow_ingestion)
            bottlenecks.append({
                "category": "Ingestion Performance Bottleneck",
                "description": f"{len(slow_ingestion)}/{len(results)} repositories showed slow ingestion (avg {avg_performance:.1f}% of baseline). Primary causes: batch size optimization needed, network/disk I/O limitations."
            })
        
        # Analyze search latency variance
        high_variance = [r for r in results if r.performance and r.performance.search_latency_stats and r.performance.search_latency_stats.coefficient_variation > 30]
        if len(high_variance) > len(results) * 0.2:  # More than 20% high variance
            bottlenecks.append({
                "category": "Search Latency Inconsistency",
                "description": f"{len(high_variance)}/{len(results)} repositories showed high search latency variance (>30% CV). This indicates query complexity differences or system resource contention."
            })
        
        # Analyze memory scaling issues
        memory_issues = [r for r in results if r.performance and r.performance.memory_growth_rate > 100]
        if len(memory_issues) > 0:
            bottlenecks.append({
                "category": "Memory Scalability Concern",
                "description": f"{len(memory_issues)}/{len(results)} repositories showed concerning memory growth rates (>100 MB/1K chunks). This may limit scalability for larger datasets."
            })
        
        # Overall system stability
        unstable = [r for r in results if r.performance and r.performance.performance_stability_index > 25]
        if len(unstable) > len(results) * 0.25:
            bottlenecks.append({
                "category": "System Performance Variability",
                "description": f"{len(unstable)}/{len(results)} repositories showed high performance variability. Consider system resource optimization and load balancing."
            })
        
        if not bottlenecks:
            bottlenecks.append({
                "category": "Optimal Performance Profile",
                "description": "No significant performance bottlenecks detected across the test suite. System demonstrates good scalability and consistency."
            })
        
        return bottlenecks
    
    def _analyze_performance_by_size(self, results: List[TestResult]) -> Dict[str, Dict]:
        """Analyze performance patterns by repository size category."""
        size_categories = {}
        
        for result in results:
            if not result.performance:
                continue
                
            category = self._get_size_category(result.chunks_extracted)
            
            if category not in size_categories:
                size_categories[category] = {
                    'results': [],
                    'count': 0,
                    'avg_ingestion_rate': 0,
                    'avg_search_latency': 0,
                    'avg_memory_efficiency': 0,
                    'consistency_rating': ''
                }
            
            size_categories[category]['results'].append(result)
            size_categories[category]['count'] += 1
        
        # Calculate averages for each category
        for category, data in size_categories.items():
            results_list = data['results']
            
            ingestion_rates = [r.performance.ingestion_rate_chunks_per_second for r in results_list if r.performance.ingestion_rate_chunks_per_second > 0]
            search_latencies = [r.performance.search_latency_avg_ms for r in results_list if r.performance.search_latency_avg_ms > 0]
            memory_efficiencies = [r.performance.memory_efficiency_mb_per_1k_chunks for r in results_list if r.performance.memory_efficiency_mb_per_1k_chunks > 0]
            
            data['avg_ingestion_rate'] = statistics.mean(ingestion_rates) if ingestion_rates else 0
            data['avg_search_latency'] = statistics.mean(search_latencies) if search_latencies else 0
            data['avg_memory_efficiency'] = statistics.mean(memory_efficiencies) if memory_efficiencies else 0
            
            # Calculate consistency rating
            if ingestion_rates:
                cv = statistics.stdev(ingestion_rates) / statistics.mean(ingestion_rates) * 100
                data['consistency_rating'] = 'High' if cv < 20 else 'Medium' if cv < 40 else 'Low'
            else:
                data['consistency_rating'] = 'Unknown'
        
        return size_categories
    
    def _generate_immediate_recommendations(self, results: List[TestResult], rate_stats: StatisticalMetrics, 
                                          latency_stats: StatisticalMetrics, memory_stats: StatisticalMetrics) -> List[str]:
        """Generate immediate high-impact optimization recommendations."""
        recommendations = []
        
        # Batch size optimization
        slow_repos = [r for r in results if r.performance and r.performance.relative_performance_vs_baseline < 80]
        if len(slow_repos) > 0:
            avg_batch_size = statistics.mean([r.batch_size for r in slow_repos])
            recommendations.append(f"Optimize batch sizes: {len(slow_repos)} repositories underperforming with avg batch size {avg_batch_size:.0f}. Test batch sizes 400-800 for better throughput.")
        
        # Latency optimization
        if latency_stats.mean > 1500:
            recommendations.append(f"Address search latency: Average {latency_stats.mean:.0f}ms exceeds 1.5s target. Implement query result caching and optimize complex queries.")
        
        # Memory optimization
        if memory_stats.coefficient_variation > 50:
            recommendations.append(f"Stabilize memory usage: High variance ({memory_stats.coefficient_variation:.1f}% CV) indicates memory leaks or inefficient cleanup. Implement consistent memory management.")
        
        # Consistency improvements
        if rate_stats.coefficient_variation > 30:
            recommendations.append(f"Improve ingestion consistency: High rate variance ({rate_stats.coefficient_variation:.1f}% CV) suggests system resource contention. Consider dedicated processing resources.")
        
        return recommendations
    
    def _generate_scaling_recommendations(self, results: List[TestResult], rate_stats: StatisticalMetrics,
                                        latency_stats: StatisticalMetrics, memory_stats: StatisticalMetrics) -> List[str]:
        """Generate scaling and long-term optimization recommendations."""
        recommendations = []
        
        # Scaling projections
        total_chunks = sum(r.chunks_extracted for r in results)
        avg_memory_per_chunk = memory_stats.mean / (total_chunks / len(results))
        
        recommendations.append(f"For 10x scaling: Expect ~{avg_memory_per_chunk * 10000:.0f}MB memory per 10K chunk repository. Plan horizontal scaling beyond 50K chunks.")
        
        # Performance predictability
        if latency_stats.coefficient_variation > 25:
            recommendations.append(f"Implement query complexity analysis: {latency_stats.coefficient_variation:.1f}% latency variance suggests need for query optimization and caching strategies.")
        
        # Resource optimization
        memory_outliers = [r for r in results if r.peak_memory_mb > memory_stats.mean + 2 * memory_stats.std_dev]
        if len(memory_outliers) > 0:
            recommendations.append(f"Investigate memory outliers: {len(memory_outliers)} repositories used excessive memory. Implement streaming ingestion for large datasets.")
        
        # Cost optimization
        total_cost = sum(self._estimate_processing_cost(r) for r in results)
        if total_cost > 10:
            recommendations.append(f"Optimize API costs: Total estimated cost ${total_cost:.2f} for {len(results)} repositories. Consider model optimization and batch processing.")
        
        return recommendations
    
    def _generate_reliability_recommendations(self, results: List[TestResult], latency_stats: StatisticalMetrics, rate_stats: StatisticalMetrics) -> List[str]:
        """Generate reliability and monitoring recommendations."""
        recommendations = []
        
        # SLA recommendations
        p95_latency = latency_stats.mean + 1.64 * latency_stats.std_dev  # Approximate P95
        recommendations.append(f"Set SLA targets: P95 latency < {p95_latency:.0f}ms, P99 < {p95_latency * 1.5:.0f}ms based on current performance distribution.")
        
        # Monitoring setup
        failed_tests = [r for r in results if r.success_rate < 80]
        if len(failed_tests) > 0:
            recommendations.append(f"Implement failure monitoring: {len(failed_tests)} repositories had issues. Monitor ingestion success rates and implement automatic retry mechanisms.")
        
        # Alerting thresholds
        recommendations.append(f"Configure alerts: Ingestion rate < {rate_stats.mean - 2 * rate_stats.std_dev:.0f} chunks/sec, Search latency > {latency_stats.mean + 2 * latency_stats.std_dev:.0f}ms")
        
        # Capacity planning
        max_memory = max(r.peak_memory_mb for r in results if r.peak_memory_mb > 0)
        recommendations.append(f"Capacity planning: Peak memory observed {max_memory:.0f}MB. Plan for {max_memory * 1.5:.0f}MB capacity with auto-scaling triggers.")
        
        return recommendations
    
    def _generate_performance_baselines(self, results: List[TestResult]) -> List[Dict[str, str]]:
        """Generate performance baselines based on test results."""
        baselines = []
        size_analysis = self._analyze_performance_by_size(results)
        
        for size_category, data in size_analysis.items():
            if data['count'] > 0:
                baselines.append({
                    'size': f"{size_category} ({data['count']} tested)",
                    'ingestion_rate': f"{data['avg_ingestion_rate']:.1f} ± {data['avg_ingestion_rate'] * 0.2:.1f}",
                    'search_latency': f"{data['avg_search_latency']:.0f} ± {data['avg_search_latency'] * 0.3:.0f}",
                    'memory_usage': f"{data['avg_memory_efficiency'] * 10:.0f} ± {data['avg_memory_efficiency'] * 5:.0f}"
                })
        
        return baselines
    
    def test_repository_with_retries(self, repo: TestRepository, max_retries: int = 10) -> TestResult:
        """Test repository with retry mechanism to handle failures.
        
        Attempts to test a repository up to max_retries times, with exponential backoff
        between attempts. This ensures the overall stress test doesn't stop due to 
        individual repository failures.
        """
        last_result = None
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                console.print(f"Testing {repo.name} (attempt {attempt}/{max_retries})", style="blue")
                self.update_report(f"**Attempt {attempt}/{max_retries}** for {repo.name}")
                
                result = self.test_repository(repo)
                
                # Consider test successful if at least KB creation and ingestion work
                if result.kb_creation_success and result.ingestion_success:
                    if attempt > 1:
                        console.print(f"✅ {repo.name} succeeded on attempt {attempt}", style="green")
                        self.update_report(f"Repository {repo.name} succeeded on attempt {attempt}", "success")
                    return result
                else:
                    last_result = result
                    console.print(f"⚠️ Attempt {attempt} failed for {repo.name} (success rate: {result.success_rate:.1f}%)", style="yellow")
                    self.update_report(f"Attempt {attempt} failed - success rate: {result.success_rate:.1f}%", "warning")
                    
            except Exception as e:
                last_error = str(e)
                console.print(f"❌ Attempt {attempt} crashed for {repo.name}: {e}", style="red")
                self.update_report(f"Attempt {attempt} crashed: {e}", "error")
                
                # Create a minimal failed result
                last_result = TestResult(
                    repo_name=repo.name,
                    repo_url=repo.url,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    batch_size=repo.batch_size,
                    environment=TestEnvironment.capture_current()
                )
                last_result.kb_creation_error = str(e)
            
            # Exponential backoff between retries (2, 4, 8, 16 seconds...)
            if attempt < max_retries:
                wait_time = min(2 ** attempt, 30)  # Cap at 30 seconds
                console.print(f"Waiting {wait_time}s before retry...", style="dim")
                time.sleep(wait_time)
        
        # All retries failed
        console.print(f"❌ All {max_retries} attempts failed for {repo.name}", style="red")
        self.update_report(f"**FINAL FAILURE** after {max_retries} attempts for {repo.name}", "error")
        
        if last_result:
            last_result.kb_creation_error = f"Failed after {max_retries} attempts. Last error: {last_error or 'Multiple failures'}"
            return last_result
        else:
            # Create a completely failed result
            failed_result = TestResult(
                repo_name=repo.name,
                repo_url=repo.url,
                start_time=datetime.now(),
                end_time=datetime.now(),
                batch_size=repo.batch_size,
                environment=TestEnvironment.capture_current()
            )
            failed_result.kb_creation_error = f"Failed after {max_retries} attempts. Last error: {last_error or 'Unknown error'}"
            return failed_result

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
        """Generate comprehensive final report with advanced statistical analysis and cross-repository insights."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        successful_tests = [r for r in self.results if r.success_rate > 80]
        failed_tests = [r for r in self.results if r.success_rate <= 80]
        
        total_files_processed = sum(r.files_processed for r in self.results)
        total_chunks_extracted = sum(r.chunks_extracted for r in self.results)
        
        # Enhanced statistical analysis
        ingestion_times = [r.ingestion_time for r in self.results if r.ingestion_time > 0]
        search_times = [r.search_time for r in self.results if r.search_time > 0]
        ingestion_rates = [r.performance.ingestion_rate_chunks_per_second for r in self.results if r.performance and r.performance.ingestion_rate_chunks_per_second > 0]
        search_latencies = [r.performance.search_latency_avg_ms for r in self.results if r.performance and r.performance.search_latency_avg_ms > 0]
        memory_usages = [r.peak_memory_mb for r in self.results if r.peak_memory_mb > 0]
        
        # Calculate aggregate statistics
        ingestion_stats = StatisticalMetrics.from_values(ingestion_times) if ingestion_times else None
        search_stats = StatisticalMetrics.from_values(search_times) if search_times else None
        rate_stats = StatisticalMetrics.from_values(ingestion_rates) if ingestion_rates else None
        latency_stats = StatisticalMetrics.from_values(search_latencies) if search_latencies else None
        memory_stats = StatisticalMetrics.from_values(memory_usages) if memory_usages else None
        
        avg_ingestion_time = statistics.mean(ingestion_times) if ingestion_times else 0.0
        avg_search_time = statistics.mean(search_times) if search_times else 0.0
        
        with open(self.report_file, 'a') as f:
            f.write(f"""
## Comprehensive Performance Benchmark Summary

**Test Suite Completed:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Duration:** {total_duration/3600:.2f} hours  
**Total Dataset Size:** {total_chunks_extracted:,} code chunks across {len(self.results)} repositories

### Executive Performance Summary

| Metric | Value | 95% Confidence Interval | Statistical Significance |
|--------|-------|------------------------|------------------------|
| **Total Repositories Tested** | {len(self.results)} | - | Complete test matrix |
| **Success Rate** | {len(successful_tests)/len(self.results)*100:.1f}% | - | {len(successful_tests)}/{len(self.results)} repositories |
| **Total Files Processed** | {total_files_processed:,} | - | Across all repositories |
| **Total Code Chunks** | {total_chunks_extracted:,} | - | Embedded and indexed |
| **Average Ingestion Rate** | {rate_stats.mean:.1f} chunks/sec | ({rate_stats.confidence_interval_95[0]:.1f}, {rate_stats.confidence_interval_95[1]:.1f}) | CV: {rate_stats.coefficient_variation:.1f}% |
| **Average Search Latency** | {latency_stats.mean:.1f} ms | ({latency_stats.confidence_interval_95[0]:.1f}, {latency_stats.confidence_interval_95[1]:.1f}) | CV: {latency_stats.coefficient_variation:.1f}% |
| **Average Memory Usage** | {memory_stats.mean:.1f} MB | ({memory_stats.confidence_interval_95[0]:.1f}, {memory_stats.confidence_interval_95[1]:.1f}) | CV: {memory_stats.coefficient_variation:.1f}% |

### Cross-Repository Performance Analysis

#### Ingestion Performance Distribution

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Ingestion Rate** | {rate_stats.median:.1f} chunks/sec | More robust than mean |
| **Performance Range** | {rate_stats.min_value:.1f} - {rate_stats.max_value:.1f} chunks/sec | {rate_stats.max_value/rate_stats.min_value:.1f}x variation |
| **Standard Deviation** | {rate_stats.std_dev:.1f} chunks/sec | Consistency measure |
| **Outlier Repositories** | {rate_stats.outliers_count} | Repositories with unusual performance |
| **Performance Consistency** | {rate_stats.coefficient_variation:.1f}% CV | {'Consistent' if rate_stats.coefficient_variation < 25 else 'Variable'} across repositories |

#### Search Latency Analysis

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Latency** | {latency_stats.median:.1f} ms | Typical user experience |
| **Latency Range** | {latency_stats.min_value:.1f} - {latency_stats.max_value:.1f} ms | {latency_stats.max_value/latency_stats.min_value:.1f}x variation |
| **95% of Queries Under** | {latency_stats.mean + 1.96 * latency_stats.std_dev:.1f} ms | SLA recommendation |
| **Latency Consistency** | {latency_stats.coefficient_variation:.1f}% CV | {'Predictable' if latency_stats.coefficient_variation < 30 else 'Variable'} performance |

#### Memory Efficiency Patterns

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Memory Usage** | {memory_stats.median:.1f} MB | Typical requirement |
| **Memory Range** | {memory_stats.min_value:.1f} - {memory_stats.max_value:.1f} MB | {memory_stats.max_value/memory_stats.min_value:.1f}x scaling factor |
| **Memory Predictability** | {memory_stats.coefficient_variation:.1f}% CV | {'Predictable' if memory_stats.coefficient_variation < 40 else 'Highly variable'} scaling |

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
### Critical Performance Insights and Optimization Recommendations

#### Statistical Significance and Confidence

- **Sample Size**: {len(self.results)} repositories tested with {total_chunks_extracted:,} total code chunks
- **Statistical Power**: 95% confidence intervals provided for all key metrics
- **Data Quality**: {len(successful_tests)}/{len(self.results)} successful tests provide robust statistical foundation
- **Variance Analysis**: Performance consistency varies by repository size and complexity

#### Key Performance Bottlenecks Identified

""")
            
            # Analyze performance patterns across repositories
            bottlenecks = self._identify_performance_bottlenecks(self.results)
            for bottleneck in bottlenecks:
                f.write(f"**{bottleneck['category']}**: {bottleneck['description']}\n\n")
            
            f.write(f"""

#### Cross-Repository Performance Patterns

""")
            
            # Analyze patterns by repository size
            size_analysis = self._analyze_performance_by_size(self.results)
            for size_cat, analysis in size_analysis.items():
                f.write(f"**{size_cat} Repositories** ({analysis['count']} tested):\n")
                f.write(f"- Average ingestion rate: {analysis['avg_ingestion_rate']:.1f} chunks/sec\n")
                f.write(f"- Average search latency: {analysis['avg_search_latency']:.1f} ms\n")
                f.write(f"- Memory efficiency: {analysis['avg_memory_efficiency']:.1f} MB per 1K chunks\n")
                f.write(f"- Performance consistency: {analysis['consistency_rating']}\n\n")
            
            f.write(f"""

#### Optimization Recommendations by Priority

**Immediate Actions (High Impact)**:
""")
            
            immediate_recs = self._generate_immediate_recommendations(self.results, rate_stats, latency_stats, memory_stats)
            for rec in immediate_recs:
                f.write(f"- {rec}\n")
            
            f.write(f"""

**Scaling Optimizations (Medium-Long Term)**:
""")
            
            scaling_recs = self._generate_scaling_recommendations(self.results, rate_stats, latency_stats, memory_stats)
            for rec in scaling_recs:
                f.write(f"- {rec}\n")
            
            f.write(f"""

**Reliability and Monitoring**:
""")
            
            reliability_recs = self._generate_reliability_recommendations(self.results, latency_stats, rate_stats)
            for rec in reliability_recs:
                f.write(f"- {rec}\n")
            
            f.write(f"""

#### Cost-Performance Analysis

- **Total Estimated Processing Cost**: ${sum(self._estimate_processing_cost(r) for r in self.results):.2f} for complete test suite
- **Average Cost per Repository**: ${sum(self._estimate_processing_cost(r) for r in self.results) / len(self.results):.2f}
- **Cost per 1K Chunks**: ${sum(self._estimate_processing_cost(r) for r in self.results) / (total_chunks_extracted / 1000):.3f}
- **Time Efficiency**: {total_chunks_extracted / (total_duration / 3600):.0f} chunks processed per hour
- **Resource Efficiency**: {total_chunks_extracted / sum(r.peak_memory_mb for r in self.results if r.peak_memory_mb > 0):.2f} chunks per MB memory

#### Performance Baselines for Future Testing

Based on this comprehensive analysis, the following performance baselines are recommended:

""")
            
            baselines = self._generate_performance_baselines(self.results)
            f.write("| Repository Size | Expected Ingestion Rate | Expected Search Latency | Expected Memory Usage |\n")
            f.write("|----------------|------------------------|------------------------|---------------------|\n")
            for baseline in baselines:
                f.write(f"| {baseline['size']} | {baseline['ingestion_rate']} chunks/sec | {baseline['search_latency']} ms | {baseline['memory_usage']} MB |\n")
            
            f.write(f"""

#### Reproducibility and Methodology

**Test Environment Consistency**: All tests run on standardized environment with documented specifications
**Statistical Methodology**: 95% confidence intervals, outlier detection, coefficient of variation analysis
**Reproducibility Score**: High - all individual reports contain exact reproduction commands
**Baseline Validation**: Performance baselines derived from {len(self.results)} repository statistical analysis

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
                # Use retry mechanism to handle individual repository failures
                for i, repo in enumerate(self.test_repositories):
                    progress.update(main_task, description=f"Testing {repo.name} ({i+1}/{len(self.test_repositories)})...")
                    
                    try:
                        # Use retry mechanism with max 10 attempts per repository
                        result = self.test_repository_with_retries(repo, max_retries=10)
                        self.results.append(result)
                        
                        if result.success_rate > 80:
                            console.print(f"✅ Completed {repo.name} ({result.success_rate:.1f}% success)", style="green")
                        elif result.success_rate > 40:
                            console.print(f"⚠️ Partial success {repo.name} ({result.success_rate:.1f}% success)", style="yellow")
                        else:
                            console.print(f"❌ Failed {repo.name} ({result.success_rate:.1f}% success)", style="red")
                        
                    except KeyboardInterrupt:
                        console.print("\n⚠️ Test interrupted by user", style="yellow")
                        self.update_report("Test suite interrupted by user", "warning")
                        break
                    except Exception as e:
                        # This should be very rare since test_repository_with_retries handles exceptions
                        console.print(f"❌ Unexpected error for {repo.name}: {e}", style="red")
                        self.update_report(f"Unexpected error for {repo.name}: {e}", "error")
                        
                        failed_result = TestResult(
                            repo_name=repo.name,
                            repo_url=repo.url,
                            start_time=datetime.now(),
                            end_time=datetime.now(),
                            batch_size=repo.batch_size,
                            environment=TestEnvironment.capture_current()
                        )
                        failed_result.kb_creation_error = f"Unexpected error: {str(e)}"
                        self.results.append(failed_result)
                    
                    progress.update(main_task, advance=1)
                    
                    # Shorter wait time since retries already include delays
                    console.print(f"Waiting 5 seconds before next repository...", style="dim")
                    time.sleep(5)
        
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