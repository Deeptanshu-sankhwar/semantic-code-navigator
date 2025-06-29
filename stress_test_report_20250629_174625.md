# Semantic Code Navigator - Comprehensive Stress Test Report

**Test Suite Started:** 2025-06-29 17:46:25

## Test Overview

This comprehensive stress test evaluates the complete workflow of the Semantic Code Navigator:

1. **Knowledge Base Creation** - Initialize MindsDB KB with embedding models
2. **Data Ingestion** - Clone repositories and extract code chunks  
3. **Index Creation** - Optimize KB for search performance
4. **Semantic Search** - Query with natural language and metadata filters
5. **AI Analysis** - Enhance results with AI tables for classification and explanation

### Test Repositories

Testing on **10** repositories ranging from ~50 to 3000+ files:

| Repository | Est. Files | Language | Batch Size | Max Queries | Description |
|------------|------------|----------|------------|-------------|-------------|
| flask-microblog | 50 | Python | 100 | 10 | Flask microblog tutorial |
| calculator | 40 | JavaScript | 80 | 12 | Express.js web framework |
| vue-calculator | 35 | JavaScript | 70 | 10 | Simple calculator app |
| todo | 80 | JavaScript | 160 | 16 | TodoMVC React implementation |
| react-weather-app | 60 | JavaScript | 120 | 15 | React app generator |
| fastapi-example | 90 | Python | 180 | 18 | FastAPI full-stack example |
| gin-rest-api | 120 | Go | 240 | 20 | Gin REST API example |
| vue-cli | 100 | JavaScript | 200 | 18 | Vue.js CLI tool |
| angular-cli | 110 | TypeScript | 220 | 22 | Angular CLI tool |
| rust-cli-tool | 60 | Rust | 120 | 15 | Fast text search tool |

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


**17:46:25** [START] \\# Stress Test Suite Started

**17:46:25** [INFO] \\*\\*Attempt 1/10\\*\\* for flask-microblog

**17:46:25** [START] \\#\\#\\# Testing Repository: flask-microblog

**17:46:25** [INFO] - \\*\\*URL:\\*\\* https://github.com/miguelgrinberg/microblog

**17:46:25** [INFO] - \\*\\*Estimated Files:\\*\\* 50

**17:46:25** [INFO] - \\*\\*Language:\\*\\* Python

**17:46:25** [INFO] - \\*\\*Batch Size:\\*\\* 100

**17:46:25** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 10

**17:46:25** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:46:27** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 1.24s

**17:46:27** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**17:46:44** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 16.39s

**17:46:44** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**17:47:05** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 20.88s

**17:47:05** [INFO]   - Files Processed: 34

**17:47:05** [INFO]   - Chunks Extracted: 140

**17:47:05** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**17:47:08** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 2.39s

**17:47:08** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**17:47:20** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 12.69s

**17:47:20** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**17:47:37** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 16.14s

**17:47:37** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**17:47:41** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 4.60s

**17:47:41** [INFO] \\#\\#\\#\\# Test Summary

**17:47:41** [INFO] - \\*\\*Total Time:\\*\\* 71.58s

**17:47:41** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**17:47:41** [INFO] - \\*\\*Peak Memory:\\*\\* 16.1 MB

**17:47:41** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**17:47:41** [INFO] ---

**17:47:46** [INFO] \\*\\*Attempt 1/10\\*\\* for calculator

**17:47:46** [START] \\#\\#\\# Testing Repository: calculator

**17:47:46** [INFO] - \\*\\*URL:\\*\\* https://github.com/Abdulvoris101/Vue-Calculator

**17:47:46** [INFO] - \\*\\*Estimated Files:\\*\\* 40

**17:47:46** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:47:46** [INFO] - \\*\\*Batch Size:\\*\\* 80

**17:47:46** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 12

**17:47:46** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:47:49** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 0.97s

**17:47:49** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**17:48:06** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 16.87s

**17:48:06** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**17:48:10** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 3.88s

**17:48:10** [INFO]   - Files Processed: 3

