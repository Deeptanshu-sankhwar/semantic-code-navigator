# CLI Commands Reference

Quick reference guide for all Semantic Code Navigator CLI commands.

## Knowledge Base Commands

### Initialize Knowledge Base
```bash
python -m src.cli kb:init [OPTIONS]
```
**Options:**
- `--force` - Force recreate knowledge base if exists
- `--validate-config` - Validate configuration before creating KB

**Examples:**
```bash
python -m src.cli kb:init
python -m src.cli kb:init --force --validate-config
```

### Ingest Repository
```bash
python -m src.cli kb:ingest REPO_URL [OPTIONS]
```
**Options:**
- `--branch, -b TEXT` - Git branch to clone (default: main)
- `--extensions TEXT` - File extensions to ingest (default: py,js,ts,java,go,rs,cpp,c,h)
- `--exclude-dirs TEXT` - Directories to exclude (default: .git,node_modules,__pycache__,.venv,venv,build,dist)
- `--batch-size INTEGER` - Batch size for insertion
- `--extract-git-info` - Extract git author and commit info
- `--generate-summaries` - Generate AI summaries for functions
- `--dry-run` - Show what would be ingested without doing it
- `--cleanup / --no-cleanup` - Clean up temporary files after ingestion (default: true)

**Examples:**
```bash
python -m src.cli kb:ingest https://github.com/psf/requests.git
python -m src.cli kb:ingest https://github.com/django/django.git --branch main --batch-size 500
python -m src.cli kb:ingest https://github.com/fastapi/fastapi.git --extract-git-info --generate-summaries
python -m src.cli kb:ingest https://github.com/gin-gonic/gin.git --extensions "go,mod" --exclude-dirs "vendor,test"
python -m src.cli kb:ingest https://github.com/vuejs/vue.git --dry-run
```

### Query Knowledge Base
```bash
python -m src.cli kb:query "SEARCH_QUERY" [OPTIONS]
```
**Options:**
- `--language, -l TEXT` - Filter by programming language
- `--filepath, -f TEXT` - Filter by file path pattern
- `--function TEXT` - Filter by function name
- `--repo, -r TEXT` - Filter by repository name
- `--author, -a TEXT` - Filter by code author
- `--since TEXT` - Filter by last modified date (YYYY-MM-DD)
- `--limit INTEGER` - Maximum number of results (default: 10)
- `--relevance-threshold FLOAT` - Minimum relevance score (default: 0.0)
- `--output-format [table|json|compact]` - Output format (default: table)
- `--ai-purpose` - Add AI purpose classification to results
- `--ai-explain` - Add AI code explanations to results
- `--ai-docstring` - Add AI-generated docstrings to results
- `--ai-tests` - Add AI test case suggestions to results
- `--ai-all` - Add all AI analysis to results

**Examples:**
```bash
python -m src.cli kb:query "authentication middleware"
python -m src.cli kb:query "database connection" --language python --limit 20
python -m src.cli kb:query "error handling" --filepath "*/handlers/*" --relevance-threshold 0.7
python -m src.cli kb:query "JWT validation" --output-format json
python -m src.cli kb:query "user login" --ai-all
python -m src.cli kb:query "API endpoint" --repo "fastapi" --author "john@example.com"
python -m src.cli kb:query "test functions" --function "*test*" --since "2024-01-01"
```

### Create Index
```bash
python -m src.cli kb:index [OPTIONS]
```
**Options:**
- `--show-stats` - Show knowledge base statistics after indexing

**Examples:**
```bash
python -m src.cli kb:index
python -m src.cli kb:index --show-stats
```

### Show Status
```bash
python -m src.cli kb:status
```

### Show Schema
```bash
python -m src.cli kb:schema
```

### Reset Knowledge Base
```bash
python -m src.cli kb:reset [OPTIONS]
```
**Options:**
- `--force` - Skip confirmation prompt

**Examples:**
```bash
python -m src.cli kb:reset
python -m src.cli kb:reset --force
```

## Repository Sync Commands

### Create Sync Job
```bash
python -m src.cli kb:sync REPO_URL [OPTIONS]
```
**Options:**
- `--branch, -b TEXT` - Git branch to sync (default: main)
- `--schedule, -s TEXT` - Job schedule (default: EVERY 6 HOURS)
- `--force` - Force recreate sync job if exists

**Examples:**
```bash
python -m src.cli kb:sync https://github.com/psf/requests.git
python -m src.cli kb:sync https://github.com/django/django.git --branch develop --schedule "EVERY 12 HOURS"
python -m src.cli kb:sync https://github.com/fastapi/fastapi.git --force
```

