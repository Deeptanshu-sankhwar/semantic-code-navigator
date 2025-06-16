# Benchmark Report: flask-hello-world

**Repository:** https://github.com/miguelgrinberg/flasky  
**Test Date:** 2025-06-16 09:15:05  
**Duration:** 90.81 seconds  
**Success Rate:** 100.0%  

## Executive Summary

This report provides comprehensive performance benchmarks for the flask-hello-world repository ingestion and search workflow using the Semantic Code Navigator. The test demonstrates reproducible performance metrics across the complete pipeline from repository cloning to AI-enhanced semantic search.

### Key Performance Indicators

| Metric | Value | Unit |
|--------|-------|------|
| **Dataset Size** | 221 | code chunks |
| **Files Processed** | 39 | files |
| **Ingestion Rate** | 5.8 | chunks/second |
| **Search Latency (Avg)** | 3066.9 | milliseconds |
| **Memory Efficiency** | 87.4 | MB per 1K chunks |
| **Throughput** | 0.33 | queries/second |

## Test Environment

### Hardware Specifications
- **Platform:** Darwin 24.5.0 (arm64)
- **CPU Cores:** 8
- **Total Memory:** 16.0 GB
- **Available Memory:** 3.0 GB
- **Disk Space:** 16.3 GB

### Software Environment
- **Python Version:** 3.13.3
- **MindsDB Version:** Latest
- **Embedding Model:** text-embedding-3-large
- **Reranking Model:** gpt-4o
- **Test Timestamp:** 2025-06-16T09:15:05.053717

## Repository Characteristics

### Dataset Overview
- **Repository URL:** https://github.com/miguelgrinberg/flasky
- **Primary Language:** Python
- **Estimated Files:** 60
- **Actual Files Processed:** 39
- **Code Chunks Extracted:** 221
- **Batch Size Used:** 20

### Language Distribution
| Language | Chunks | Percentage |
|----------|--------|------------|
| python | 221 | 100.0% |


## Performance Benchmarks

### Ingestion Performance

| Metric | Value | Benchmark Category |
|--------|-------|-------------------|
| **Total Ingestion Time** | 37.92 seconds | Good |
| **Chunks per Second** | 5.8 | Slow |
| **Files per Second** | 1.0 | Average |
| **Time per 1K Chunks** | 171.6 seconds | Slow |

### Search Performance

| Metric | Value | Benchmark Category |
|--------|-------|-------------------|
| **Average Latency** | 3066.9 ms | Slow |
| **95th Percentile** | 0.0 ms | Excellent |
| **99th Percentile** | 0.0 ms | Excellent |
| **Queries per Second** | 0.33 | Slow |

### Memory Efficiency

| Metric | Value | Benchmark Category |
|--------|-------|-------------------|
| **Peak Memory Usage** | 19.3 MB | Excellent |
| **Memory per 1K Chunks** | 87.4 MB | Inefficient |
| **CPU Usage Peak** | 0.0% | Low |

## Detailed Test Results

### Workflow Step Performance

| Step | Status | Duration | Notes |
|------|--------|----------|-------|
| **KB Creation** | ✓ Success | 7.37s | Completed successfully |
| **Data Ingestion** | ✓ Success | 37.92s | Completed successfully |
| **Index Creation** | ✓ Success | 1.26s | Completed successfully |
| **Semantic Search** | ✓ Success | 9.20s | Completed successfully |
| **AI Analysis** | ✓ Success | 16.48s | Completed successfully |

### Search Query Performance
| Query # | Response Time (ms) | Status |
|---------|-------------------|--------|
| 1 | 3132.4 | ✗ Very Slow |
| 2 | 3528.6 | ✗ Very Slow |
| 3 | 2539.7 | ⚠ Slow |


## Reproducibility Information

### Test Methodology

This benchmark follows a standardized methodology for reproducible results:

1. **Environment Setup**: Fresh MindsDB instance with clean knowledge base
2. **Repository Cloning**: Clone from https://github.com/miguelgrinberg/flasky using detected default branch
3. **Code Extraction**: AST-based parsing for Python files with metadata extraction
4. **Batch Processing**: Insert 20 chunks per batch for optimal performance
5. **Search Testing**: Execute 3 semantic queries with natural language
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
python -m src.cli kb:ingest https://github.com/miguelgrinberg/flasky --batch-size 20 --extract-git-info
python -m src.cli kb:query "authentication and login validation" --limit 3
python -m src.cli ai:init --force
python -m src.cli kb:query "authentication and login validation" --limit 2 --ai-all
```

### Performance Baselines

Based on repository size category (Small):

| Metric | Expected Range | Actual Result | Status |
|--------|----------------|---------------|--------|
| **Ingestion Rate** | 30-60 chunks/sec | 5.8 | Below Expected |
| **Search Latency** | < 2000 ms | 3066.9 ms | Needs Improvement |
| **Memory Usage** | 66-133 MB | 19.3 MB | Efficient |

## Recommendations

### Performance Optimization
- Consider increasing batch size for better ingestion performance
- Search latency is high - consider optimizing query complexity


### Scaling Considerations

For repositories of similar size (221 chunks):
- **Optimal Batch Size**: 100
- **Memory Requirements**: 4 GB minimum
- **Expected Duration**: 1 minutes

---

**Report Generated:** 2025-06-16 09:16:39  
**Tool Version:** Semantic Code Navigator v1.0  
**Report Format:** Individual Repository Benchmark v1.0  