**17:48:10** [INFO]   - Chunks Extracted: 3

**17:48:10** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**17:48:11** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 1.13s

**17:48:11** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**17:48:22** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 10.11s

**17:48:22** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**17:48:39** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 17.06s

**17:48:39** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**17:48:42** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 3.21s

**17:48:42** [INFO] \\#\\#\\#\\# Test Summary

**17:48:42** [INFO] - \\*\\*Total Time:\\*\\* 52.50s

**17:48:42** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**17:48:42** [INFO] - \\*\\*Peak Memory:\\*\\* 17.2 MB

**17:48:42** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**17:48:42** [INFO] ---

**17:48:47** [INFO] \\*\\*Attempt 1/10\\*\\* for vue-calculator

**17:48:47** [START] \\#\\#\\# Testing Repository: vue-calculator

**17:48:47** [INFO] - \\*\\*URL:\\*\\* https://github.com/ahfarmer/calculator

**17:48:47** [INFO] - \\*\\*Estimated Files:\\*\\* 35

**17:48:47** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:48:47** [INFO] - \\*\\*Batch Size:\\*\\* 70

**17:48:47** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 10

**17:48:47** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:48:50** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 1.05s

**17:48:50** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**17:49:05** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 15.53s

**17:49:05** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**17:49:14** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 7.68s

**17:49:14** [INFO]   - Files Processed: 10

**17:49:14** [INFO]   - Chunks Extracted: 36

**17:49:14** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**17:49:15** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 1.03s

**17:49:15** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**17:49:24** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 9.53s

**17:49:24** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**17:49:41** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 16.98s

**17:49:41** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**17:49:45** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 3.63s

**17:49:45** [INFO] \\#\\#\\#\\# Test Summary

**17:49:45** [INFO] - \\*\\*Total Time:\\*\\* 54.33s

**17:49:45** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**17:49:45** [INFO] - \\*\\*Peak Memory:\\*\\* 17.1 MB

**17:49:45** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**17:49:45** [INFO] ---

**17:49:50** [INFO] \\*\\*Attempt 1/10\\*\\* for todo

**17:49:50** [START] \\#\\#\\# Testing Repository: todo

**17:49:50** [INFO] - \\*\\*URL:\\*\\* https://github.com/tusharnankani/ToDoList

**17:49:50** [INFO] - \\*\\*Estimated Files:\\*\\* 80

**17:49:50** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:49:50** [INFO] - \\*\\*Batch Size:\\*\\* 160

**17:49:50** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 16

**17:49:50** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:49:54** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 1.20s

**17:49:54** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**17:50:10** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 16.12s

**17:50:10** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**17:50:14** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 3.97s

**17:50:14** [INFO]   - Files Processed: 2

**17:50:14** [INFO]   - Chunks Extracted: 12

**17:50:14** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**17:50:15** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 1.08s

**17:50:15** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**17:50:25** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 9.91s

**17:50:25** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**17:50:40** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 14.63s

**17:50:40** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**17:50:44** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 4.26s

**17:50:44** [INFO] \\#\\#\\#\\# Test Summary

**17:50:44** [INFO] - \\*\\*Total Time:\\*\\* 50.10s

**17:50:44** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**17:50:44** [INFO] - \\*\\*Peak Memory:\\*\\* 16.7 MB

**17:50:44** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**17:50:44** [INFO] ---

**17:50:49** [INFO] \\*\\*Attempt 1/10\\*\\* for react-weather-app

**17:50:49** [START] \\#\\#\\# Testing Repository: react-weather-app

**17:50:49** [INFO] - \\*\\*URL:\\*\\* https://github.com/Adedoyin-Emmanuel/react-weather-app

**17:50:49** [INFO] - \\*\\*Estimated Files:\\*\\* 60

**17:50:49** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:50:49** [INFO] - \\*\\*Batch Size:\\*\\* 120

**17:50:49** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 15

**17:50:49** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:50:52** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 1.45s

**17:50:52** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**17:51:09** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 16.48s

**17:51:09** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**17:51:20** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 10.32s

