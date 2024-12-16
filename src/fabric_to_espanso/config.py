"""Configuration management for fabric-to-espanso."""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse

from parameters import (
    MARKDOWN_FOLDER,
    YAML_OUTPUT_FOLDER,
    USE_FASTEMBED,
    EMBED_MODEL,
    COLLECTION_NAME,
    BASE_WORDS
)

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str = "http://localhost:6333"
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 10.0

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
    use_fastembed: bool = USE_FASTEMBED
    model_name: str = EMBED_MODEL
    collection_name: str = COLLECTION_NAME
    vector_size: int = 384
    
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
    _instance: Optional['Config'] = None
    
    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.database = DatabaseConfig()
            cls._instance.embedding = EmbeddingConfig()
            cls._instance.markdown_folder = MARKDOWN_FOLDER
            cls._instance.yaml_output_folder = YAML_OUTPUT_FOLDER
            cls._instance.base_words = BASE_WORDS
        return cls._instance
    
    def validate(self) -> None:
        """Validate all configuration settings."""
        self.database.validate()
        self.embedding.validate()
        
        # Validate paths
        if not self.markdown_folder:
            from .exceptions import ConfigurationError
            raise ConfigurationError("Markdown folder path cannot be empty")
            
        if not self.yaml_output_folder:
            from .exceptions import ConfigurationError
            raise ConfigurationError("YAML output folder path cannot be empty")

# Global configuration instance
config = Config()
