import json
import os
from pathlib import Path

class ConfigManager:
    """Manages application configuration, including paths and API keys."""

    _instance = None

    DEFAULT_CONFIG = {
        "paths": {
            "flow_html": "assets/html/Flow.html",
            "whisk_html": "assets/html/Whisk.tml",
            "qwen_tts_model": "assets/models/qwen3_tts",
            "output_dir": "assets/outputs",
            "fonts_dir": "assets/fonts"
        },
        "api_keys": {
            "gemini_api_key": "",
            "google_fonts_api_key": ""
        },
        "automation": {
            "headless": False,
            "browser_path": ""  # Default browser path if needed
        },
        "tts": {
            "voice_preset": "default"
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.config_path = Path("config/settings.json")
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        """Loads configuration from file or creates default if missing."""
        if not self.config_path.exists():
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
        else:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.config = {**self.DEFAULT_CONFIG, **loaded_config}
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                self.config = self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """Saves current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def get(self, section, key, default=None):
        """Retrieves a configuration value safely."""
        return self.config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """Sets a configuration value and saves."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

# Global instance for easy access
config_manager = ConfigManager()
