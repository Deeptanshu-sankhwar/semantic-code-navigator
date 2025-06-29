# Performance Benchmark Report: semantic-code-navigator

**Repository:** https://github.com/Deeptanshu-sankhwar/semantic-code-navigator  
**Test Date:** 2025-06-29 18:16:59  
**Duration:** 62.30 seconds  
**Success Rate:** 100.0%  
**Dataset Category:** Small

## Executive Summary

This report provides comprehensive performance benchmarks for the semantic-code-navigator repository using the Semantic Code Navigator. The analysis includes statistical significance testing, confidence intervals, and critical optimization insights for reproducible performance evaluation.

### Key Performance Indicators

| Metric | Value | Unit | Baseline Comparison |
|--------|-------|------|-------------------|
| **Dataset Size** | 69 | code chunks | Small category |
| **Files Processed** | 15 | files | - |
| **Ingestion Rate** | 5.4 | chunks/second | ⚠ Below range (5.4 < 20) |
| **Search Latency (Avg)** | 3533.5 | milliseconds | ⚡ Above range (3533.5 > 800) |
| **Memory Efficiency** | 250.2 | MB per 1K chunks | - |
| **Throughput** | 0.28 | queries/second | - |
| **Performance vs Baseline** | 13.5% | relative | Below expected |
| **Stability Index** | 6.5 | consistency score | Stable |

## Test Environment

### Hardware Specifications
- **Platform:** Darwin 24.5.0 (arm64)
- **CPU Cores:** 8
- **Total Memory:** 16.0 GB
- **Available Memory:** 3.3 GB
- **Disk Space:** 6.8 GB

### Software Environment
- **Python Version:** 3.13.3
- **MindsDB Version:** Latest
- **Embedding Model:** text-embedding-3-large
- **Reranking Model:** gpt-3.5-turbo
- **Test Timestamp:** 2025-06-29T18:16:59.023262

## Repository Characteristics

### Dataset Overview
- **Repository URL:** https://github.com/Deeptanshu-sankhwar/semantic-code-navigator
- **Primary Language:** Python
- **Estimated Files:** 60
- **Actual Files Processed:** 15
- **Code Chunks Extracted:** 69
- **Batch Size Used:** 120

### Language Distribution
| Language | Chunks | Percentage |
|----------|--------|------------|
| python | 69 | 100.0% |
