# Semantic Code Navigator

A CLI tool for stress testing MindsDB's Knowledge Base feature through semantic codebase navigation. Ingests codebases and enables natural language search using MindsDB's embedding and reranking capabilities.

## Overview

The Semantic Code Navigator is a CLI application that transforms codebase navigation through semantic search. It clones GitHub repositories, extracts functions and classes from multiple programming languages, and ingests them into MindsDB Knowledge Bases with rich metadata. Users can perform natural language queries with advanced filtering capabilities.

The application demonstrates MindsDB Knowledge Base capabilities including CREATE KNOWLEDGE_BASE with OpenAI embedding models, batch INSERT operations, complex SELECT queries with metadata filtering, and CREATE INDEX for performance optimization.

## Features

### Core Functionality
- Semantic code search with natural language queries
- Metadata filtering by language, file path, function name, repository
- Batch processing for large codebases
- Multiple output formats (table, JSON, compact)
- Progress tracking with rich CLI interface

### AI-Enhanced Analysis
- Code purpose classification
- Natural language explanations
- Automated docstring generation
- Test case suggestions
- Search result rationale

### Stress Testing Capabilities
- Concurrent query testing
- Performance benchmarking
- Scalability analysis
- Error rate monitoring

## Prerequisites

1. **MindsDB**: Install and run MindsDB locally or use MindsDB Cloud
   ```bash
   # Local installation
   pip install mindsdb
   
   # Docker
   docker-compose up
   ```

2. **OpenAI API Key**: Required for embeddings and reranking
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Deeptanshu-sankhwar/semantic-code-navigator.git
   cd semantic-code-navigator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. Set environment variables:
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

### Initialize Knowledge Base

```bash
python main.py kb:init --validate-config
```

Options:
- `--force`: Recreate knowledge base if exists
- `--validate-config`: Validate configuration before creation

### Semantic Search

```bash
# Basic search
python main.py kb:query "authentication middleware"

# With filters
python main.py kb:query "database connection" --language python --limit 20

# With AI analysis
python main.py kb:query "error handling" --ai-all

# Different output formats
python main.py kb:query "JWT validation" --output-format json
```

Search Options:
- `--language, -l`: Filter by programming language
- `--filepath, -f`: Filter by file path pattern
- `--function`: Filter by function name
- `--repo, -r`: Filter by repository name
- `--limit`: Maximum number of results (default: 10)
- `--relevance-threshold`: Minimum relevance score (0.0-1.0)
- `--output-format`: Output format (table, json, compact)
- `--ai-purpose`: Add AI purpose classification
- `--ai-explain`: Add AI code explanations
- `--ai-docstring`: Add AI-generated docstrings
- `--ai-tests`: Add AI test case suggestions
- `--ai-all`: Add all AI analysis

### Repository Ingestion

The `kb:ingest` command clones Git repositories, parses code files to extract functions and classes, and inserts the resulting code chunks into the knowledge base with comprehensive metadata.

```bash
# Basic ingestion
python main.py kb:ingest https://github.com/org/repo-name.git

# Advanced ingestion with full options
python main.py kb:ingest https://github.com/org/repo.git \
  --branch develop \
  --extensions "py,js,ts,java,go" \
  --exclude-dirs "node_modules,__pycache__,build" \
  --batch-size 500 \
  --extract-git-info \
  --generate-summaries

# Preview ingestion without inserting data
python main.py kb:ingest https://github.com/org/repo.git --dry-run
```

#### Ingestion Process

1. **Repository Cloning**: Clones the specified Git repository and branch
2. **File Discovery**: Scans for files matching specified extensions
3. **Code Parsing**: Extracts functions, classes, and methods using AST parsing
4. **Metadata Extraction**: Collects file paths, languages, function names, and Git information
5. **Batch Processing**: Inserts code chunks in configurable batch sizes for optimal performance
6. **Progress Reporting**: Provides real-time feedback on ingestion progress