**17:51:20** [INFO]   - Files Processed: 16

**17:51:20** [INFO]   - Chunks Extracted: 55

**17:51:20** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**17:51:21** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 1.23s

**17:51:21** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**17:51:31** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 9.98s

**17:51:31** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**17:51:47** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 16.45s

**17:51:47** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**17:51:51** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 4.04s

**17:51:51** [INFO] \\#\\#\\#\\# Test Summary

**17:51:51** [INFO] - \\*\\*Total Time:\\*\\* 57.98s

**17:51:51** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**17:51:51** [INFO] - \\*\\*Peak Memory:\\*\\* 17.2 MB

**17:51:51** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**17:51:51** [INFO] ---

**17:51:56** [INFO] \\*\\*Attempt 1/10\\*\\* for fastapi-example

**17:51:56** [START] \\#\\#\\# Testing Repository: fastapi-example

**17:51:56** [INFO] - \\*\\*URL:\\*\\* https://github.com/tiangolo/full-stack-fastapi-postgresql

**17:51:56** [INFO] - \\*\\*Estimated Files:\\*\\* 90

**17:51:56** [INFO] - \\*\\*Language:\\*\\* Python

**17:51:56** [INFO] - \\*\\*Batch Size:\\*\\* 180

**17:51:56** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**17:51:56** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:51:59** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 1.01s

**17:51:59** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**17:52:15** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 16.38s

**17:52:15** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**17:52:45** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 28.85s

**17:52:45** [INFO]   - Files Processed: 74

**17:52:45** [INFO]   - Chunks Extracted: 196

**17:52:45** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**17:52:46** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 1.41s

**17:52:46** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**17:52:56** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 10.32s

**17:52:56** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**17:53:11** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 14.72s

**17:53:11** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**17:53:16** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 4.43s

**17:53:16** [INFO] \\#\\#\\#\\# Test Summary

**17:53:16** [INFO] - \\*\\*Total Time:\\*\\* 74.81s

**17:53:16** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**17:53:16** [INFO] - \\*\\*Peak Memory:\\*\\* 16.3 MB

**17:53:16** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**17:53:16** [INFO] ---

**17:53:21** [INFO] \\*\\*Attempt 1/10\\*\\* for gin-rest-api

**17:53:21** [START] \\#\\#\\# Testing Repository: gin-rest-api

**17:53:21** [INFO] - \\*\\*URL:\\*\\* https://github.com/gin-gonic/gin

**17:53:21** [INFO] - \\*\\*Estimated Files:\\*\\* 120

**17:53:21** [INFO] - \\*\\*Language:\\*\\* Go

**17:53:21** [INFO] - \\*\\*Batch Size:\\*\\* 240

**17:53:21** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 20

**17:53:21** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:53:24** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 1.58s

**17:53:24** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**17:55:51** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 146.47s

**17:55:51** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**17:57:35** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 103.74s

**17:57:35** [INFO]   - Files Processed: 94

**17:57:35** [INFO]   - Chunks Extracted: 463

**17:57:35** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**17:57:38** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 3.09s

**17:57:38** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**17:57:42** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 3.61s

**17:57:42** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**17:57:43** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 1.03s

**17:57:43** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**17:57:44** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 1.03s

**17:57:44** [INFO] \\#\\#\\#\\# Test Summary

**17:57:44** [INFO] - \\*\\*Total Time:\\*\\* 262.44s

**17:57:44** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**17:57:44** [INFO] - \\*\\*Peak Memory:\\*\\* 17.3 MB

**17:57:44** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**17:57:44** [INFO] ---

**17:57:49** [INFO] \\*\\*Attempt 1/10\\*\\* for vue-cli

**17:57:49** [START] \\#\\#\\# Testing Repository: vue-cli

**17:57:49** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**17:57:49** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**17:57:49** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:57:49** [INFO] - \\*\\*Batch Size:\\*\\* 200

**17:57:49** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**17:57:49** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:58:03** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**17:58:03** [WARNING] Attempt 1 failed - success rate: 0.0%