### List Sync Jobs
```bash
python -m src.cli kb:sync:list
```

### Delete Sync Job
```bash
python -m src.cli kb:sync:delete JOB_NAME [OPTIONS]
```
**Options:**
- `--force` - Skip confirmation prompt

**Examples:**
```bash
python -m src.cli kb:sync:delete sync_github_com_psf_requests_git
python -m src.cli kb:sync:delete sync_django_repo --force
```

## AI Tables Commands

### Initialize AI Tables
```bash
python -m src.cli ai:init [OPTIONS]
```
**Options:**
- `--force` - Force recreate AI tables if they exist

**Examples:**
```bash
python -m src.cli ai:init
python -m src.cli ai:init --force
```

### Analyze Code
```bash
python -m src.cli ai:analyze "CODE_CHUNK" [OPTIONS]
```
**Options:**
- `--classify` - Classify the code purpose
- `--explain` - Explain the code in simple English
- `--docstring` - Generate a docstring
- `--tests` - Suggest test cases
- `--all` - Run all analysis types

**Examples:**
```bash
python -m src.cli ai:analyze "def authenticate_user(username, password): return username == 'admin'" --all
python -m src.cli ai:analyze "function validateEmail(email) { return /\S+@\S+\.\S+/.test(email); }" --explain --tests
python -m src.cli ai:analyze "class UserManager: pass" --classify --docstring
```

### List AI Tables
```bash
python -m src.cli ai:list
```

### Reset AI Tables
```bash
python -m src.cli ai:reset [OPTIONS]
```
**Options:**
- `--force` - Skip confirmation prompt

**Examples:**
```bash
python -m src.cli ai:reset
python -m src.cli ai:reset --force
```

## Common Usage Patterns

### Complete Workflow
```bash
# 1. Initialize knowledge base
python -m src.cli kb:init --validate-config

# 2. Ingest a repository
python -m src.cli kb:ingest https://github.com/psf/requests.git --extract-git-info

# 3. Create index for better performance
python -m src.cli kb:index --show-stats

# 4. Initialize AI tables
python -m src.cli ai:init

# 5. Perform semantic search
python -m src.cli kb:query "HTTP request handling" --limit 5

# 6. AI-enhanced search
python -m src.cli kb:query "authentication" --ai-all --limit 3
```

### Multiple Repository Ingestion
```bash
python -m src.cli kb:ingest https://github.com/psf/requests.git --batch-size 500
python -m src.cli kb:ingest https://github.com/django/django.git --batch-size 1000
python -m src.cli kb:ingest https://github.com/fastapi/fastapi.git --batch-size 300
```

### Advanced Search Examples
```bash
# Search Python authentication code
python -m src.cli kb:query "user authentication" --language python --limit 10

# Search recent changes in specific repository
python -m src.cli kb:query "database" --repo "django" --since "2024-01-01"

# Search test files with AI analysis
python -m src.cli kb:query "validation tests" --filepath "*/test*" --ai-explain

# High relevance search with JSON output
python -m src.cli kb:query "JWT token" --relevance-threshold 0.8 --output-format json
```

### Maintenance Commands
```bash
# Check system status
python -m src.cli kb:status

# View database schema
python -m src.cli kb:schema

# Reset everything for fresh start
python -m src.cli kb:reset --force
python -m src.cli ai:reset --force
```

### Sync Job Management
```bash
# Set up automatic syncing
python -m src.cli kb:sync https://github.com/psf/requests.git --schedule "EVERY 6 HOURS"

# Monitor sync jobs
python -m src.cli kb:sync:list

# Clean up old jobs
python -m src.cli kb:sync:delete old_job_name --force
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `kb:init` | Initialize knowledge base |
| `kb:ingest` | Ingest repository code |
| `kb:query` | Search with natural language |
| `kb:index` | Create performance index |
| `kb:status` | Show system status |
| `kb:schema` | Show database schema |
| `kb:reset` | Reset knowledge base |
| `kb:sync` | Create sync job |
| `kb:sync:list` | List sync jobs |
| `kb:sync:delete` | Delete sync job |
| `ai:init` | Initialize AI tables |
| `ai:analyze` | Analyze code with AI |
| `ai:list` | List AI tables |
| `ai:reset` | Reset AI tables |

## Environment Variables

Set these before running commands:

```bash
# Required
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# Optional (for local MindsDB)
export MINDSDB_HOST="127.0.0.1"
export MINDSDB_PORT="47334"

# Optional (for MindsDB Cloud)
export MINDSDB_USER="your-email@example.com"
export MINDSDB_PASSWORD="your-password"
```

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - Connection error
- `4` - Data error 