#### Ingestion Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--branch, -b` | Git branch to clone | `main` | `--branch develop` |
| `--extensions` | Comma-separated file extensions | `py,js,ts,java,go,rs,cpp,c,h` | `--extensions "py,js"` |
| `--exclude-dirs` | Directories to skip during ingestion | `.git,node_modules,__pycache__,.venv,build,dist` | `--exclude-dirs "tests,docs"` |
| `--batch-size` | Number of records per batch insert | `500` | `--batch-size 1000` |
| `--extract-git-info` | Include Git author and commit data | `false` | `--extract-git-info` |
| `--generate-summaries` | Generate AI summaries (costs OpenAI credits) | `false` | `--generate-summaries` |
| `--dry-run` | Preview without inserting data | `false` | `--dry-run` |
| `--cleanup` | Remove temporary files after ingestion | `true` | `--no-cleanup` |

#### Supported Languages

The ingestion engine supports AST-based parsing for:
- **Python** (.py) - Functions, classes, methods
- **JavaScript/TypeScript** (.js, .ts) - Functions, classes, arrow functions
- **Java** (.java) - Methods, classes, interfaces
- **Go** (.go) - Functions, methods, structs
- **Rust** (.rs) - Functions, implementations, traits
- **C/C++** (.c, .cpp, .h) - Functions, classes, structs

For unsupported languages, the system falls back to chunk-based extraction.

#### Extracted Metadata

Each ingested code chunk includes:

| Field | Description | Source |
|-------|-------------|--------|
| `content` | The actual function/class code | AST parsing |
| `filepath` | Relative path within repository | File system |
| `language` | Programming language | File extension |
| `function_name` | Name of function/class/method | AST parsing |
| `repo` | GitHub repository URL | Git remote |
| `last_modified` | Last commit timestamp | Git log |
| `author` | Code author (if `--extract-git-info`) | Git blame |
| `line_range` | Start-end line numbers (if `--extract-git-info`) | AST + file position |
| `summary` | AI-generated summary (if `--generate-summaries`) | OpenAI API |

#### Performance Considerations

- **Batch Size**: Larger batches (500-1000) improve throughput but use more memory
- **Git Info Extraction**: Adds processing time but provides richer metadata
- **AI Summaries**: Significantly increases processing time and OpenAI costs
- **Repository Size**: Large repositories (1000+ files) may require 10-30 minutes
- **Network**: Repository cloning speed depends on internet connection

#### Example Output

```
Starting repository ingestion: https://github.com/psf/requests.git
This may take a few minutes depending on repository size...

Extracted 1,247 code chunks from repository
Starting batch insertion into knowledge base...
Using batch size: 500 for stable insertion
Total records to insert: 1,247

Inserted batch 1/3: 500 records
Inserted batch 2/3: 500 records  
Inserted batch 3/3: 247 records

Successfully ingested 1,247 code chunks

Language breakdown:
  python: 1,198 chunks
  markdown: 31 chunks
  yaml: 12 chunks
  shell: 6 chunks
```

### AI Tables Management

```bash
# Initialize AI tables
python main.py ai:init

# Analyze code
python main.py ai:analyze "def authenticate_user(username, password): return username == 'admin'" --all

# List AI tables
python main.py ai:list

# Reset AI tables
python main.py ai:reset
```

AI Analysis Types:
- `--classify`: Code purpose classification
- `--explain`: Natural language explanation
- `--docstring`: Generate documentation
- `--tests`: Suggest test cases
- `--all`: Run all analysis types

### Repository Sync Jobs

```bash
# Create sync job
python main.py kb:sync https://github.com/org/repo-name.git

# Custom schedule
python main.py kb:sync https://github.com/org/repo.git --schedule "EVERY 12 HOURS"

# List jobs
python main.py kb:sync:list

# Delete job
python main.py kb:sync:delete sync_github_com_org_repo_git
```