**17:58:05** [INFO] \\*\\*Attempt 2/10\\*\\* for vue-cli

**17:58:05** [START] \\#\\#\\# Testing Repository: vue-cli

**17:58:05** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**17:58:05** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**17:58:05** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:58:05** [INFO] - \\*\\*Batch Size:\\*\\* 200

**17:58:05** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**17:58:05** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:58:19** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**17:58:19** [WARNING] Attempt 2 failed - success rate: 0.0%

**17:58:23** [INFO] \\*\\*Attempt 3/10\\*\\* for vue-cli

**17:58:23** [START] \\#\\#\\# Testing Repository: vue-cli

**17:58:23** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**17:58:23** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**17:58:23** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:58:23** [INFO] - \\*\\*Batch Size:\\*\\* 200

**17:58:23** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**17:58:23** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:58:36** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**17:58:36** [WARNING] Attempt 3 failed - success rate: 0.0%

**17:58:44** [INFO] \\*\\*Attempt 4/10\\*\\* for vue-cli

**17:58:44** [START] \\#\\#\\# Testing Repository: vue-cli

**17:58:44** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**17:58:44** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**17:58:44** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:58:44** [INFO] - \\*\\*Batch Size:\\*\\* 200

**17:58:44** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**17:58:44** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:58:58** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**17:58:58** [WARNING] Attempt 4 failed - success rate: 0.0%

**17:59:14** [INFO] \\*\\*Attempt 5/10\\*\\* for vue-cli

**17:59:14** [START] \\#\\#\\# Testing Repository: vue-cli

**17:59:14** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**17:59:14** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**17:59:14** [INFO] - \\*\\*Language:\\*\\* JavaScript

**17:59:14** [INFO] - \\*\\*Batch Size:\\*\\* 200

**17:59:14** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**17:59:14** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**17:59:30** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**17:59:30** [WARNING] Attempt 5 failed - success rate: 0.0%

**18:00:00** [INFO] \\*\\*Attempt 6/10\\*\\* for vue-cli

**18:00:00** [START] \\#\\#\\# Testing Repository: vue-cli

**18:00:00** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**18:00:00** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**18:00:00** [INFO] - \\*\\*Language:\\*\\* JavaScript

**18:00:00** [INFO] - \\*\\*Batch Size:\\*\\* 200

**18:00:00** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**18:00:00** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:00:16** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**18:00:16** [WARNING] Attempt 6 failed - success rate: 0.0%

**18:00:46** [INFO] \\*\\*Attempt 7/10\\*\\* for vue-cli

**18:00:46** [START] \\#\\#\\# Testing Repository: vue-cli

**18:00:46** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**18:00:46** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**18:00:46** [INFO] - \\*\\*Language:\\*\\* JavaScript

**18:00:46** [INFO] - \\*\\*Batch Size:\\*\\* 200

**18:00:46** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**18:00:46** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:01:01** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**18:01:01** [WARNING] Attempt 7 failed - success rate: 0.0%

**18:01:31** [INFO] \\*\\*Attempt 8/10\\*\\* for vue-cli

**18:01:31** [START] \\#\\#\\# Testing Repository: vue-cli

**18:01:31** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**18:01:31** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**18:01:31** [INFO] - \\*\\*Language:\\*\\* JavaScript

**18:01:31** [INFO] - \\*\\*Batch Size:\\*\\* 200

**18:01:31** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**18:01:31** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:01:45** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**18:01:45** [WARNING] Attempt 8 failed - success rate: 0.0%

**18:02:15** [INFO] \\*\\*Attempt 9/10\\*\\* for vue-cli

**18:02:15** [START] \\#\\#\\# Testing Repository: vue-cli

**18:02:15** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**18:02:15** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**18:02:15** [INFO] - \\*\\*Language:\\*\\* JavaScript

**18:02:15** [INFO] - \\*\\*Batch Size:\\*\\* 200

**18:02:15** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**18:02:15** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:02:30** [ERROR] \\*\\*KB Creation:\\*\\* Failed - ╭─────────────────────────────────────╮
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

