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
        default="postgresql+asyncpg://le_sesame_user:le_sesame_password@localhost:5432/le_sesame",
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

    # Google OAuth
    google_oauth_client_id: str = Field(default="", alias="GOOGLE_OAUTH_CLIENT_ID")

    # reCAPTCHA v3
    recaptcha_secret_key: str = Field(default="", alias="RECAPTCHA_SECRET_KEY")
    recaptcha_score_threshold: float = Field(default=0.5, alias="RECAPTCHA_SCORE_THRESHOLD")
    recaptcha_bypass_token: str = Field(default="", alias="RECAPTCHA_BYPASS_TOKEN")

    # SMTP for email verification
    smtp_host: str = Field(default="", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="noreply@lesesame.eu", alias="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="Le Sésame", alias="SMTP_FROM_NAME")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    smtp_use_ssl: bool = Field(default=False, alias="SMTP_USE_SSL")

    # Frontend URL (for email verification links)
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    
    # LLM Configuration
    mistral_api_key: str = Field(default="", alias="MISTRAL_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_endpoint_url: str = Field(default="", alias="OPENAI_ENDPOINT_URL")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    aws_access_key_id: str = Field(default="", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", alias="AWS_SECRET_ACCESS_KEY")
    aws_region_name: str = Field(default="us-east-1", alias="AWS_REGION_NAME")
    alibaba_api_key: str = Field(default="", alias="ALIBABA_API_KEY")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    vllm_api_key: str = Field(default="", alias="VLLM_API_KEY")
    together_api_key: str = Field(default="", alias="TOGETHER_API_KEY")
    xai_api_key: str = Field(default="", alias="XAI_API_KEY")
    cohere_api_key: str = Field(default="", alias="COHERE_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # LangSmith tracing
    langchain_tracing_v2: str = Field(default="false", alias="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field(default="le-sesame", alias="LANGCHAIN_PROJECT")
    langchain_api_key: str = Field(default="", alias="LANGCHAIN_API_KEY")
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com", alias="LANGCHAIN_ENDPOINT"
    )

    # LLM defaults (sourced from config.yaml only — NOT from .env)
    @property
    def llm_provider(self) -> str:
        return get_yaml_value(_yaml_config, "llm", "provider", default="mistral")

    @property
    def llm_model(self) -> str:
        return get_yaml_value(_yaml_config, "llm", "model", default="mistral-small-latest")

    @property
    def llm_temperature(self) -> float:
        return float(get_yaml_value(_yaml_config, "llm", "temperature", default=0.7))

    @property
    def llm_max_tokens(self) -> int:
        return int(get_yaml_value(_yaml_config, "llm", "max_tokens", default=1024))
    
    # CORS (sourced from config.yaml only — NOT from .env)
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS allowed origins from YAML config."""
        yaml_origins = get_yaml_value(_yaml_config, "security", "cors", "allowed_origins")
        if yaml_origins and isinstance(yaml_origins, list):
            return yaml_origins
        return ["http://localhost:3000"]
    
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