### Workflow Demo

Experience the complete AI-enhanced semantic search workflow:

```bash
# Complete workflow demonstration
python demo.py workflow "decorator function" --limit 3

# Create SQL view joining KB with AI tables
python demo.py create-view

# Query integrated workflow view
python demo.py query-view --limit 5
```

Demo Features:
- Complete pipeline demonstration (KB search to AI analysis)
- Step-by-step workflow output
- SQL view integration
- Professional presentation format

### Utility Commands

```bash
# Check status
python main.py kb:status

# View schema
python main.py kb:schema

# Create index
python main.py kb:index

# Reset knowledge base
python main.py kb:reset --force
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Semantic Code Navigator                  │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface (Click + Rich)                              │
│  ├── kb:*        - Knowledge Base Operations               │
│  ├── ai:*        - AI Table Management                     │
│  └── demo:*      - Workflow Demonstrations                 │
├─────────────────────────────────────────────────────────────┤
│  MindsDB Client (Python SDK)                               │
│  ├── Connection Management                                 │
│  ├── Knowledge Base Operations                             │
│  ├── AI Table Integration                                  │
│  └── Batch Processing                                      │
├─────────────────────────────────────────────────────────────┤
│  MindsDB Knowledge Base                                     │
│  ├── OpenAI Embeddings (text-embedding-3-large)           │
│  ├── OpenAI Reranking (gpt-4o)                            │
│  ├── Vector Storage & Indexing                             │
│  └── Metadata Filtering                                    │
├─────────────────────────────────────────────────────────────┤
│  AI Tables (Generative AI Models)                          │
│  ├── code_classifier - Purpose Classification              │
│  ├── code_explainer - Natural Language Explanations       │
│  ├── docstring_generator - Documentation Generation        │
│  ├── test_case_outliner - Test Case Suggestions           │
│  └── result_rationale - Search Match Explanations         │
├─────────────────────────────────────────────────────────────┤
│  Git Repository Ingestion Pipeline                         │
│  ├── Repository Cloning & Discovery                        │
│  ├── Function/Class Extraction                             │
│  ├── Metadata Extraction                                   │
│  └── Batch Processing                                      │
└─────────────────────────────────────────────────────────────┘
```

## Knowledge Base Schema

### Storage Structure
- `chunk_content`: Code content with embedded metadata
- `chunk_id`: Unique identifier
- `metadata`: MindsDB internal metadata
- `relevance`: Semantic search relevance score
- `distance`: Vector similarity distance

### Extracted Metadata
- `filepath`: Relative path within repository
- `language`: Programming language
- `function_name`: Function/class/method name
- `repo`: GitHub repository URL
- `last_modified`: Git commit timestamp
- `author`: Git commit author (optional)
- `line_range`: Start-end line numbers (optional)

### Supported Languages
- Python, JavaScript, TypeScript, Java, Go, Rust, C/C++
- Fallback chunking for unsupported languages

## Example Queries

```bash
# Authentication code
python main.py kb:query "user authentication and login validation"

# HTTP handling
python main.py kb:query "http request" --language python --limit 5

# Error patterns
python main.py kb:query "exception handling" --relevance-threshold 0.7

# Test files
python main.py kb:query "test validation" --filepath "*/test*"

# Specific functions
python main.py kb:query "database connection" --function "*connect*"

# Recent changes
python main.py kb:query "authentication" --author "john@example.com" --since "2024-01-01"
```

## Quick Start

```bash
# 1. Initialize
python main.py kb:init

# 2. Ingest repository
python main.py kb:ingest https://github.com/psf/requests.git --extract-git-info

# 3. Search
python main.py kb:query "http request handling" --limit 5

# 4. Check status
python main.py kb:status

# 5. Reset for new testing
python main.py kb:reset --force
```

## Contributing

This project is part of MindsDB Knowledge Base stress testing. Contributions welcome.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Stress Testing

