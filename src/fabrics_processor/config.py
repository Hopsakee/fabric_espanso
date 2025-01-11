"""Configuration management for fabric-to-espanso."""
# TODO: check if config.validate wel gebruikt wordt

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from urllib.parse import urlparse
from pathlib import Path
import logging

from parameters import (
    FABRIC_PATTERNS_FOLDER,
    YAML_OUTPUT_FOLDER,
    DEFAULT_TRIGGER,
    OBSIDIAN_OUTPUT_FOLDER,
    OBSIDIAN_INPUT_FOLDER,
    BASE_WORDS,
    USE_FASTEMBED,
    EMBED_MODEL,
    COLLECTION_NAME,
    REQUIRED_FIELDS,
    REQUIRED_FIELDS_DEFAULTS
)

logger = logging.getLogger('fabric_to_espanso')

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str = "http://localhost:6333"
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 10.0
    required_fields: list = field(default_factory=lambda: REQUIRED_FIELDS)
    required_fields_defaults: dict = field(default_factory=lambda: REQUIRED_FIELDS_DEFAULTS)


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
            cls._instance.espanso_trigger = DEFAULT_TRIGGER
            cls._instance.fabric_patterns_folder = FABRIC_PATTERNS_FOLDER
            cls._instance.yaml_output_folder = YAML_OUTPUT_FOLDER
            cls._instance.obsidian_output_folder = OBSIDIAN_OUTPUT_FOLDER
            cls._instance.obsidian_input_folder = OBSIDIAN_INPUT_FOLDER
            cls._instance.base_words = BASE_WORDS
        return cls._instance
    
    def validate(self) -> None:
        """Validate all configuration settings."""
        self.database.validate()
        self.embedding.validate()
        
        # Validate paths
        if not self.espanso_trigger:
            from .exceptions import ConfigurationError
            raise ConfigurationError("The default trigger for espanso patterns cannot be empty")

        if not self.fabric_patterns_folder:
            from .exceptions import ConfigurationError
            raise ConfigurationError("The fabric patterns folder path cannot be empty")
            
        if not self.yaml_output_folder:
            from .exceptions import ConfigurationError
            raise ConfigurationError("YAML output folder path for espanso cannot be empty")

        if not self.obsidian_output_folder:
            from .exceptions import ConfigurationError
            raise ConfigurationError("Obsidian output folder path to write the files for Obsidian Textgenerator cannot be empty")
        
        if not self.obsidian_input_folder:
            from .exceptions import ConfigurationError
            raise ConfigurationError("Obsidian input folder path to find the personal prompts stored in Obsidian cannot be empty")

        for path in [self.fabric_patterns_folder, self.yaml_output_folder, self.obsidian_output_folder, self.obsidian_input_folder]:
            if not Path(path).is_dir():
                from .exceptions import ConfigurationError
                raise ConfigurationError(f"{path} is not a valid directory")
# Global configuration instance
config = Config()
