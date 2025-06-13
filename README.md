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
   docker run -p 47334:47334 mindsdb/mindsdb
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

```bash
# Basic ingestion
python main.py kb:ingest https://github.com/org/repo-name.git

# With options
python main.py kb:ingest https://github.com/org/repo.git --branch develop --extensions "py,js" --extract-git-info

# Dry run
python main.py kb:ingest https://github.com/org/repo.git --dry-run
```

Ingestion Options:
- `--branch, -b`: Git branch to clone (default: main)
- `--extensions`: File extensions to ingest
- `--exclude-dirs`: Directories to exclude
- `--extract-git-info`: Extract git author and commit information
- `--batch-size`: Batch size for insertion
- `--dry-run`: Preview without inserting data

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

## Acknowledgments

- [MindsDB](https://mindsdb.com/) for the Knowledge Base platform
- [MindsDB Python SDK](https://mindsdb.com/blog/introduction-to-python-sdk-interact-with-mindsdb-directly-from-python) for integration
- OpenAI for embedding and reranking models

---

