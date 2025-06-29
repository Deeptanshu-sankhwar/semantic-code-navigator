"""MindsDB client wrapper for knowledge base operations using the official Python SDK."""

import mindsdb_sdk
import requests
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
import json
import pandas as pd
from datetime import datetime
import time

from .config import config
from .code_ingestion import CodeIngestionEngine

console = Console()


class MindsDBClient:
    """Client for interacting with MindsDB Knowledge Base using the official Python SDK."""
    
    def __init__(self):
        self.server = None
        
    def connect(self) -> bool:
        """Establish connection to MindsDB using configured host/credentials or default local instance."""
        try:
            if config.mindsdb.host and config.mindsdb.port:
                connection_url = f"http://{config.mindsdb.host}:{config.mindsdb.port}"
                self.server = mindsdb_sdk.connect(connection_url)
            else:
                if config.mindsdb.user and config.mindsdb.password:
                    self.server = mindsdb_sdk.connect(
                        login=config.mindsdb.user,
                        password=config.mindsdb.password
                    )
                else:
                    self.server = mindsdb_sdk.connect('http://127.0.0.1:47334')
            
            console.print("Connected to MindsDB", style="green")
            return True
            
        except Exception as e:
            console.print(f"Connection failed: {e}", style="red")
            return False
    
    def disconnect(self):
        """Close connection to MindsDB."""
        self.server = None
        console.print("Disconnected from MindsDB", style="dim")
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute raw SQL query and return results as list of dictionaries."""
        try:
            result = self.server.query(query)
            if hasattr(result, 'fetch'):
                data = result.fetch()
                if hasattr(data, 'to_dict'):
                    return data.to_dict('records')
                return data if isinstance(data, list) else []
            return []
        except Exception as e:
            console.print(f"Query execution failed: {e}", style="red")
            raise
    
    def create_knowledge_base(self) -> bool:
        """Create knowledge base with OpenAI embedding/reranking models and configured content/metadata columns."""
        try:
            try:
                describe_query = f"DESCRIBE KNOWLEDGE_BASE {config.kb.name};"
                result = self.execute_query(describe_query)
                if result:
                    console.print(f"Knowledge base '{config.kb.name}' already exists", style="yellow")
                    return True
            except:
                pass
            
            metadata_cols = ', '.join([f"'{col}'" for col in config.kb.metadata_columns])
            content_cols = ', '.join([f"'{col}'" for col in config.kb.content_columns])
            
            create_kb_query = f"""
            CREATE KNOWLEDGE_BASE {config.kb.name}
            USING
                embedding_model = {{
                    "provider": "openai",
                    "model_name": "{config.kb.embedding_model}",
                    "api_key": "{config.kb.openai_api_key}"
                }},
                reranking_model = {{
                    "provider": "openai", 
                    "model_name": "{config.kb.reranking_model}",
                    "api_key": "{config.kb.openai_api_key}"
                }},
                content_columns = [{content_cols}],
                metadata_columns = [{metadata_cols}];
            """
            
            self.execute_query(create_kb_query)
            console.print(f"Created knowledge base: {config.kb.name}", style="green")
            return True
            
        except Exception as e:
            console.print(f"Failed to create knowledge base: {e}", style="red")
            return False
    
    def insert_data(self, data: List[Dict[str, Any]], batch_size: Optional[int] = None) -> bool:
        """Insert data into knowledge base using batched raw SQL INSERT statements.
        
        Uses proper SQL escaping and connection recovery for stable insertion.
        Implements retry logic for transient connection failures and provides
        detailed progress reporting for batch operations.
        """
        try:
            if not data:
                console.print("No data to insert", style="yellow")
                return True
            
            batch_size = min(batch_size or config.stress_test.batch_size, 25)
            console.print(f"Using batch size: {batch_size} for stable insertion", style="blue")
            console.print(f"Total records to insert: {len(data)}", style="blue")
            
            successful_batches = 0
            total_batches = (len(data) + batch_size - 1) // batch_size
            
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        columns = list(batch_data[0].keys())
                        columns_str = ', '.join(columns)
                        
                        values_list = []
                        for record in batch_data:
                            escaped_values = []
                            for col in columns:
                                value = record[col]
                                if isinstance(value, str):
                                    escaped_str = value.replace("\\", "\\\\").replace("'", "''")
                                    escaped_value = f"'{escaped_str}'"
                                elif value is None:
                                    escaped_value = "NULL"
                                else:
                                    escaped_value = f"'{str(value).replace(chr(39), chr(39)+chr(39))}'"
                                escaped_values.append(escaped_value)
                            values_list.append(f"({', '.join(escaped_values)})")
                        
                        values_str = ', '.join(values_list)
                        insert_query = f"""
                        INSERT INTO {config.kb.name} ({columns_str})
                        VALUES {values_str};
                        """
                        
                        self.execute_query(insert_query)
                        console.print(f"Inserted batch {batch_num}/{total_batches}: {len(batch_data)} records", style="green")
                        successful_batches += 1
                        break
                        
                    except Exception as batch_error:
                        if attempt < max_retries - 1:
                            console.print(f"Batch {batch_num} failed (attempt {attempt + 1}), retrying...", style="yellow")
                            console.print(f"   Error: {str(batch_error)[:100]}...", style="dim")
                            time.sleep(2)
                            
                            try:
                                console.print("Reconnecting to MindsDB...", style="dim")
                                self.disconnect()
                                time.sleep(1)
                                self.connect()
                            except:
                                pass
                        else:
                            console.print(f"Batch {batch_num} failed after {max_retries} attempts: {batch_error}", style="red")
                            continue
                
                if batch_num < total_batches:
                    time.sleep(0.5)
            
            if successful_batches == total_batches:
                console.print(f"Successfully inserted all {len(data)} records in {successful_batches} batches", style="green")
                return True
            elif successful_batches > 0:
                inserted_records = successful_batches * batch_size
                console.print(f"Partially successful: inserted ~{inserted_records} of {len(data)} records", style="yellow")
                return True
            else:
                console.print("Failed to insert any data", style="red")
                return False
            
        except Exception as e:
            console.print(f"Data insertion failed: {e}", style="red")
            return False
    
    def semantic_search(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                       limit: int = 10, relevance_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Perform semantic search using SDK, extract metadata from JSON, and apply filters/thresholds."""
        try:
            kb = self.server.knowledge_bases.get(config.kb.name)
            if not kb:
                console.print(f"Knowledge base '{config.kb.name}' not found", style="red")
                return []
            
            search_result = kb.find(query, limit=limit)
            results = search_result.fetch()
            
            if hasattr(results, 'to_dict'):
                results_list = results.to_dict('records')
            else:
                results_list = list(results) if results else []
            
            transformed_results = []
            for result in results_list:
                metadata = result.get('metadata', {})
                if isinstance(metadata, str):
                    try:
                        import json
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                transformed_result = {
                    'chunk_content': result.get('chunk_content', ''),
                    'relevance': result.get('relevance', 0.0),
                    'distance': result.get('distance', 0.0),
                    'filepath': metadata.get('filepath', 'Unknown'),
                    'language': metadata.get('language', 'Unknown'),
                    'function_name': metadata.get('function_name', 'Unknown'),
                    'repo': metadata.get('repo', 'Unknown'),
                    'last_modified': metadata.get('last_modified', 'Unknown'),
                    'author': metadata.get('author', ''),
                    'line_range': metadata.get('line_range', ''),
                }
                
                transformed_results.append(transformed_result)
            
            if filters:
                filtered_results = []
                for result in transformed_results:
                    match = True
                    for key, value in filters.items():
                        if key in config.kb.metadata_columns:
                            result_value = result.get(key, '')
                            if '*' in value or '%' in value:
                                import fnmatch
                                if not fnmatch.fnmatch(result_value, value.replace('%', '*')):
                                    match = False
                                    break
                            elif value.startswith('>') or value.startswith('<'):
                                continue
                            else:
                                if result_value != value:
                                    match = False
                                    break
                    if match:
                        filtered_results.append(result)
                transformed_results = filtered_results
            
            if relevance_threshold > 0:
                transformed_results = [
                    result for result in transformed_results 
                    if result.get('relevance', 0) >= relevance_threshold
                ]
            
            console.print(f"Found {len(transformed_results)} results", style="blue")
            return transformed_results
            
        except Exception as e:
            console.print(f"Search failed: {e}", style="red")
            try:
                kb = self.server.knowledge_bases.get(config.kb.name)
                if kb:
                    search_query = kb.find(query, limit=limit)
                    results = search_query.fetch()
                    
                    if hasattr(results, 'to_dict'):
                        results_list = results.to_dict('records')
                    else:
                        results_list = list(results) if results else []
                    
                    for result in results_list:
                        result['filepath'] = result.get('filepath', 'Unknown')
                        result['language'] = result.get('language', 'Unknown')
                        result['function_name'] = result.get('function_name', 'Unknown')
                    
                    return results_list
                    
            except Exception as fallback_error:
                console.print(f"Fallback search also failed: {fallback_error}", style="red")
                return []
    
    def create_index(self) -> bool:
        """Create performance index on knowledge base.
        
        MindsDB Knowledge Bases are automatically indexed for semantic search.
        No manual index creation is needed or supported by the platform.
        """
        try:
            console.print(f"Knowledge base '{config.kb.name}' is automatically indexed for semantic search", style="green")
            console.print("MindsDB handles vector indexing internally for optimal performance", style="blue")
            return True
        except Exception as e:
            console.print(f"Index status check failed: {e}", style="red")
            return False
    
    def describe_knowledge_base(self) -> Dict[str, Any]:
        """Get knowledge base metadata and status information via SQL query."""
        try:
            describe_query = f"DESCRIBE KNOWLEDGE_BASE {config.kb.name};"
            result = self.execute_query(describe_query)
            
            if result and len(result) > 0:
                return result[0] if isinstance(result, list) else {"name": config.kb.name, "status": "active"}
            return {"name": config.kb.name, "status": "not_found"}
        except Exception as e:
            console.print(f"Failed to describe knowledge base: {e}", style="red")
            return {"name": config.kb.name, "status": "error"}
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get detailed schema information by sampling records or returning expected schema structure."""
        try:
            stats = self.get_stats()
            total_records = stats.get('total_records', 0)
            
            if total_records == 0:
                return None
            
            try:
                kb = self.server.knowledge_bases.get(config.kb.name)
                if kb:
                    sample_search = kb.find("function", limit=1)
                    sample_results = sample_search.fetch()
                    
                    if hasattr(sample_results, 'to_dict'):
                        sample_list = sample_results.to_dict('records')
                    else:
                        sample_list = list(sample_results) if sample_results else []
                    
                    if sample_list and len(sample_list) > 0:
                        sample_row = sample_list[0]
                        columns = []
                        
                        for col_name in sample_row.keys():
                            col_type = type(sample_row[col_name]).__name__
                            columns.append({
                                "name": col_name,
                                "type": col_type
                            })
                        
                        return {
                            "name": config.kb.name,
                            "columns": columns,
                            "status": "active",
                            "total_records": total_records
                        }
            except Exception as e:
                pass
            
            if total_records > 0:
                columns = []
                for col in config.kb.all_columns + [config.kb.id_column]:
                    columns.append({
                        "name": col,
                        "type": "TEXT"
                    })
                
                return {
                    "name": config.kb.name,
                    "columns": columns,
                    "status": "active",
                    "total_records": total_records
                }
            
            return None
            
        except Exception as e:
            console.print(f"Failed to get schema info: {e}", style="red")
            return None
    
    def drop_knowledge_base(self) -> bool:
        """Drop the knowledge base."""
        try:
            self.server.knowledge_bases.drop(config.kb.name)
            console.print(f"Dropped knowledge base: {config.kb.name}", style="yellow")
            return True
        except Exception as e:
            console.print(f"Failed to drop knowledge base: {e}", style="red")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base record count and basic statistics via SQL query."""
        try:
            stats_query = f"SELECT COUNT(*) as total_records FROM {config.kb.name};"
            result = self.execute_query(stats_query)
            
            if result and len(result) > 0:
                return {"total_records": result[0].get("total_records", 0)}
            return {"total_records": 0}
        except Exception as e:
            console.print(f"Failed to get statistics: {e}", style="red")
            return {"total_records": 0}
    
    def list_knowledge_bases(self) -> List[str]:
        """List all knowledge bases."""
        try:
            kbs = self.server.knowledge_bases.list()
            return [kb.name for kb in kbs] if kbs else []
        except Exception as e:
            console.print(f"Failed to list knowledge bases: {e}", style="red")
            return []
    
    def ingest_git_repository(self, repo_url: str, branch: str = "main",
                             extensions: List[str] = None, exclude_dirs: List[str] = None,
                             batch_size: int = 500, extract_git_info: bool = False,
                             generate_summaries: bool = False, cleanup: bool = True) -> bool:
        """Clone repository, extract code chunks with metadata, and insert into knowledge base.
        
        Clones the specified Git repository, parses code files to extract functions and classes,
        and inserts the resulting code chunks into the knowledge base with metadata.
        Provides language breakdown statistics upon successful completion.
        """
        try:
            console.print(f"Starting repository ingestion: {repo_url}", style="blue")
            console.print(f"This may take a few minutes depending on repository size...", style="dim")
            
            ingestion_engine = CodeIngestionEngine()
            chunks = ingestion_engine.ingest_repository(
                repo_url=repo_url,
                branch=branch,
                extensions=extensions or ['py', 'js', 'ts', 'java', 'go', 'rs', 'cpp', 'c', 'h'],
                exclude_dirs=exclude_dirs or ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 'build', 'dist'],
                extract_git_info=extract_git_info,
                cleanup=cleanup
            )
            
            if not chunks:
                console.print("No code chunks extracted from repository", style="yellow")
                return True
            
            console.print(f"Extracted {len(chunks)} code chunks from repository", style="green")
            console.print(f"Starting batch insertion into knowledge base...", style="blue")
            success = self.insert_data(chunks, batch_size)
            
            if success:
                console.print(f"Successfully ingested {len(chunks)} code chunks", style="bold green")
                
                langs = {}
                for chunk in chunks:
                    lang = chunk.get('language', 'unknown')
                    langs[lang] = langs.get(lang, 0) + 1
                
                console.print(f"Language breakdown:", style="bold")
                for lang, count in sorted(langs.items(), key=lambda x: x[1], reverse=True):
                    console.print(f"  {lang}: {count} chunks")
                
                return True
            else:
                console.print("Failed to insert chunks into knowledge base", style="red")
                return False
                
        except Exception as e:
            console.print(f"Repository ingestion failed: {e}", style="red")
            return False
    
    def create_sync_job(self, repo_url: str, branch: str = "main", schedule: str = "EVERY 6 HOURS") -> bool:
        """Create a scheduled job to sync repository changes using REST API.
        
        Creates a job that runs on the specified schedule to ingest new changes since the last sync.
        Uses MindsDB REST API for job creation.
        
        Args:
            repo_url: URL of the git repository to sync
            branch: Git branch to sync (default: main)
            schedule: Job schedule in MindsDB format (default: EVERY 6 HOURS)
            
        Returns:
            bool: True if job creation was successful, False otherwise
        """
        try:
            job_name = f"sync_{repo_url.split('/')[-1].replace('.git', '')}"
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            job_data = {
                "job": {
                    "name": job_name,
                    "query": f"""
                        SELECT * FROM {config.kb.name}
                        WHERE repo = '{repo_url}'
                        AND metadata->>'last_modified' > (
                            SELECT MAX(metadata->>'last_modified') 
                            FROM {config.kb.name} 
                            WHERE repo = '{repo_url}'
                        )
                    """,
                    "schedule_str": schedule,
                    "start_at": current_time,
                    "end_at": current_time
                }
            }
            
            api_url = f"{config.mindsdb.connection_url}/api/projects/mindsdb/jobs"
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(api_url, json=job_data, headers=headers)
            
            if response.status_code == 200:
                console.print(f"Created sync job '{job_name}' for {repo_url}", style="green")
                return True
            else:
                console.print(f"Failed to create sync job. Status: {response.status_code}, Response: {response.text}", style="red")
                return False
            
        except Exception as e:
            console.print(f"Failed to create sync job: {e}", style="red")
            return False
    
    def list_sync_jobs(self) -> List[Dict[str, Any]]:
        """List all repository sync jobs using REST API.
        
        Retrieves all jobs from MindsDB and filters for those that start with 'sync_'.
        Each job entry includes name, schedule, status, and other job information.
        
        Returns:
            List of dictionaries containing job information
        """
        try:
            api_url = f"{config.mindsdb.connection_url}/api/projects/mindsdb/jobs"
            
            response = requests.get(api_url)
            
            if response.status_code == 200:
                all_jobs = response.json()
                
                sync_jobs = []
                for job in all_jobs:
                    if job.get('name', '').startswith('sync_'):
                        sync_jobs.append({
                            'name': job.get('name', ''),
                            'schedule': job.get('schedule_str', ''),
                            'status': 'active',
                            'last_run': job.get('start_at', ''),
                            'next_run': job.get('end_at', '')
                        })
                
                return sync_jobs
            else:
                console.print(f"Failed to list jobs. Status: {response.status_code}", style="red")
                return []
            
        except Exception as e:
            console.print(f"Failed to list sync jobs: {e}", style="red")
            return []
    
    def delete_sync_job(self, job_name: str) -> bool:
        """Delete a repository sync job using REST API.
        
        Removes the sync job using MindsDB REST API.
        
        Args:
            job_name: Name of the job to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            api_url = f"{config.mindsdb.connection_url}/api/projects/mindsdb/jobs/{job_name}"
            
            response = requests.delete(api_url)
            
            if response.status_code == 200:
                console.print(f"Deleted sync job '{job_name}'", style="green")
                return True
            else:
                console.print(f"Failed to delete sync job. Status: {response.status_code}, Response: {response.text}", style="red")
                return False
            
        except Exception as e:
            console.print(f"Failed to delete sync job: {e}", style="red")
            return False
    
    def create_single_ai_table(self, table_name: str, predict_column: str, prompt_template: str) -> bool:
        """Create a single AI table with retry logic."""
        try:
            console.print(f"Creating AI table: {table_name}", style="blue")
            
            create_model_query = f"""
            CREATE MODEL {table_name}
            PREDICT {predict_column}
            USING
                engine = 'openai',
                model_name = 'gpt-3.5-turbo',
                openai_api_key = '{config.kb.openai_api_key}',
                prompt_template = '{prompt_template}';
            """
            
            self.execute_query(create_model_query)
            console.print(f"Created AI table: {table_name}", style="green")
            return True
            
        except Exception as e:
            if "already exists" in str(e).lower():
                console.print(f"AI table already exists: {table_name}", style="yellow")
                return True
            else:
                console.print(f"Failed to create AI table {table_name}: {e}", style="red")
                return False
    
    def create_ai_tables_individually(self) -> bool:
        """Create AI tables one by one with better error handling."""
        try:
            ai_tables = [
                {
                    "name": "code_classifier",
                    "predict": "purpose",
                    "prompt": 'Classify the purpose of the following function in one or two words: {{code_chunk}}'
                },
                {
                    "name": "code_explainer", 
                    "predict": "explanation",
                    "prompt": 'Explain this function in simple English: {{code_chunk}}'
                },
                {
                    "name": "docstring_generator",
                    "predict": "docstring", 
                    "prompt": 'Generate a docstring for the following function: {{code_chunk}}'
                },
                {
                    "name": "test_case_outliner",
                    "predict": "test_plan",
                    "prompt": 'Suggest 3 test cases (just names) for this function: {{code_chunk}}'
                },
                {
                    "name": "result_rationale",
                    "predict": "rationale",
                    "prompt": 'Given this code and the search query "{{search_query}}", explain why this function was a match: {{code_chunk}}'
                }
            ]
            
            success_count = 0
            
            for table in ai_tables:
                try:
                    if self.create_single_ai_table(table['name'], table['predict'], table['prompt']):
                        success_count += 1
                    
                    time.sleep(2)
                    
                except Exception as e:
                    console.print(f"Error creating {table['name']}: {e}", style="red")
                    continue
            
            console.print(f"Successfully created {success_count}/5 AI tables", style="bold green" if success_count == 5 else "yellow")
            return success_count == 5
            
        except Exception as e:
            console.print(f"Failed to create AI tables: {e}", style="red")
            return False
    
    def create_ai_tables(self) -> bool:
        """Create AI tables for code analysis using OpenAI models."""
        return self.create_ai_tables_individually()
    
    def list_ai_tables(self) -> List[str]:
        """List all AI tables (models) in MindsDB."""
        try:
            query = "SHOW MODELS;"
            models = self.execute_query(query)
            
            ai_table_names = ["code_classifier", "code_explainer", "docstring_generator", 
                             "test_case_outliner", "result_rationale"]
            
            existing_tables = []
            for model in models:
                model_name = model.get('name', model.get('NAME', ''))
                if model_name in ai_table_names:
                    existing_tables.append(model_name)
            
            return existing_tables
            
        except Exception as e:
            console.print(f"Failed to list AI tables: {e}", style="red")
            return []
    
    def drop_ai_tables(self) -> bool:
        """Drop all AI tables for code analysis."""
        try:
            ai_table_names = ["code_classifier", "code_explainer", "docstring_generator", 
                             "test_case_outliner", "result_rationale"]
            
            for table_name in ai_table_names:
                try:
                    drop_query = f"DROP MODEL {table_name};"
                    self.execute_query(drop_query)
                    console.print(f"Dropped AI table: {table_name}", style="green")
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        console.print(f"AI table doesn't exist: {table_name}", style="yellow")
                    else:
                        console.print(f"Failed to drop AI table {table_name}: {e}", style="red")
            
            console.print("AI tables cleanup completed!", style="bold green")
            return True
            
        except Exception as e:
            console.print(f"Failed to drop AI tables: {e}", style="red")
            return False
    
    def classify_code_purpose(self, code_chunk: str) -> str:
        """Classify the purpose of a code chunk using the code_classifier AI table.
        
        Args:
            code_chunk: The code to classify
            
        Returns:
            Purpose classification as a string
        """
        try:
            query = f"""
            SELECT purpose
            FROM code_classifier
            WHERE code_chunk = '{code_chunk.replace("'", "''")}';
            """
            
            result = self.execute_query(query)
            if result and len(result) > 0:
                return result[0].get('purpose', 'unknown')
            return 'unknown'
            
        except Exception as e:
            console.print(f"Failed to classify code purpose: {e}", style="red")
            return 'unknown'
    
    def explain_code(self, code_chunk: str) -> str:
        """Explain a code chunk using the code_explainer AI table.
        
        Args:
            code_chunk: The code to explain
            
        Returns:
            Code explanation as a string
        """
        try:
            query = f"""
            SELECT explanation
            FROM code_explainer
            WHERE code_chunk = '{code_chunk.replace("'", "''")}';
            """
            
            result = self.execute_query(query)
            if result and len(result) > 0:
                return result[0].get('explanation', 'No explanation available')
            return 'No explanation available'
            
        except Exception as e:
            console.print(f"Failed to explain code: {e}", style="red")
            return 'No explanation available'
    
    def generate_docstring(self, code_chunk: str) -> str:
        """Generate a docstring for a code chunk using the docstring_generator AI table.
        
        Args:
            code_chunk: The code to generate docstring for
            
        Returns:
            Generated docstring as a string
        """
        try:
            query = f"""
            SELECT docstring
            FROM docstring_generator
            WHERE code_chunk = '{code_chunk.replace("'", "''")}';
            """
            
            result = self.execute_query(query)
            if result and len(result) > 0:
                return result[0].get('docstring', 'No docstring generated')
            return 'No docstring generated'
            
        except Exception as e:
            console.print(f"Failed to generate docstring: {e}", style="red")
            return 'No docstring generated'
    
    def suggest_test_cases(self, code_chunk: str) -> str:
        """Suggest test cases for a code chunk using the test_case_outliner AI table.
        
        Args:
            code_chunk: The code to suggest test cases for
            
        Returns:
            Test case suggestions as a string
        """
        try:
            query = f"""
            SELECT test_plan
            FROM test_case_outliner
            WHERE code_chunk = '{code_chunk.replace("'", "''")}';
            """
            
            result = self.execute_query(query)
            if result and len(result) > 0:
                return result[0].get('test_plan', 'No test cases suggested')
            return 'No test cases suggested'
            
        except Exception as e:
            console.print(f"Failed to suggest test cases: {e}", style="red")
            return 'No test cases suggested'
    
    def explain_search_match(self, code_chunk: str, search_query: str) -> str:
        """Explain why a code chunk matches a search query using the result_rationale AI table.
        
        Args:
            code_chunk: The code that was found
            search_query: The original search query
            
        Returns:
            Explanation of why the code matches the query
        """
        try:
            query = f"""
            SELECT rationale
            FROM result_rationale
            WHERE code_chunk = '{code_chunk.replace("'", "''")}'
            AND search_query = '{search_query.replace("'", "''")}';
            """
            
            result = self.execute_query(query)
            if result and len(result) > 0:
                return result[0].get('rationale', 'No explanation available')
            return 'No explanation available'
            
        except Exception as e:
            console.print(f"Failed to explain search match: {e}", style="red")
            return 'No explanation available'
    
    def semantic_search_with_ai_analysis(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                                       limit: int = 10, relevance_threshold: float = 0.0,
                                       analyze_purpose: bool = False, analyze_explanation: bool = False,
                                       analyze_docstring: bool = False, analyze_tests: bool = False) -> List[Dict[str, Any]]:
        """Perform semantic search and analyze results with AI tables in a single workflow."""
        try:
            search_results = self.semantic_search(query, filters, limit, relevance_threshold)
            
            if not search_results:
                return []
            
            available_ai_tables = self.list_ai_tables()
            console.print(f"Available AI tables: {', '.join(available_ai_tables)}", style="dim")
            
            enriched_results = []
            
            for result in search_results:
                code_chunk = result.get('chunk_content', '')
                if not code_chunk.strip():
                    enriched_results.append(result)
                    continue
                
                enriched_result = result.copy()
                
                if analyze_purpose and 'code_classifier' in available_ai_tables:
                    try:
                        purpose_query = f"""
                        SELECT purpose
                        FROM code_classifier
                        WHERE code_chunk = '{code_chunk.replace("'", "''")}';
                        """
                        purpose_result = self.execute_query(purpose_query)
                        if purpose_result and len(purpose_result) > 0:
                            enriched_result['ai_purpose'] = purpose_result[0].get('purpose', 'unknown')
                        else:
                            enriched_result['ai_purpose'] = 'unknown'
                    except Exception as e:
                        console.print(f"Warning: Purpose classification failed: {e}", style="yellow")
                        enriched_result['ai_purpose'] = 'error'
                elif analyze_purpose:
                    enriched_result['ai_purpose'] = 'unavailable (table not created)'
                
                if analyze_explanation and 'code_explainer' in available_ai_tables:
                    try:
                        explanation_query = f"""
                        SELECT explanation
                        FROM code_explainer
                        WHERE code_chunk = '{code_chunk.replace("'", "''")}';
                        """
                        explanation_result = self.execute_query(explanation_query)
                        if explanation_result and len(explanation_result) > 0:
                            enriched_result['ai_explanation'] = explanation_result[0].get('explanation', 'No explanation available')
                        else:
                            enriched_result['ai_explanation'] = 'No explanation available'
                    except Exception as e:
                        console.print(f"Warning: Code explanation failed: {e}", style="yellow")
                        enriched_result['ai_explanation'] = 'error'
                elif analyze_explanation:
                    enriched_result['ai_explanation'] = 'unavailable (table not created)'
                
                if analyze_docstring and 'docstring_generator' in available_ai_tables:
                    try:
                        docstring_query = f"""
                        SELECT docstring
                        FROM docstring_generator
                        WHERE code_chunk = '{code_chunk.replace("'", "''")}';
                        """
                        docstring_result = self.execute_query(docstring_query)
                        if docstring_result and len(docstring_result) > 0:
                            enriched_result['ai_docstring'] = docstring_result[0].get('docstring', 'No docstring generated')
                        else:
                            enriched_result['ai_docstring'] = 'No docstring generated'
                    except Exception as e:
                        console.print(f"Warning: Docstring generation failed: {e}", style="yellow")
                        enriched_result['ai_docstring'] = 'error'
                elif analyze_docstring:
                    enriched_result['ai_docstring'] = 'unavailable (table not created)'
                
                if analyze_tests and 'test_case_outliner' in available_ai_tables:
                    try:
                        tests_query = f"""
                        SELECT test_plan
                        FROM test_case_outliner
                        WHERE code_chunk = '{code_chunk.replace("'", "''")}';
                        """
                        tests_result = self.execute_query(tests_query)
                        if tests_result and len(tests_result) > 0:
                            enriched_result['ai_test_cases'] = tests_result[0].get('test_plan', 'No test cases suggested')
                        else:
                            enriched_result['ai_test_cases'] = 'No test cases suggested'
                    except Exception as e:
                        console.print(f"Warning: Test case suggestion failed: {e}", style="yellow")
                        enriched_result['ai_test_cases'] = 'error'
                elif analyze_tests:
                    enriched_result['ai_test_cases'] = 'unavailable (table not created)'
                
                if 'result_rationale' in available_ai_tables:
                    try:
                        rationale_query = f"""
                        SELECT rationale
                        FROM result_rationale
                        WHERE code_chunk = '{code_chunk.replace("'", "''")}'
                        AND search_query = '{query.replace("'", "''")}';
                        """
                        rationale_result = self.execute_query(rationale_query)
                        if rationale_result and len(rationale_result) > 0:
                            enriched_result['ai_match_rationale'] = rationale_result[0].get('rationale', 'No rationale available')
                        else:
                            enriched_result['ai_match_rationale'] = 'No rationale available'
                    except Exception as e:
                        console.print(f"Warning: Search rationale failed: {e}", style="yellow")
                        enriched_result['ai_match_rationale'] = 'error'
                else:
                    enriched_result['ai_match_rationale'] = 'unavailable (table not created)'
                
                enriched_results.append(enriched_result)
            
            console.print(f"Enhanced {len(enriched_results)} results with AI analysis", style="green")
            return enriched_results
            
        except Exception as e:
            console.print(f"Workflow search failed: {e}", style="red")
            return []
    
    def create_ai_workflow_view(self) -> bool:
        """Create a SQL view that combines KB search results with AI table analysis.
        
        This creates a reusable view that demonstrates the multi-step workflow
        by joining the knowledge base with AI tables.
        
        Returns:
            bool: True if view was created successfully
        """
        try:
            create_view_query = f"""
            CREATE OR REPLACE VIEW code_analysis_workflow AS
            SELECT 
                kb.chunk_content,
                kb.filepath,
                kb.language,
                kb.function_name,
                kb.repo,
                classifier.purpose as ai_purpose,
                explainer.explanation as ai_explanation,
                docgen.docstring as ai_docstring,
                tester.test_plan as ai_test_cases
            FROM {config.kb.name} kb
            LEFT JOIN code_classifier classifier ON classifier.code_chunk = kb.chunk_content
            LEFT JOIN code_explainer explainer ON explainer.code_chunk = kb.chunk_content  
            LEFT JOIN docstring_generator docgen ON docgen.code_chunk = kb.chunk_content
            LEFT JOIN test_case_outliner tester ON tester.code_chunk = kb.chunk_content
            LIMIT 100;
            """
            
            self.execute_query(create_view_query)
            console.print("Created AI workflow view: code_analysis_workflow", style="green")
            return True
            
        except Exception as e:
            console.print(f"Failed to create AI workflow view: {e}", style="red")
            return False
    
    def query_ai_workflow_view(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Query the AI workflow view to demonstrate integrated analysis.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of results with both KB data and AI analysis
        """
        try:
            query = f"""
            SELECT * FROM code_analysis_workflow
            LIMIT {limit};
            """
            
            results = self.execute_query(query)
            console.print(f"Retrieved {len(results)} results from AI workflow view", style="blue")
            return results
            
        except Exception as e:
            console.print(f"Failed to query AI workflow view: {e}", style="red")
            return []
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    