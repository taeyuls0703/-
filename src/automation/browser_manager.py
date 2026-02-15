import json
import time
from pathlib import Path
from DrissionPage import ChromiumPage, ChromiumOptions
from src.utils.config_manager import ConfigManager
import logging

class BrowserManager:
    """Manages the browser instance using DrissionPage."""

    def __init__(self, headless=False):
        self.config = ConfigManager()
        self.logger = logging.getLogger("BrowserManager")
        self.headless = headless
        self.page = None
        self._initialize_browser()

    def _initialize_browser(self):
        """Initializes the ChromiumPage with options."""
        co = ChromiumOptions()
        if self.headless:
            co.headless(True)

        # Add user agent to avoid detection (basic)
        co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        try:
            self.page = ChromiumPage(co)
            self.logger.info("Browser initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")

    def load_url(self, url):
        """Navigates to the specified URL."""
        if self.page:
            try:
                self.page.get(url)
                self.logger.info(f"Loaded URL: {url}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to load URL {url}: {e}")
                return False
        return False

    def load_local_html(self, file_path):
        """Loads a local HTML file."""
        path = Path(file_path).resolve()
        if not path.exists():
            self.logger.error(f"Local file not found: {path}")
            return False

        url = f"file:///{path}"
        return self.load_url(url)

    def save_session(self, name="default"):
        """Saves cookies and local storage to a file."""
        if not self.page:
            return

        session_data = {
            "cookies": self.page.cookies(as_dict=True),
            "local_storage": self.page.run_js("return {...localStorage};"),
            "session_storage": self.page.run_js("return {...sessionStorage};")
        }

        path = Path(self.config.get("paths", "output_dir")) / f"sessions/{name}_session.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4)
        self.logger.info(f"Session saved to {path}")

    def load_session(self, name="default"):
        """Loads cookies and local storage from a file."""
        path = Path(self.config.get("paths", "output_dir")) / f"sessions/{name}_session.json"
        if not path.exists():
            self.logger.warning(f"Session file not found: {path}")
            return False

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if self.page:
                # Set cookies
                # DrissionPage set_cookies expects list of dicts or dict
                self.page.set.cookies(data.get("cookies", {}))

                # Set local storage
                for k, v in data.get("local_storage", {}).items():
                    self.page.run_js(f"localStorage.setItem('{k}', '{v}');")

                # Set session storage
                for k, v in data.get("session_storage", {}).items():
                    self.page.run_js(f"sessionStorage.setItem('{k}', '{v}');")

                self.logger.info(f"Session loaded from {path}")
                # Refresh to apply changes
                self.page.refresh()
                return True
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
            return False

    def analyze_page_structure(self):
        """ specialized method to print DOM structure for debugging."""
        if self.page:
            html = self.page.html
            self.logger.info(f"Page Title: {self.page.title}")
            # Identify inputs and buttons
            inputs = self.page.eles('tag:input')
            buttons = self.page.eles('tag:button')
            self.logger.info(f"Found {len(inputs)} inputs and {len(buttons)} buttons.")
            for i, inp in enumerate(inputs[:5]): # Show first 5
                self.logger.info(f"Input {i}: id={inp.attr('id')}, name={inp.attr('name')}, class={inp.attr('class')}")
            for i, btn in enumerate(buttons[:5]):
                self.logger.info(f"Button {i}: text={btn.text}, id={btn.attr('id')}, class={btn.attr('class')}")
            return html
        return ""

    def quit(self):
        if self.page:
            self.page.quit()
