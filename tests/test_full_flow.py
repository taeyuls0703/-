import unittest
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.ai import AIEngine
from src.automation import BrowserManager, FlowDriver, WhiskDriver
from src.tts import TTSEngine
from src.utils.config_manager import ConfigManager

class TestFullFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = ConfigManager()
        repo_root = Path(os.getcwd())
        cls.flow_path = repo_root / "assets/html/Flow.html"
        cls.whisk_path = repo_root / "assets/html/Whisk.tml"

        (repo_root / "assets/outputs/audio").mkdir(parents=True, exist_ok=True)
        (repo_root / "assets/outputs/video").mkdir(parents=True, exist_ok=True)
        (repo_root / "assets/models/qwen3_tts").mkdir(parents=True, exist_ok=True)

        cls.config.set("paths", "flow_html", str(cls.flow_path))
        cls.config.set("paths", "whisk_html", str(cls.whisk_path))
        cls.config.set("automation", "headless", True)

    @patch('src.automation.browser_manager.ChromiumPage')
    def test_automation_runner(self, MockPage):
        # Setup Mock Page
        mock_page_instance = MockPage.return_value

        # Mock Element
        mock_element = MagicMock()
        mock_element.attr.return_value = "https://example.com/video.mp4" # For download link

        # Configure Mock Page behavior
        # When finding inputs/buttons, return mock_element
        mock_page_instance.ele.return_value = mock_element

        # Initialize BrowserManager with mocked page
        browser_manager = BrowserManager(headless=True)
        # Force the mock page into the manager (in case init created a new one before patch or failed)
        browser_manager.page = mock_page_instance

        flow_driver = FlowDriver(browser_manager)
        whisk_driver = WhiskDriver(browser_manager)
        tts_engine = TTSEngine()

        # Test Flow Driver
        print("Testing Flow Driver (Mocked)...")
        video_url = flow_driver.generate_video("A cat flying in space")

        # Verify interactions
        mock_page_instance.ele.assert_any_call("#prompt-input")
        mock_page_instance.ele.assert_any_call("#generate-btn")

        # Since we mocked the download button return, it should work
        self.assertIsNotNone(video_url)
        self.assertEqual(video_url, "https://example.com/video.mp4")

        # Test TTS (Mocking internal model loading which we simulated)
        print("Testing TTS Engine...")
        # Force model to be "loaded"
        tts_engine.model = True
        audio_path = tts_engine.generate_speech("Look at that cat go!", "test_audio.wav")
        self.assertTrue(os.path.exists(audio_path))

        # Test Whisk Driver
        print("Testing Whisk Driver (Mocked)...")
        mock_element.attr.return_value = "https://example.com/edited_image.jpg"

        dummy_video = Path("assets/outputs/dummy_video.mp4")
        with open(dummy_video, 'w') as f: f.write("dummy")

        edited_url = whisk_driver.edit_image(str(dummy_video), "Add sparkle effect")
        self.assertEqual(edited_url, "https://example.com/edited_image.jpg")

        browser_manager.quit()

if __name__ == '__main__':
    unittest.main()
