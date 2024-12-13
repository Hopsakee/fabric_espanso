"""Configuration management for fabric-to-espanso."""
from typing import Dict, Any, Optional
import os
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str = os.getenv('QDRANT_URL', 'http://localhost:6333')
    max_retries: int = int(os.getenv('QDRANT_MAX_RETRIES', '3'))
    retry_delay: float = float(os.getenv('QDRANT_RETRY_DELAY', '1.0'))
    timeout: float = float(os.getenv('QDRANT_TIMEOUT', '10.0'))

    def validate(self) -> None:
        """Validate the database configuration.
        
        Raises:
            ConfigurationError: If any configuration values are invalid.
        """
        try:
            result = urlparse(self.url)
            if not all([result.scheme, result.netloc]):
                raise ValueError(f"Invalid database URL: {self.url}")
            
            if self.max_retries < 0:
                raise ValueError(f"max_retries must be >= 0, got {self.max_retries}")
            
            if self.retry_delay <= 0:
                raise ValueError(f"retry_delay must be > 0, got {self.retry_delay}")
            
            if self.timeout <= 0:
                raise ValueError(f"timeout must be > 0, got {self.timeout}")
                
        except ValueError as e:
            from .exceptions import ConfigurationError
            raise ConfigurationError(str(e))

@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    use_fastembed: bool = os.getenv('USE_FASTEMBED', 'true').lower() == 'true'
    model_name: str = os.getenv('EMBED_MODEL', 'fast-bge-small-en')
    vector_size: int = int(os.getenv('VECTOR_SIZE', '384'))
    
    def validate(self) -> None:
        """Validate the embedding configuration."""
        if not self.model_name:
            from .exceptions import ConfigurationError
            raise ConfigurationError("Embedding model name cannot be empty")
        
        if self.vector_size <= 0:
            from .exceptions import ConfigurationError
            raise ConfigurationError(f"Vector size must be > 0, got {self.vector_size}")

class Config:
    """Global configuration singleton."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.database = DatabaseConfig()
            cls._instance.embedding = EmbeddingConfig()
        return cls._instance
        
    def validate(self):
        """Validate all configuration settings."""
        self.database.validate()
        self.embedding.validate()

# Global configuration instance
config = Config()