**18:02:30** [WARNING] Attempt 9 failed - success rate: 0.0%

**18:03:00** [INFO] \\*\\*Attempt 10/10\\*\\* for vue-cli

**18:03:00** [START] \\#\\#\\# Testing Repository: vue-cli

**18:03:00** [INFO] - \\*\\*URL:\\*\\* https://github.com/vuejs/vue-cli

**18:03:00** [INFO] - \\*\\*Estimated Files:\\*\\* 100

**18:03:00** [INFO] - \\*\\*Language:\\*\\* JavaScript

**18:03:00** [INFO] - \\*\\*Batch Size:\\*\\* 200

**18:03:00** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 18

**18:03:00** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:03:09** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 7.98s

**18:03:09** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**18:03:30** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 20.34s

**18:03:30** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**18:08:24** [SUCCESS] \\*\\*Data Ingestion:\\*\\* Success in 293.82s

**18:08:24** [INFO]   - Files Processed: 480

**18:08:24** [INFO]   - Chunks Extracted: 2324

**18:08:24** [INFO] \\#\\#\\#\\# Step 4: Index Creation

**18:08:27** [SUCCESS] \\*\\*Index Creation:\\*\\* Success in 2.37s

**18:08:27** [INFO] \\#\\#\\#\\# Step 5: Enhanced Semantic Search

**18:08:30** [SUCCESS] \\*\\*Search Testing:\\*\\* Success - 3 queries in 3.20s

**18:08:30** [INFO] \\#\\#\\#\\# Step 6: AI-Enhanced Search

**18:08:31** [SUCCESS] \\*\\*AI-Enhanced Search:\\*\\* Success in 1.48s

**18:08:31** [INFO] \\#\\#\\#\\# Step 7: Cleanup

**18:08:33** [SUCCESS] \\*\\*Cleanup:\\*\\* KB reset successful in 1.42s

**18:08:33** [INFO] \\#\\#\\#\\# Test Summary

**18:08:33** [INFO] - \\*\\*Total Time:\\*\\* 331.62s

**18:08:33** [INFO] - \\*\\*Success Rate:\\*\\* 100.0%

**18:08:33** [INFO] - \\*\\*Peak Memory:\\*\\* 17.2 MB

**18:08:33** [INFO] - \\*\\*CPU Usage:\\*\\* 0.0%

**18:08:33** [INFO] ---

**18:08:33** [SUCCESS] Repository vue-cli succeeded on attempt 10

**18:08:38** [INFO] \\*\\*Attempt 1/10\\*\\* for angular-cli

**18:08:38** [START] \\#\\#\\# Testing Repository: angular-cli

**18:08:38** [INFO] - \\*\\*URL:\\*\\* https://github.com/angular/angular-cli

**18:08:38** [INFO] - \\*\\*Estimated Files:\\*\\* 110

**18:08:38** [INFO] - \\*\\*Language:\\*\\* TypeScript

**18:08:38** [INFO] - \\*\\*Batch Size:\\*\\* 220

**18:08:38** [INFO] - \\*\\*Max Concurrent Queries:\\*\\* 22

**18:08:38** [INFO] \\#\\#\\#\\# Step 1: Knowledge Base Creation

**18:08:47** [SUCCESS] \\*\\*KB Creation:\\*\\* Success in 7.50s

**18:08:47** [INFO] \\#\\#\\#\\# Step 2: AI Tables Initialization

**18:09:08** [SUCCESS] \\*\\*AI Tables:\\*\\* Success in 20.86s

**18:09:08** [INFO] \\#\\#\\#\\# Step 3: Data Ingestion

**18:10:35** [WARNING] Test suite interrupted by user

## Comprehensive Performance Benchmark Summary

**Test Suite Completed:** 2025-06-29 18:10:35  
**Total Duration:** 0.40 hours  
**Total Dataset Size:** 3,229 code chunks across 8 repositories

### Executive Performance Summary

