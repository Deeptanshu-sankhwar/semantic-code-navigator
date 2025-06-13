"""MindsDB client wrapper for knowledge base operations using the official Python SDK."""

import mindsdb_sdk
import requests
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
import json
import pandas as pd
from datetime import datetime

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
        """Insert data into knowledge base using batched raw SQL INSERT statements with proper escaping."""
        try:
            if not data:
                console.print("No data to insert", style="yellow")
                return True
            
            batch_size = batch_size or config.stress_test.batch_size
            
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i + batch_size]
                columns = list(batch_data[0].keys())
                columns_str = ', '.join(columns)
                
                values_list = []
                for record in batch_data:
                    escaped_values = []
                    for col in columns:
                        value = record[col]
                        if isinstance(value, str):
                            escaped_value = f"'{value.replace(chr(39), chr(39)+chr(39))}'" 
                        elif value is None:
                            escaped_value = "NULL"
                        else:
                            escaped_value = f"'{str(value)}'"
                        escaped_values.append(escaped_value)
                    values_list.append(f"({', '.join(escaped_values)})")
                
                values_str = ', '.join(values_list)
                insert_query = f"""
                INSERT INTO {config.kb.name} ({columns_str})
                VALUES {values_str};
                """
                
                self.execute_query(insert_query)
                console.print(f"Inserted batch {i//batch_size + 1}: {len(batch_data)} records", style="blue")
            
            console.print(f"Successfully inserted {len(data)} records", style="green")
            return True
            
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
        """Create performance index on knowledge base using raw SQL."""
        try:
            index_query = f"CREATE INDEX ON {config.kb.name};"
            self.execute_query(index_query)
            console.print(f"Created index on {config.kb.name}", style="green")
            return True
        except Exception as e:
            console.print(f"Index creation failed: {e}", style="red")
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
            # Use the correct SDK method to drop knowledge base
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
        """Clone repository, extract code chunks with metadata, and insert into knowledge base."""
        try:
            console.print(f"Starting repository ingestion: {repo_url}", style="blue")
            
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
            
            console.print(f"Inserting {len(chunks)} chunks into knowledge base...", style="blue")
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
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect() 