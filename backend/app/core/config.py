"""
Le Sésame Backend - Configuration Module

Supports loading configuration from:
1. Environment variables (highest priority)
2. .env file
3. config/config.yaml file (lowest priority)

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import os
import json
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any, Optional

import yaml
from pydantic_settings import BaseSettings
from pydantic import Field


# Possible locations for config.yaml
CONFIG_PATHS = [
    Path("/app/config/config.yaml"),  # Docker mount location
    Path("../deployment/local/backend/config.local.yaml"),  # Local development (from backend/)
    Path("../../deployment/local/backend/config.local.yaml"),  # Local development (from backend/app/)
]


def load_yaml_config() -> Dict[str, Any]:
    """Load configuration from YAML file if available."""
    for config_path in CONFIG_PATHS:
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
                    print(f"✓ Loaded config from {config_path}")
                    return config
            except Exception as e:
                print(f"⚠ Failed to load {config_path}: {e}")
    return {}


def get_yaml_value(yaml_config: Dict[str, Any], *keys, default=None):
    """Get a nested value from YAML config."""
    value = yaml_config
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value


# Load YAML config once at module level
_yaml_config = load_yaml_config()


class Settings(BaseSettings):
    """Application settings loaded from environment variables and YAML config."""
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "server", "debug", default=True),
        alias="DEBUG"
    )
    log_level: str = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "logging", "level", default="INFO"),
        alias="LOG_LEVEL"
    )
    
    # Server
    host: str = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "server", "host", default="0.0.0.0"),
        alias="HOST"
    )
    port: int = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "server", "port", default=8000),
        alias="PORT"
    )
    
    # Database
    database_url: str = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "database", "url", default="postgresql+asyncpg://le_sesame_user:le_sesame_password@localhost:5432/le_sesame"),
        alias="DATABASE_URL"
    )
    
    # JWT
    jwt_secret: str = Field(default="change-me-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "security", "jwt", "algorithm", default="HS256"),
        alias="JWT_ALGORITHM"
    )
    jwt_expiration_hours: int = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "security", "jwt", "expiration_hours", default=24),
        alias="JWT_EXPIRATION_HOURS"
    )
    
    # LLM Configuration
    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_endpoint_url: str = Field(default="", alias="OPENAI_ENDPOINT_URL")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    aws_access_key_id: str = Field(default="", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", alias="AWS_SECRET_ACCESS_KEY")
    aws_region_name: str = Field(default="us-east-1", alias="AWS_REGION_NAME")
    llm_provider: str = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "llm", "provider", default="mistral"),
        alias="LLM_PROVIDER"
    )
    llm_model: str = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "llm", "model", default="mistral-small-latest"),
        alias="LLM_MODEL"
    )
    llm_temperature: float = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "llm", "temperature", default=0.7),
        alias="LLM_TEMPERATURE"
    )
    llm_max_tokens: int = Field(
        default_factory=lambda: get_yaml_value(_yaml_config, "llm", "max_tokens", default=1024),
        alias="LLM_MAX_TOKENS"
    )
    
    # Game Configuration
    default_secret: str = Field(default="GOLDEN_KEY_2024", alias="DEFAULT_SECRET")
    default_passphrase: str = Field(default="open sesame", alias="DEFAULT_PASSPHRASE")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # CORS
    cors_origins: str = Field(
        default='["http://localhost:3000"]',
        alias="CORS_ORIGINS"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string or YAML config."""
        try:
            return json.loads(self.cors_origins)
        except json.JSONDecodeError:
            # Try to get from YAML
            yaml_origins = get_yaml_value(_yaml_config, "security", "cors", "allowed_origins")
            if yaml_origins and isinstance(yaml_origins, list):
                return yaml_origins
            return ["http://localhost:3000"]
    
    @property
    def game_levels_config(self) -> Dict[str, Any]:
        """Get game level configuration from YAML."""
        return get_yaml_value(_yaml_config, "game", "levels", default={})
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance for convenience
settings = get_settings()
