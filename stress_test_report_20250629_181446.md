# Semantic Code Navigator - Comprehensive Stress Test Report

**Test Suite Started:** 2025-06-29 18:14:46

## Test Overview

This comprehensive stress test evaluates the complete workflow of the Semantic Code Navigator:

1. **Knowledge Base Creation** - Initialize MindsDB KB with embedding models
2. **Data Ingestion** - Clone repositories and extract code chunks  
3. **Index Creation** - Optimize KB for search performance
4. **Semantic Search** - Query with natural language and metadata filters
5. **AI Analysis** - Enhance results with AI tables for classification and explanation

### Test Repositories

Testing on **2** repositories ranging from ~50 to 3000+ files:

| Repository | Est. Files | Language | Batch Size | Max Queries | Description |
|------------|------------|----------|------------|-------------|-------------|
| price-tracker | 110 | TypeScript | 220 | 22 | Crypto price tracker |
| semantic-code-navigator | 60 | Python | 120 | 15 | Semantic code navigator |

### Test Parameters

- **Search Queries:** 10 different semantic queries
- **Batch Size Variation:** From 100 to 1000 based on repository size
- **Test Execution:** Serial execution (one repository at a time)
- **Memory Management:** KB reset after each test to free memory
- **Cost Optimization:** No AI summary generation to reduce OpenAI costs
- **Individual Reports:** Detailed benchmark reports saved to `results/` directory
- **Performance Metrics:** P95/P99 latency, throughput, memory efficiency tracking

---

## Test Results


**18:14:46** [START] \\# Stress Test Suite Started

**18:14:46** [INFO] \\*\\*Attempt 1/10\\*\\* for price-tracker

**18:14:46** [START] \\#\\#\\# Testing Repository: price-tracker

**18:14:46** [INFO] - \\*\\*URL:\\*\\* https://github.com/Deeptanshu-sankhwar/crypto-price-tracker

**18:14:46** [INFO] - \\*\\*Estimated Files:\\*\\* 110

**18:14:46** [INFO] - \\*\\*Language:\\*\\* TypeScript

**18:14:46** [INFO] - \\*\\*Batch Size:\\*\\* 220

**18:14:46** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 22

