import requests
import json
import logging
from pathlib import Path
from src.utils.config_manager import ConfigManager

class FontManager:
    """Manages Google Fonts downloading and listing."""

    def __init__(self):
        self.config = ConfigManager()
        self.logger = logging.getLogger("FontManager")
        self.api_key = self.config.get("api_keys", "google_fonts_api_key")
        self.fonts_dir = Path(self.config.get("paths", "fonts_dir"))
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        self.fonts_list = []

    def fetch_fonts_list(self):
        """Fetches the list of available Google Fonts."""
        if not self.api_key:
            self.logger.warning("Google Fonts API Key missing. Using cached or empty list.")
            return []

        url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={self.api_key}&sort=popularity"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.fonts_list = data.get("items", [])
                self.logger.info(f"Fetched {len(self.fonts_list)} fonts.")
                return self.fonts_list
            else:
                self.logger.error(f"Failed to fetch fonts: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching fonts list: {e}")
            return []

    def download_font(self, font_name, variant="regular"):
        """Downloads the specified font."""
        font_data = next((f for f in self.fonts_list if f["family"] == font_name), None)
        if not font_data:
            self.logger.error(f"Font {font_name} not found in list.")
            return None

        file_url = font_data["files"].get(variant)
        if not file_url:
            # Fallback to first available variant
            file_url = list(font_data["files"].values())[0]

        try:
            response = requests.get(file_url)
            if response.status_code == 200:
                # Determine extension (usually ttf)
                ext = file_url.split('.')[-1]
                filename = f"{font_name.replace(' ', '_')}-{variant}.{ext}"
                save_path = self.fonts_dir / filename

                with open(save_path, 'wb') as f:
                    f.write(response.content)

                self.logger.info(f"Downloaded font to {save_path}")
                return str(save_path)
            else:
                self.logger.error(f"Failed to download font file: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error downloading font: {e}")
            return None

    def list_local_fonts(self):
        """Lists fonts already downloaded."""
        return [f.name for f in self.fonts_dir.glob("*.[to]tf")]
