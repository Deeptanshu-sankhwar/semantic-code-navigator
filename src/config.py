"""Configuration management for the Semantic Code Navigator."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class MindsDBConfig:
    """MindsDB connection configuration."""
    host: str = os.getenv("MINDSDB_HOST", "127.0.0.1")
    port: int = int(os.getenv("MINDSDB_PORT", "47334"))
    user: str = os.getenv("MINDSDB_USER", "")
    password: str = os.getenv("MINDSDB_PASSWORD", "")
    database: str = os.getenv("MINDSDB_DATABASE", "mindsdb")
    
    @property
    def connection_url(self) -> str:
        """Get HTTP connection URL for configured host and port."""
        return f"http://{self.host}:{self.port}"
    
    @property
    def is_cloud_connection(self) -> bool:
        """Check if cloud credentials are configured for remote connection."""
        return bool(self.user and self.password)


@dataclass
class KnowledgeBaseConfig:
    """Knowledge Base configuration."""
    name: str = os.getenv("KB_NAME", "codebase_kb")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    reranking_model: str = os.getenv("RERANKING_MODEL", "gpt-3.5-turbo")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    metadata_columns: list = None
    content_columns: list = None
    id_column: str = "chunk_id"
    
    def __post_init__(self):
        """Initialize default metadata and content columns if not configured."""
        if self.metadata_columns is None:
            self.metadata_columns = [
                'filepath',
                'language',
                'function_name',
                'repo',
                'last_modified',
                'author',
                'line_range'
            ]
        if self.content_columns is None:
            self.content_columns = [
                'code_chunk'
            ]
    
    @property
    def required_columns(self) -> list:
        """Get essential columns required for basic stress testing functionality."""
        return [
            'content',
            'filepath', 
            'language',
            'function_name',
            'repo',
            'last_modified'
        ]
    
    @property
    def optional_columns(self) -> list:
        """Get optional columns that enhance search and filtering capabilities."""
        return [
            'author',
            'line_range', 
            'summary'
        ]
    
    @property
    def all_columns(self) -> list:
        """Get combined list of all metadata and content columns."""
        return self.metadata_columns + self.content_columns


@dataclass
class StressTestConfig:
    """Stress testing configuration."""
    max_concurrent_queries: int = int(os.getenv("MAX_CONCURRENT_QUERIES", "100"))
    stress_test_duration: int = int(os.getenv("STRESS_TEST_DURATION", "300"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "500"))
    threads: int = int(os.getenv("THREADS", "10"))


@dataclass
class AppConfig:
    """Main application configuration."""
    mindsdb: MindsDBConfig
    kb: KnowledgeBaseConfig
    stress_test: StressTestConfig
    
    def __init__(self):
        self.mindsdb = MindsDBConfig()
        self.kb = KnowledgeBaseConfig()
        self.stress_test = StressTestConfig()
    
    def validate(self) -> bool:
        """Validate required configuration parameters and raise error if missing."""
        if not self.kb.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return True


config = AppConfig() 