**18:14:46** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:15:10** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
│ Semantic Code Navigator             │
│ Initializing MindsDB Knowledge Base │
╰─────────────────────────────────────╯
Validating configuration...
Configuration is valid
Connected to MindsDB
Query execution failed: \\('Connection aborted.', RemoteDisconnected\\('Remote end closed
connection without response'\\)\\)
Query execution failed: \\('Connection aborted.', RemoteDisconnected\\('Remote end closed
connection without response'\\)\\)
Failed to create knowledge base: \\('Connection aborted.', RemoteDisconnected\\('Remote
end closed connection without response'\\)\\)
⠋ Failed to create knowledge base
Disconnected from MindsDB

**18:15:10** [WARNING] Attempt 1 failed - success rate: 0.0%

**18:15:12** [INFO] \\*\\*Attempt 2/10\\*\\* for price-tracker

**18:15:12** [START] \\#\\#\\# Testing Repository: price-tracker

**18:15:12** [INFO] - \\*\\*URL:\\*\\* https://github.com/Deeptanshu-sankhwar/crypto-price-tracker

**18:15:12** [INFO] - \\*\\*Estimated Files:\\*\\* 110

**18:15:12** [INFO] - \\*\\*Language:\\*\\* TypeScript

**18:15:12** [INFO] - \\*\\*Batch Size:\\*\\* 220

**18:15:12** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 22

**18:15:12** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:15:28** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
│ Semantic Code Navigator             │
│ Initializing MindsDB Knowledge Base │
╰─────────────────────────────────────╯
Validating configuration...
Configuration is valid
Connected to MindsDB
Query execution failed: \\('Connection aborted.', RemoteDisconnected\\('Remote end closed
connection without response'\\)\\)
Query execution failed: \\('Connection aborted.', RemoteDisconnected\\('Remote end closed
connection without response'\\)\\)
Failed to create knowledge base: \\('Connection aborted.', RemoteDisconnected\\('Remote
end closed connection without response'\\)\\)
⠋ Failed to create knowledge base
Disconnected from MindsDB

**18:15:28** [WARNING] Attempt 2 failed - success rate: 0.0%

**18:15:32** [INFO] \\*\\*Attempt 3/10\\*\\* for price-tracker

**18:15:32** [START] \\#\\#\\# Testing Repository: price-tracker

**18:15:32** [INFO] - \\*\\*URL:\\*\\* https://github.com/Deeptanshu-sankhwar/crypto-price-tracker

**18:15:32** [INFO] - \\*\\*Estimated Files:\\*\\* 110

**18:15:32** [INFO] - \\*\\*Language:\\*\\* TypeScript

**18:15:32** [INFO] - \\*\\*Batch Size:\\*\\* 220

**18:15:32** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 22

**18:15:32** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:15:46** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 12.84s

**18:15:46** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**18:16:05** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 18.96s

**18:16:05** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**18:16:16** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 9.73s

**18:16:16** [INFO]   - Files Processed: 8

**18:16:16** [INFO]   - Chunks Extracted: 13

**18:16:16** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**18:16:20** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 3.53s

**18:16:20** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**18:16:30** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 10.70s

**18:16:30** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**18:16:46** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 15.75s

**18:16:46** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**18:16:54** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 7.46s

**18:16:54** [INFO] \\#\\#\\#\\# Test Summary

**18:16:54** [INFO] - \\*\\*Total Time:\\*\\* 73.83s

**18:16:54** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**18:16:54** [INFO] - \\*\\*Peak Memory:\\*\\* 16.1 MB

**18:16:54** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**18:16:54** [INFO] ---

**18:16:54** [SUCCESS] Repository price-tracker succeeded on attempt 3

**18:16:59** [INFO] \\*\\*Attempt 1/10\\*\\* for semantic-code-navigator

**18:16:59** [START] \\#\\#\\# Testing Repository: semantic-code-navigator

**18:16:59** [INFO] - \\*\\*URL:\\*\\* https://github.com/Deeptanshu-sankhwar/semantic-code-navigator

**18:16:59** [INFO] - \\*\\*Estimated Files:\\*\\* 60

**18:16:59** [INFO] - \\*\\*Language:\\*\\* Python

**18:16:59** [INFO] - \\*\\*Batch Size:\\*\\* 120

**18:16:59** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 15

**18:16:59** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:17:01** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 1.33s

**18:17:02** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**18:17:18** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 16.14s

**18:17:18** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**18:17:31** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 12.78s

**18:17:31** [INFO]   - Files Processed: 15

**18:17:31** [INFO]   - Chunks Extracted: 69

**18:17:31** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**18:17:32** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 1.31s

**18:17:32** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**18:17:43** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 10.60s

**18:17:43** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**18:18:01** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 17.71s

**18:18:01** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**18:18:06** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 4.74s

**18:18:06** [INFO] \\#\\#\\#\\# Test Summary

**18:18:06** [INFO] - \\*\\*Total Time:\\*\\* 62.30s

**18:18:06** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**18:18:06** [INFO] - \\*\\*Peak Memory:\\*\\* 17.3 MB

**18:18:06** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**18:18:06** [INFO] ---

## Comprehensive Performance Benchmark Summary

**Test Suite Completed:** 2025-06-29 18:18:11  
**Total Duration:** 0.06 hours  
**Total Dataset Size:** 82 code chunks across 2 repositories

### Executive Performance Summary

| Metric | Value | 95% Confidence Interval | Statistical Significance |
|--------|-------|------------------------|------------------------|
| **Total Repositories Tested** | 2 | - | Complete test matrix |
| **Success Rate** | 100.0% | - | 2/2 repositories |
| **Total Files Processed** | 23 | - | Across all repositories |
| **Total Code Chunks** | 82 | - | Embedded and indexed |
| **Average Ingestion Rate** | 3.4 chunks/sec | (-0.6, 7.3) | CV: 85.3% |
| **Average Search Latency** | 3550.8 ms | (3516.9, 3584.7) | CV: 0.7% |
| **Average Memory Usage** | 16.7 MB | (15.6, 17.8) | CV: 4.8% |

### Cross-Repository Performance Analysis

#### Ingestion Performance Distribution

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Ingestion Rate** | 3.4 chunks/sec | More robust than mean |
| **Performance Range** | 1.3 - 5.4 chunks/sec | 4.0x variation |
| **Standard Deviation** | 2.9 chunks/sec | Consistency measure |
| **Outlier Repositories** | 0 | Repositories with unusual performance |
| **Performance Consistency** | 85.3% CV | Variable across repositories |

#### Search Latency Analysis

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Latency** | 3550.8 ms | Typical user experience |
| **Latency Range** | 3533.5 - 3568.1 ms | 1.0x variation |
| **95% of Queries Under** | 3598.8 ms | SLA recommendation |
| **Latency Consistency** | 0.7% CV | Predictable performance |

#### Memory Efficiency Patterns

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Memory Usage** | 16.7 MB | Typical requirement |
| **Memory Range** | 16.1 - 17.3 MB | 1.1x scaling factor |
| **Memory Predictability** | 4.8% CV | Predictable scaling |

### Performance Analysis

#### Ingestion Performance by Repository Size

| Repository | Files | Chunks | Batch Size | Ingestion Time | Chunks/Second |
|------------|-------|--------|------------|----------------|---------------|
| price-tracker | 8 | 13 | 220 | 9.73s | 1.3 |
| semantic-code-navigator | 15 | 69 | 120 | 12.78s | 5.4 |

#### Search Performance Analysis

| Repository | Queries Tested | Avg Response Time | Total Results | Results/Query |
|------------|----------------|-------------------|---------------|---------------|
| price-tracker | 3 | 10.70s | 9 | 3.0 |
| semantic-code-navigator | 3 | 10.60s | 9 | 3.0 |

### Failure Analysis

#### Failed Tests

### Critical Performance Insights and Optimization Recommendations

#### Statistical Significance and Confidence

- **Sample Size**: 2 repositories tested with 82 total code chunks
- **Statistical Power**: 95% confidence intervals provided for all key metrics
- **Data Quality**: 2/2 successful tests provide robust statistical foundation
- **Variance Analysis**: Performance consistency varies by repository size and complexity

#### Key Performance Bottlenecks Identified

**Ingestion Performance Bottleneck**: 2/2 repositories showed slow ingestion (avg 8.4% of baseline). Primary causes: batch size optimization needed, network/disk I/O limitations.



#### Cross-Repository Performance Patterns

**Small Repositories** (2 tested):
- Average ingestion rate: 3.4 chunks/sec
- Average search latency: 3550.8 ms
- Memory efficiency: 745.9 MB per 1K chunks
- Performance consistency: Low



#### Optimization Recommendations by Priority

**Immediate Actions (High Impact)**:
- Optimize batch sizes: 2 repositories underperforming with avg batch size 170. Test batch sizes 400-800 for better throughput.
- Address search latency: Average 3551ms exceeds 1.5s target. Implement query result caching and optimize complex queries.
- Improve ingestion consistency: High rate variance (85.3% CV) suggests system resource contention. Consider dedicated processing resources.


**Scaling Optimizations (Medium-Long Term)**:
- For 10x scaling: Expect ~4074MB memory per 10K chunk repository. Plan horizontal scaling beyond 50K chunks.


**Reliability and Monitoring**:
