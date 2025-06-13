# Semantic Code Navigator

A powerful CLI tool for stress testing MindsDB's Knowledge Base feature through semantic codebase navigation. This tool ingests codebases and enables natural language search across your code using MindsDB's advanced embedding and reranking capabilities.

## Project Overview

The Semantic Code Navigator is a comprehensive CLI application that transforms codebase navigation through intelligent semantic search. It clones GitHub repositories, extracts functions and classes from multiple programming languages (Python, JavaScript, Java, Go, Rust, C/C++), and ingests them into MindsDB Knowledge Bases with rich metadata including git history, file paths, and code structure. Users can then perform natural language queries like "authentication middleware" or "database connection handling" with advanced filtering by language, file path, author, and relevance thresholds.

The application demonstrates full MindsDB Knowledge Base capabilities including `CREATE KNOWLEDGE_BASE` with custom OpenAI embedding models, batch `INSERT INTO` operations for large-scale ingestion, complex `SELECT ... WHERE` semantic queries with metadata filtering, and `CREATE INDEX` for performance optimization. Built with the official MindsDB Python SDK, it includes robust error handling, connection recovery, batch processing, and stress testing capabilities for production-scale deployments with 10K+ code chunks.

## Features

### Core Functionality
- **Semantic Code Search**: Natural language queries across your codebase
- **Metadata Filtering**: Filter by language, file path, function name, repository
- **Batch Processing**: Efficient ingestion of large codebases
- **Multiple Output Formats**: Table, JSON, and compact views
- **Progress Tracking**: Rich CLI with progress bars and status updates

### Stress Testing Capabilities
- **Concurrent Query Testing**: Simulate high-load scenarios
- **Performance Benchmarking**: Measure query latency and throughput
- **Scalability Analysis**: Test with large codebases (10K+ functions)
- **Error Rate Monitoring**: Track failures under stress

## Prerequisites

1. **MindsDB**: Install and run MindsDB locally or use MindsDB Cloud
   ```bash
   # Option 1: Local installation via pip
   pip install mindsdb
   
   # Option 2: Docker
   docker run -p 47334:47334 mindsdb/mindsdb
   
   # Option 3: Use MindsDB Cloud (requires account)
   ```

2. **OpenAI API Key**: Required for embeddings and reranking
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Deeptanshu-sankhwar/semantic-code-navigator.git
   cd semantic-code-navigator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Set up your environment variables**:
   ```bash
   # Required
   OPENAI_API_KEY=sk-your-openai-api-key-here
   
   # Optional (for local MindsDB)
   MINDSDB_HOST=127.0.0.1
   MINDSDB_PORT=47334
   
   # Optional (for MindsDB Cloud)
   MINDSDB_USER=your-email@example.com
   MINDSDB_PASSWORD=your-password
   ```

## Usage

### 1. Initialize Knowledge Base

Create and configure your knowledge base:

```bash
python main.py kb:init --validate-config
```

**Options:**
- `--force`: Recreate knowledge base if it exists
- `--validate-config`: Validate configuration before creation

### 2. Check Status

View knowledge base status and statistics:

```bash
python main.py kb:status
```

### 3. Perform Semantic Search

Search your codebase using natural language:

```bash
# Basic search
python main.py kb:query "authentication middleware"

# With filters
python main.py kb:query "database connection" --language python --limit 20

# With relevance threshold
python main.py kb:query "error handling" --relevance-threshold 0.7

# Different output formats
python main.py kb:query "JWT validation" --output-format json
python main.py kb:query "logging setup" --output-format compact
```

**Search Options:**
- `--language, -l`: Filter by programming language
- `--filepath, -f`: Filter by file path pattern
- `--function`: Filter by function name
- `--repo, -r`: Filter by repository name
- `--limit`: Maximum number of results (default: 10)
- `--relevance-threshold`: Minimum relevance score (0.0-1.0)
- `--output-format`: Output format (table, json, compact)

### 4. Create Index

Optimize search performance:

```bash
python main.py kb:index --show-stats
```

### 5. Ingest Git Repository

Clone and ingest entire GitHub repositories:

```bash
# Basic repository ingestion
python main.py kb:ingest https://github.com/org/repo-name.git

# With specific branch and file types
python main.py kb:ingest https://github.com/org/repo.git --branch develop --extensions "py,js"

# With git metadata extraction
python main.py kb:ingest https://github.com/org/repo.git --extract-git-info

# Dry run to see what would be ingested
python main.py kb:ingest https://github.com/org/repo.git --dry-run
```

**Ingestion Options:**
- `--branch, -b`: Git branch to clone (default: main)
- `--extensions`: File extensions to ingest (default: py,js,ts,java,go,rs,cpp,c,h)
- `--exclude-dirs`: Directories to exclude (default: .git,node_modules,__pycache__,.venv,venv,build,dist)
- `--extract-git-info`: Extract git author and commit information
- `--batch-size`: Batch size for insertion (default: 500)
- `--dry-run`: Preview ingestion without actually inserting data
- `--cleanup`: Clean up temporary files (default: true)

### 6. Reset Knowledge Base

Start fresh by clearing all data:

```bash
# Interactive reset (asks for confirmation)
python main.py kb:reset

# Force reset (skips confirmation)
python main.py kb:reset --force
```

### 7. View Schema

Inspect the knowledge base structure:

```bash
python main.py kb:schema
```

### 8. Manage Repository Sync Jobs

Create scheduled jobs to automatically sync repository changes:Build a multi-step workflow within MindsDB by taking the results from a KB semantic query and feeding them as input into another 🔗 MindsDB AI Table (e.g., for summarisation, classification, generation).

```bash
# Create a sync job for a repository
python main.py kb:sync https://github.com/org/repo-name.git

# Create a sync job with custom schedule
python main.py kb:sync https://github.com/org/repo.git --schedule "EVERY 12 HOURS"

# Force recreate an existing job
python main.py kb:sync https://github.com/org/repo.git --force

# List all sync jobs
python main.py kb:sync:list

# Delete a sync job
python main.py kb:sync:delete sync_github_com_org_repo_git
```

**Sync Job Options:**
- `--branch, -b`: Git branch to sync (default: main)
- `--schedule, -s`: Job schedule (default: EVERY 6 HOURS)
- `--force`: Force recreate sync job if exists

**How Sync Jobs Work:**
1. Track the last sync timestamp
2. Ingest new changes since last sync
3. Run automatically every 6 hours
4. Update knowledge base with new code


### 9. AI-Powered Code Analysis

Use AI tables to analyze and understand code with natural language:

```bash
# Initialize AI tables (one-time setup)
python main.py ai:init

# Analyze code with all AI capabilities
python main.py ai:analyze "def authenticate_user(username, password): return username == 'admin'" --all

# Classify code purpose only
python main.py ai:analyze "def calculate_tax(amount): return amount * 0.1" --classify

# Get code explanation
python main.py ai:analyze "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)" --explain

# Generate docstring
python main.py ai:analyze "def process_data(data): return [x*2 for x in data]" --docstring

# Suggest test cases
python main.py ai:analyze "def validate_email(email): return '@' in email" --tests

# Check AI tables status
python main.py ai:list

# Reset all AI tables
python main.py ai:reset
```

**AI Analysis Capabilities:**
- **Code Classification**: Categorizes functions (auth, utility, api handler, etc.)
- **Natural Language Explanation**: Explains code in simple English
- **Docstring Generation**: Creates documentation for undocumented functions
- **Test Case Suggestions**: Recommends test scenarios for functions
- **Search Result Rationale**: Explains why code matches search queries

**AI Tables Created:**
- `code_classifier` - Classifies code purpose
- `code_explainer` - Explains functions in simple English  
- `docstring_generator` - Generates docstrings
- `test_case_outliner` - Suggests test cases
- `result_rationale` - Explains search matches

### 10. AI Workflow Demo

Experience the complete AI-enhanced semantic search workflow with dedicated demo commands:

```bash
# Run complete AI workflow demonstration
python demo.py workflow "decorator function" --limit 3

# Create SQL view that joins KB with AI tables
python demo.py create-view

# Query the integrated workflow view
python demo.py query-view --limit 5
```

**Workflow Demo Features:**
- **Complete Pipeline**: Demonstrates KB search → AI analysis → unified results
- **Step-by-Step Output**: Shows each stage of the multi-step workflow
- **SQL View Integration**: Creates reusable views joining KB with AI tables
- **Professional Presentation**: Clean output suitable for demonstrations

**Demo Commands:**
- `workflow` - Complete AI workflow with semantic search + AI analysis
- `create-view` - Create SQL view demonstrating KB + AI table integration
- `query-view` - Query the integrated workflow view for combined results

The demo module showcases the full power of MindsDB's multi-step workflows, taking semantic search results and enriching them with AI table analysis in a single, streamlined process.


## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Semantic Code Navigator                  │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface (Click + Rich)                              │
│  ├── kb:init     - Initialize Knowledge Base               │
│  ├── kb:ingest   - Clone & Ingest Git Repository           │
│  ├── kb:query    - Semantic Search with Filters           │
│  ├── kb:index    - Create Performance Index                │
│  ├── kb:status   - Show Statistics & Record Count          │
│  ├── kb:schema   - View Knowledge Base Structure           │
│  ├── kb:reset    - Clear All Data & Start Fresh           │
│  ├── kb:sync     - Create Repository Sync Jobs             │
│  ├── kb:sync:*   - Manage Sync Jobs (list, delete)        │
│  ├── ai:init     - Initialize AI Tables                    │
│  ├── ai:analyze  - Analyze Code with AI                    │
│  ├── ai:list     - List AI Tables Status                   │
│  └── ai:reset    - Reset AI Tables                         │
├─────────────────────────────────────────────────────────────┤
│  MindsDB Client (Python SDK)                               │
│  ├── Connection Management                                 │
│  ├── Knowledge Base Operations                             │
│  ├── Batch Data Processing                                 │
│  └── Query Execution                                       │
├─────────────────────────────────────────────────────────────┤
│  MindsDB Knowledge Base                                     │
│  ├── OpenAI Embeddings (text-embedding-3-large)           │
│  ├── OpenAI Reranking (gpt-4o)                            │
│  ├── Vector Storage & Indexing                             │
│  └── Metadata Filtering                                    │
├─────────────────────────────────────────────────────────────┤
│  AI Tables (Generative AI Models)                          │
│  ├── code_classifier - Code Purpose Classification         │
│  ├── code_explainer - Natural Language Explanations       │
│  ├── docstring_generator - Documentation Generation        │
│  ├── test_case_outliner - Test Case Suggestions           │
│  └── result_rationale - Search Match Explanations         │
├─────────────────────────────────────────────────────────────┤
│  Git Repository Ingestion Pipeline                         │
│  ├── Git Cloning & Repository Discovery                    │
│  ├── Regex-based Function/Class Extraction                 │
│  ├── Git Metadata Extraction (Author, Timestamps)         │
│  ├── Content Enrichment with Embedded Metadata            │
│  └── Batch Processing & Cleanup                            │
└─────────────────────────────────────────────────────────────┘
```

## Knowledge Base Schema

The knowledge base stores code chunks with rich metadata embedded in the content:

### MindsDB Columns (Actual Storage)
- `chunk_content`: Enriched code content with embedded metadata headers
- `chunk_id`: Unique identifier for each code chunk
- `metadata`: MindsDB internal chunking metadata
- `relevance`: Semantic search relevance score
- `distance`: Vector distance for similarity

### Extracted Metadata (From Content Headers)
- `filepath`: Relative path within the repository
- `language`: Programming language (python, javascript, java, go, rust, etc.)
- `function_name`: Name of the function/class/method
- `repo`: GitHub repository URL
- `last_modified`: Git commit timestamp
- `author`: Git commit author (when --extract-git-info used)
- `line_range`: Start-end line numbers (when --extract-git-info used)

### Supported Languages
- **Python**: Functions and classes via regex parsing
- **JavaScript/TypeScript**: Functions, arrow functions, classes, methods
- **Java, Go, Rust, C/C++**: Basic function extraction (extensible)
- **Fallback**: Fixed-size chunking for unsupported languages

## Example Queries

```bash
# Find authentication-related code
python main.py kb:query "user authentication and login validation"

# Search for HTTP request handling
python main.py kb:query "http request" --language python --limit 5

# Find error handling patterns with high relevance
python main.py kb:query "exception handling" --relevance-threshold 0.7

# Look for specific functionality in test files
python main.py kb:query "test validation" --filepath "*/test*" --limit 10

# Search for specific functions or classes
python main.py kb:query "database connection" --function "*connect*"

# Find recent changes by author
python main.py kb:query "authentication" --author "john@example.com" --since "2024-01-01"
```

## Quick Start Workflow

```bash
# 1. Initialize knowledge base
python main.py kb:init

# 2. Ingest a popular repository
python main.py kb:ingest https://github.com/psf/requests.git --extract-git-info

# 3. Search the codebase
python main.py kb:query "http request handling" --limit 5

# 4. Check status and schema
python main.py kb:status
python main.py kb:schema

# 5. Reset when ready to test another repo
python main.py kb:reset --force
```

## Stress Testing (Coming Soon)

The tool will include comprehensive stress testing capabilities:

- **Query Load Testing**: Simulate 100+ concurrent semantic queries
- **Ingestion Performance**: Test with 50K+ code chunks
- **Latency Benchmarking**: Measure P95/P99 response times
- **Error Rate Analysis**: Monitor failures under high load
- **Reranking Evaluation**: Compare relevance scores across models

## Contributing

This project is part of the MindsDB Knowledge Base stress testing. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MindsDB](https://mindsdb.com/) for the powerful Knowledge Base platform
- [MindsDB Python SDK](https://mindsdb.com/blog/introduction-to-python-sdk-interact-with-mindsdb-directly-from-python) for seamless integration
- OpenAI for embedding and reranking models

---