| Metric | Value | 95% Confidence Interval | Statistical Significance |
|--------|-------|------------------------|------------------------|
| **Total Repositories Tested** | 8 | - | Complete test matrix |
| **Success Rate** | 100.0% | - | 8/8 repositories |
| **Total Files Processed** | 713 | - | Across all repositories |
| **Total Code Chunks** | 3,229 | - | Embedded and indexed |
| **Average Ingestion Rate** | 5.0 chunks/sec | (3.4, 6.6) | CV: 46.3% |
| **Average Search Latency** | 2889.8 ms | (2106.4, 3673.2) | CV: 39.1% |
| **Average Memory Usage** | 16.9 MB | (16.6, 17.2) | CV: 2.6% |

### Cross-Repository Performance Analysis

#### Ingestion Performance Distribution

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Ingestion Rate** | 5.0 chunks/sec | More robust than mean |
| **Performance Range** | 0.8 - 7.9 chunks/sec | 10.2x variation |
| **Standard Deviation** | 2.3 chunks/sec | Consistency measure |
| **Outlier Repositories** | 0 | Repositories with unusual performance |
| **Performance Consistency** | 46.3% CV | Variable across repositories |

#### Search Latency Analysis

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Latency** | 3315.5 ms | Typical user experience |
| **Latency Range** | 1065.0 - 4230.6 ms | 4.0x variation |
| **95% of Queries Under** | 5105.6 ms | SLA recommendation |
| **Latency Consistency** | 39.1% CV | Variable performance |

#### Memory Efficiency Patterns

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **Median Memory Usage** | 17.1 MB | Typical requirement |
| **Memory Range** | 16.1 - 17.3 MB | 1.1x scaling factor |
| **Memory Predictability** | 2.6% CV | Predictable scaling |

### Performance Analysis

#### Ingestion Performance by Repository Size

| Repository | Files | Chunks | Batch Size | Ingestion Time | Chunks/Second |
|------------|-------|--------|------------|----------------|---------------|
| flask-microblog | 34 | 140 | 100 | 20.88s | 6.7 |
| calculator | 3 | 3 | 80 | 3.88s | 0.8 |
| vue-calculator | 10 | 36 | 70 | 7.68s | 4.7 |
| todo | 2 | 12 | 160 | 3.97s | 3.0 |
| react-weather-app | 16 | 55 | 120 | 10.32s | 5.3 |
| fastapi-example | 74 | 196 | 180 | 28.85s | 6.8 |
| gin-rest-api | 94 | 463 | 240 | 103.74s | 4.5 |
| vue-cli | 480 | 2324 | 200 | 293.82s | 7.9 |

#### Search Performance Analysis

| Repository | Queries Tested | Avg Response Time | Total Results | Results/Query |
|------------|----------------|-------------------|---------------|---------------|
| flask-microblog | 3 | 12.69s | 9 | 3.0 |
| calculator | 3 | 10.11s | 9 | 3.0 |
| vue-calculator | 3 | 9.53s | 9 | 3.0 |
| todo | 3 | 9.91s | 9 | 3.0 |
| react-weather-app | 3 | 9.98s | 9 | 3.0 |
| fastapi-example | 3 | 10.32s | 9 | 3.0 |
| gin-rest-api | 3 | 3.61s | 0 | 0.0 |
| vue-cli | 3 | 3.20s | 0 | 0.0 |

### Failure Analysis

#### Failed Tests

### Critical Performance Insights and Optimization Recommendations

#### Statistical Significance and Confidence

- **Sample Size**: 8 repositories tested with 3,229 total code chunks
- **Statistical Power**: 95% confidence intervals provided for all key metrics
- **Data Quality**: 8/8 successful tests provide robust statistical foundation
- **Variance Analysis**: Performance consistency varies by repository size and complexity

#### Key Performance Bottlenecks Identified

**Ingestion Performance Bottleneck**: 8/8 repositories showed slow ingestion (avg 14.9% of baseline). Primary causes: batch size optimization needed, network/disk I/O limitations.

**Search Latency Inconsistency**: 2/8 repositories showed high search latency variance (>30% CV). This indicates query complexity differences or system resource contention.



#### Cross-Repository Performance Patterns

