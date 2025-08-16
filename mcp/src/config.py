"""
Configuration management module for the MCP server.

This module handles loading and validating configuration from multiple sources:
1. Environment variables (highest priority)
2. Configuration file (config.yaml)

The configuration supports multiple Searx hosts with automatic failover.
"""

import logging
import os
import random
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class SearxConfig(BaseModel):
    """
    Searx configuration model with validation.

    Attributes:
        searx_hosts: List of Searx instance URLs for load balancing and failover.
        timeout: Request timeout in seconds for Searx API calls.
        max_retries: Maximum number of retry attempts for failed requests.
        cache_enabled: Whether to enable request caching.
        cache_ttl: Default cache time-to-live in seconds.
        cache_memory_mb: Maximum memory cache size in MB.
        cache_disk_mb: Maximum disk cache size in MB.
    """

    searx_hosts: list[str] = Field(default_factory=list, description="List of Searx instance URLs")
    timeout: int = Field(default=10, ge=1, le=60, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum number of retry attempts")
    cache_enabled: bool = Field(default=True, description="Enable request caching")
    cache_ttl: int = Field(
        default=3600, ge=60, le=86400, description="Cache TTL in seconds (1 minute to 24 hours)"
    )
    cache_memory_mb: int = Field(
        default=50, ge=10, le=500, description="Maximum memory cache size in MB"
    )
    cache_disk_mb: int = Field(
        default=200, ge=0, le=5000, description="Maximum disk cache size in MB"
    )

    @field_validator("searx_hosts", mode="before")
    @classmethod
    def validate_searx_hosts(cls, v):
        """Ensure searx_hosts is a non-empty list of valid URLs."""
        if isinstance(v, str):
            # Support comma-separated string from environment variable
            v = [host.strip() for host in v.split(",") if host.strip()]

        if not v:
            raise ValueError("At least one Searx host must be configured")

        # Validate URL format
        for host in v:
            if not host.startswith(("http://", "https://")):
                raise ValueError(f"Invalid URL format: {host}")
            # Remove trailing slashes for consistency
            if host.endswith("/"):
                host = host[:-1]

        return v

    @model_validator(mode="after")
    def validate_model(self):
        """Perform cross-field validation."""
        # Remove duplicates while preserving order
        seen = set()
        unique_hosts = []
        for host in self.searx_hosts:
            normalized = host.rstrip("/")
            if normalized not in seen:
                seen.add(normalized)
                unique_hosts.append(normalized)
        self.searx_hosts = unique_hosts

        logging.debug(
            "Configured %d unique Searx host(s): %s",
            len(self.searx_hosts),
            ", ".join(self.searx_hosts),
        )
        return self

    def get_random_host(self) -> str:
        """
        Get a random Searx host from the configured list.

        This provides simple load balancing across multiple instances.

        Returns:
            str: A randomly selected Searx host URL.
        """
        return random.choice(self.searx_hosts)

    def get_all_hosts(self) -> list[str]:
        """
        Get all configured Searx hosts in order.

        Useful for implementing retry logic with different hosts.

        Returns:
            List[str]: All configured Searx host URLs.
        """
        return self.searx_hosts.copy()


class Config(BaseModel):
    """
    Main configuration model for the MCP server.

    This class orchestrates loading configuration from multiple sources
    and provides a unified interface for accessing configuration values.
    """

    searx: SearxConfig = Field(
        default_factory=SearxConfig, description="Searx search engine configuration"
    )

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Config":
        """
        Load configuration from environment variables and/or config file.

        Priority order (highest to lowest):
        1. Environment variables
        2. Configuration file (config.yaml)
        3. Default values

        Args:
            config_path: Optional path to configuration file.
                        Defaults to 'config.yaml' in the project root.

        Returns:
            Config: Loaded and validated configuration instance.

        Raises:
            ValueError: If configuration is invalid.
            FileNotFoundError: If specified config file doesn't exist.
        """
        config_data = {}

        # Load from config file if it exists
        if config_path is None:
            config_path = Path("config.yaml")

        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    file_config = yaml.safe_load(f) or {}

                    # Build searx config from file
                    searx_config = {}
                    if "searx_hosts" in file_config:
                        searx_config["searx_hosts"] = file_config["searx_hosts"]
                    if "cache_ttl" in file_config:
                        searx_config["cache_ttl"] = file_config["cache_ttl"]
                    if "cache_enabled" in file_config:
                        searx_config["cache_enabled"] = file_config["cache_enabled"]
                    if "cache_memory_mb" in file_config:
                        searx_config["cache_memory_mb"] = file_config["cache_memory_mb"]
                    if "cache_disk_mb" in file_config:
                        searx_config["cache_disk_mb"] = file_config["cache_disk_mb"]

                    if searx_config:
                        config_data["searx"] = searx_config

                    logging.info("Loaded configuration from %s", config_path)
            except yaml.YAMLError as e:
                logging.error("Failed to parse configuration file: %s", e)
                raise ValueError(f"Invalid YAML in configuration file: {e}")
        else:
            logging.debug("Configuration file %s not found, using defaults", config_path)

        # Override with environment variables (highest priority)
        env_hosts = os.getenv("SEARX_HOSTS")
        if env_hosts:
            if "searx" not in config_data:
                config_data["searx"] = {}
            config_data["searx"]["searx_hosts"] = env_hosts
            logging.info("Overriding Searx hosts from environment variable")

        # Load timeout and retry settings from environment
        env_timeout = os.getenv("SEARX_TIMEOUT")
        if env_timeout:
            try:
                if "searx" not in config_data:
                    config_data["searx"] = {}
                config_data["searx"]["timeout"] = int(env_timeout)
            except ValueError:
                logging.warning("Invalid SEARX_TIMEOUT value: %s", env_timeout)

        env_retries = os.getenv("SEARX_MAX_RETRIES")
        if env_retries:
            try:
                if "searx" not in config_data:
                    config_data["searx"] = {}
                config_data["searx"]["max_retries"] = int(env_retries)
            except ValueError:
                logging.warning("Invalid SEARX_MAX_RETRIES value: %s", env_retries)

        # Load cache settings from environment (highest priority)
        env_cache_ttl = os.getenv("SEARX_CACHE_TTL")
        if env_cache_ttl:
            try:
                if "searx" not in config_data:
                    config_data["searx"] = {}
                config_data["searx"]["cache_ttl"] = int(env_cache_ttl)
                logging.info("Cache TTL set to %s seconds from environment", env_cache_ttl)
            except ValueError:
                logging.warning("Invalid SEARX_CACHE_TTL value: %s", env_cache_ttl)

        env_cache_enabled = os.getenv("SEARX_CACHE_ENABLED")
        if env_cache_enabled:
            if "searx" not in config_data:
                config_data["searx"] = {}
            config_data["searx"]["cache_enabled"] = env_cache_enabled.lower() in (
                "true",
                "1",
                "yes",
                "on",
            )
            logging.info(
                "Cache %s from environment",
                "enabled" if config_data["searx"]["cache_enabled"] else "disabled",
            )

        env_cache_memory = os.getenv("SEARX_CACHE_MEMORY_MB")
        if env_cache_memory:
            try:
                if "searx" not in config_data:
                    config_data["searx"] = {}
                config_data["searx"]["cache_memory_mb"] = int(env_cache_memory)
            except ValueError:
                logging.warning("Invalid SEARX_CACHE_MEMORY_MB value: %s", env_cache_memory)

        env_cache_disk = os.getenv("SEARX_CACHE_DISK_MB")
        if env_cache_disk:
            try:
                if "searx" not in config_data:
                    config_data["searx"] = {}
                config_data["searx"]["cache_disk_mb"] = int(env_cache_disk)
            except ValueError:
                logging.warning("Invalid SEARX_CACHE_DISK_MB value: %s", env_cache_disk)

        # Create and validate configuration
        try:
            config = cls(**config_data)
            logging.info(
                "Configuration loaded successfully with %d Searx host(s)",
                len(config.searx.searx_hosts) if config.searx.searx_hosts else 0,
            )
            return config
        except Exception as e:
            logging.error("Configuration validation failed: %s", e)
            raise


# Global configuration instance (lazy-loaded)
_config: Config | None = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    This function implements lazy loading and caching of the configuration.
    The configuration is loaded only once on first access.

    Returns:
        Config: The global configuration instance.

    Raises:
        ValueError: If configuration is invalid.
    """
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config(config_path: Path | None = None) -> Config:
    """
    Force reload the configuration from sources.

    This is useful for testing or when configuration might have changed.

    Args:
        config_path: Optional path to configuration file.

    Returns:
        Config: Newly loaded configuration instance.
    """
    global _config
    _config = Config.load(config_path)
    return _config