The project includes a comprehensive stress testing suite that evaluates the complete workflow across 25 GitHub repositories of varying sizes (50 to 3000+ files).

### Stress Test Features

- **Complete Workflow Testing**: Tests KB creation, data ingestion, indexing, semantic search, and AI analysis
- **25 Repository Coverage**: From small Flask apps to large projects like Linux kernel and WebKit
- **Serial Execution**: Tests run one after another to prevent memory issues
- **Memory Management**: Automatic KB reset after each test to free memory
- **Real-time Reporting**: Beautiful markdown reports with timestamps and metrics
- **Performance Analysis**: Tracks ingestion speed, search response times, and success rates
- **Failure Analysis**: Detailed error reporting and recommendations

### Repository Test Matrix

| Size Category | File Count | Examples | Batch Size |
|---------------|------------|----------|------------|
| Small | 50-150 | Flask, Express, Gin examples | 100-300 |
| Medium | 200-450 | Django, React, Spring Boot | 200-400 |
| Medium-Large | 500-700 | Angular, NestJS, FastAPI | 300-500 |
| Large | 800-1000 | Kubernetes, TensorFlow.js | 400-600 |
| Very Large | 1200-3000+ | VS Code, Chromium, Linux | 500-1000 |

### Running Stress Tests

```bash
# Full stress test (25 repositories, ~4-6 hours)
python stress_test.py

# View help
python stress_test.py --help
```

### Test Workflow

Each repository test follows this workflow:

1. **KB Creation** - Initialize fresh knowledge base
2. **AI Tables Setup** - Create AI analysis models
3. **Data Ingestion** - Clone repo and extract code chunks
4. **Index Creation** - Optimize for search performance
5. **Semantic Search** - Test 5 different queries
6. **AI Analysis** - Test code classification and explanation
7. **Cleanup** - Reset KB to free memory for next test

### Output Reports

The stress test generates detailed markdown reports including:

- **Real-time Progress**: Timestamped updates during execution
- **Performance Metrics**: Ingestion speed, search response times
- **Success Rates**: Pass/fail statistics for each workflow step
- **Memory Usage**: Peak memory consumption tracking
- **Failure Analysis**: Detailed error logs and recommendations
- **Comparative Analysis**: Performance across different repository sizes

### Example Report Sections

```markdown
### Testing Repository: django-blog
- **URL:** https://github.com/django/django
- **Estimated Files:** 250
- **Language:** Python
- **Batch Size:** 200

#### Step 1: Knowledge Base Creation
**KB Creation:** Success in 2.34s

#### Step 3: Data Ingestion
**Data Ingestion:** Success in 45.67s
  - Files Processed: 247
  - Chunks Extracted: 1,234

#### Step 5: Semantic Search Testing
**Semantic Search:** Success
  - Queries Tested: 5
  - Average Response Time: 1.23s
  - Total Results: 47
```

### Prerequisites for Stress Testing

- MindsDB running locally (`docker-compose up`)
- OpenAI API key configured in `.env`
- Sufficient disk space (~5GB for temporary repositories)
- Stable internet connection for repository cloning
- 8GB+ RAM recommended for large repositories

### Cost Considerations

- **Embedding Costs**: ~$0.10-0.50 per repository (varies by size)
- **AI Analysis Costs**: ~$0.05-0.20 per repository
- **Total Estimated Cost**: $5-15 for full 25-repository test
- **No Summary Generation**: Disabled to reduce OpenAI costs

The stress test is designed to thoroughly validate the system's reliability, performance, and scalability across diverse codebases while providing actionable insights for optimization.

## Acknowledgments

- [MindsDB](https://mindsdb.com/) for the Knowledge Base platform
- [MindsDB Python SDK](https://mindsdb.com/blog/introduction-to-python-sdk-interact-with-mindsdb-directly-from-python) for integration
- OpenAI for embedding and reranking models

---

