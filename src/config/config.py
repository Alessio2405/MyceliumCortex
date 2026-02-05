"""Configuration management."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration."""

    DEFAULT_CONFIG = {
        "llm": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "api_key": "",  # Will be read from environment
        },
        "system": {
            "log_level": "INFO",
            "max_memory_per_conversation": 10,  # Number of messages to keep in context
        },
        "tools": {
            "shell": {"enabled": True},
            "file": {"enabled": True},
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_path = config_path or self._get_default_path()
        self.config = self._load_config()

    def _get_default_path(self) -> str:
        """Get default config path."""
        home = Path.home()
        config_dir = home / ".miniclaw"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.json")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                return self.DEFAULT_CONFIG.copy()

        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """Save configuration to file."""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

    def set(self, key: str, value: Any):
        """Set configuration value by dot-notation key."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
