"""Code ingestion module for parsing git repositories and extracting code chunks."""

import os
import tempfile
import shutil
import git
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import tree_sitter
from tree_sitter import Language, Parser
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

console = Console()


class CodeIngestionEngine:
    """Engine for ingesting git repositories and extracting code chunks."""
    
    LANGUAGE_MAPPING = {
        '.py': 'python',
        '.js': 'javascript', 
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.go': 'go',
        '.java': 'java',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp'
    }
    
    def __init__(self):
        self.parsers = {}
        self._setup_parsers()
    
    def _setup_parsers(self):
        """Initialize Tree-sitter parsers for supported programming languages."""
        try:
            languages_to_setup = ['python', 'javascript', 'typescript', 'go', 'java', 'rust', 'cpp']
            
            for lang in languages_to_setup:
                try:
                    pass
                except Exception as e:
                    console.print(f"Warning: Could not setup {lang} parser: {e}", style="yellow")
                    
        except Exception as e:
            console.print(f"Warning: Tree-sitter setup failed, using fallback parsing: {e}", style="yellow")
    
    def clone_repository(self, repo_url: str, branch: str = "main") -> str:
        """Clone git repository to temporary directory and return path."""
        temp_dir = tempfile.mkdtemp(prefix='semantic_nav_')
        
        try:
            console.print(f"Cloning repository: {repo_url} (branch: {branch})")
            
            repo = git.Repo.clone_from(repo_url, temp_dir, branch=branch, depth=1)
            
            console.print(f"Repository cloned to: {temp_dir}", style="green")
            return temp_dir
            
        except git.exc.GitCommandError as e:
            console.print(f"Git clone failed: {e}", style="red")
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
        except Exception as e:
            console.print(f"Repository cloning failed: {e}", style="red")
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
    
    def discover_code_files(self, repo_path: str, extensions: List[str], 
                           exclude_dirs: List[str]) -> List[str]:
        """Scan repository for code files matching specified extensions, excluding unwanted directories."""
        code_files = []
        
        valid_extensions = [f'.{ext}' if not ext.startswith('.') else ext for ext in extensions]
        
        console.print(f"Discovering code files with extensions: {', '.join(valid_extensions)}")
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in valid_extensions:
                    rel_path = os.path.relpath(file_path, repo_path)
                    code_files.append(file_path)
        
        console.print(f"Found {len(code_files)} code files", style="green")
        return code_files
    
    def extract_functions_fallback(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract functions and classes using regex patterns when Tree-sitter is unavailable."""
        functions = []
        lines = content.split('\n')
        
        if language == 'python':
            import re
            
            func_pattern = re.compile(r'^(\s*)(def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*?\):')
            
            for i, line in enumerate(lines):
                match = func_pattern.match(line)
                if match:
                    indent_level = len(match.group(1))
                    func_type = match.group(2)
                    func_name = match.group(3)
                    
                    end_line = len(lines) - 1
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith(' ' * (indent_level + 1)):
                            if lines[j].startswith(' ' * indent_level) and lines[j].strip():
                                end_line = j - 1
                                break
                    
                    func_content = '\n'.join(lines[i:end_line + 1])
                    
                    functions.append({
                        'name': func_name,
                        'type': func_type,
                        'content': func_content,
                        'start_line': i + 1,
                        'end_line': end_line + 1,
                        'line_range': f"{i + 1}-{end_line + 1}"
                    })
        
        elif language in ['javascript', 'typescript']:
            import re
            
            patterns = [
                re.compile(r'^(\s*)(function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*?\)\s*\{'),
                re.compile(r'^(\s*)(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*.*?=>\s*\{'),
                re.compile(r'^(\s*)(class)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\{'),
                re.compile(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*?\)\s*\{'),
            ]
            
            for i, line in enumerate(lines):
                for pattern in patterns:
                    match = pattern.match(line)
                    if match:
                        indent_level = len(match.group(1))
                        func_name = match.group(3) if len(match.groups()) >= 3 else match.group(2)
                        
                        brace_count = line.count('{') - line.count('}')
                        end_line = i
                        
                        for j in range(i + 1, len(lines)):
                            brace_count += lines[j].count('{') - lines[j].count('}')
                            if brace_count == 0:
                                end_line = j
                                break
                        
                        func_content = '\n'.join(lines[i:end_line + 1])
                        
                        functions.append({
                            'name': func_name,
                            'type': 'function',
                            'content': func_content,
                            'start_line': i + 1,
                            'end_line': end_line + 1,
                            'line_range': f"{i + 1}-{end_line + 1}"
                        })
                        break
        
        if not functions:
            chunk_size = 50
            for i in range(0, len(lines), chunk_size):
                chunk_lines = lines[i:i + chunk_size]
                chunk_content = '\n'.join(chunk_lines)
                
                if chunk_content.strip():
                    functions.append({
                        'name': f'chunk_{i//chunk_size + 1}',
                        'type': 'code_chunk',
                        'content': chunk_content,
                        'start_line': i + 1,
                        'end_line': min(i + chunk_size, len(lines)),
                        'line_range': f"{i + 1}-{min(i + chunk_size, len(lines))}"
                    })
        
        return functions
    
    def extract_git_metadata(self, repo_path: str, file_path: str, 
                           extract_git_info: bool = False) -> Dict[str, Any]:
        """Extract git commit metadata including author, timestamp, and repository URL."""
        metadata = {}
        
        try:
            if extract_git_info:
                repo = git.Repo(repo_path)
                
                rel_path = os.path.relpath(file_path, repo_path)
                
                commits = list(repo.iter_commits(paths=rel_path, max_count=1))
                if commits:
                    last_commit = commits[0]
                    metadata['author'] = str(last_commit.author)
                    metadata['last_modified'] = datetime.fromtimestamp(last_commit.committed_date).isoformat()
                    metadata['commit_hash'] = last_commit.hexsha[:8]
                else:
                    metadata['last_modified'] = datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).isoformat()
                
                try:
                    origin = repo.remote('origin')
                    metadata['repo'] = origin.url
                except:
                    metadata['repo'] = repo_path
            else:
                metadata['last_modified'] = datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).isoformat()
                metadata['repo'] = repo_path
                
        except Exception as e:
            console.print(f"Warning: Could not extract git metadata for {file_path}: {e}", style="yellow")
            metadata['last_modified'] = datetime.fromtimestamp(
                os.path.getmtime(file_path)
            ).isoformat()
            metadata['repo'] = repo_path
        
        return metadata
    
    def process_file(self, file_path: str, repo_path: str, repo_url: str,
                    extract_git_info: bool = False) -> List[Dict[str, Any]]:
        """Parse single code file into chunks with clean content/metadata separation."""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return chunks
            
            file_ext = os.path.splitext(file_path)[1].lower()
            language = self.LANGUAGE_MAPPING.get(file_ext, 'text')
            
            functions = self.extract_functions_fallback(content, language)
            
            git_metadata = self.extract_git_metadata(repo_path, file_path, extract_git_info)
            
            for func in functions:
                chunk_id = hashlib.md5(
                    f"{repo_url}:{os.path.relpath(file_path, repo_path)}:{func['name']}".encode()
                ).hexdigest()[:12]
                
                relative_path = os.path.relpath(file_path, repo_path)
                
                clean_code_content = func['content'].strip()
                
                chunk = {
                    'code_chunk': clean_code_content,
                    
                    'filepath': relative_path,
                    'language': language,
                    'function_name': func['name'],
                    'repo': repo_url,
                    'last_modified': git_metadata.get('last_modified', ''),
                    
                    'chunk_id': chunk_id,
                }
                
                if extract_git_info:
                    if 'author' in git_metadata:
                        chunk['author'] = git_metadata['author']
                    else:
                        chunk['author'] = ''
                    chunk['line_range'] = func.get('line_range', '')
                else:
                    chunk['author'] = ''
                    chunk['line_range'] = ''
                
                chunks.append(chunk)
        
        except Exception as e:
            console.print(f"Error processing file {file_path}: {e}", style="red")
        
        return chunks
    
    def ingest_repository(self, repo_url: str, branch: str = "main",
                         extensions: List[str] = None, exclude_dirs: List[str] = None,
                         extract_git_info: bool = False, cleanup: bool = True) -> List[Dict[str, Any]]:
        """Clone repository, discover code files, and extract chunks with metadata for knowledge base ingestion."""
        
        if extensions is None:
            extensions = ['py', 'js', 'ts', 'java', 'go', 'rs', 'cpp', 'c', 'h']
        
        if exclude_dirs is None:
            exclude_dirs = ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 'build', 'dist']
        
        temp_dir = None
        all_chunks = []
        
        try:
            temp_dir = self.clone_repository(repo_url, branch)
            
            code_files = self.discover_code_files(temp_dir, extensions, exclude_dirs)
            
            if not code_files:
                console.print("No code files found in repository", style="yellow")
                return all_chunks
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Processing code files...", total=len(code_files))
                
                for file_path in code_files:
                    chunks = self.process_file(
                        file_path, temp_dir, repo_url, extract_git_info
                    )
                    all_chunks.extend(chunks)
                    
                    progress.update(task, advance=1, 
                                  description=f"Processed {os.path.basename(file_path)}...")
            
            console.print(f"Extracted {len(all_chunks)} code chunks from {len(code_files)} files", 
                         style="bold green")
            
        except Exception as e:
            console.print(f"Repository ingestion failed: {e}", style="red")
            raise
        
        finally:
            if temp_dir and cleanup:
                try:
                    shutil.rmtree(temp_dir)
                    console.print("Cleaned up temporary files", style="dim")
                except Exception as e:
                    console.print(f"Warning: Could not cleanup temp dir: {e}", style="yellow")
        
        return all_chunks 