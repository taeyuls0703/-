import json
import logging
from bardapi import Bard
from src.utils.config_manager import ConfigManager
from src.ai.prompts import SCRIPT_GENERATION_PROMPT, EDIT_INSTRUCTION_PROMPT, TTS_STYLE_PROMPT

class AIEngine:
    def __init__(self):
        self.config = ConfigManager()
        self.logger = logging.getLogger("AIEngine")
        self.token = self.config.get("api_keys", "gemini_api_key")
        self.bard = None
        self._initialize_bard()

    def _initialize_bard(self):
        """Initializes the Bard API client."""
        if self.token:
            try:
                # Assuming the token is the __Secure-1PSID cookie value
                self.bard = Bard(token=self.token)
                self.logger.info("Bard API initialized successfully.")
            except Exception as e:
                self.logger.error(f"Failed to initialize Bard API: {e}")
        else:
            self.logger.warning("Gemini API Key (Secure-1PSID) not found in configuration.")

    def generate_plan(self, input_text):
        """Generates a video plan from the input text."""
        if not self.bard:
            self.logger.error("Bard API is not initialized.")
            return None

        prompt = SCRIPT_GENERATION_PROMPT.format(input_text=input_text)
        try:
            self.logger.info(f"Sending prompt to AI: {prompt[:50]}...")
            response = self.bard.get_answer(prompt)['content']
            self.logger.info("Received response from AI.")
            return self._parse_json_response(response)
        except Exception as e:
            self.logger.error(f"Error generating plan: {e}")
            return None

    def generate_edit_instructions(self, user_request, scene_description):
        """Generates editing instructions based on user request."""
        if not self.bard:
             return None

        prompt = EDIT_INSTRUCTION_PROMPT.format(user_request=user_request, scene_description=scene_description)
        try:
            response = self.bard.get_answer(prompt)['content']
            return self._parse_json_response(response)
        except Exception as e:
            self.logger.error(f"Error generating edit instructions: {e}")
            return None

    def generate_tts_style(self, text):
        """Generates TTS style instructions."""
        if not self.bard:
            return None

        prompt = TTS_STYLE_PROMPT.format(text=text)
        try:
            response = self.bard.get_answer(prompt)['content']
            return self._parse_json_response(response)
        except Exception as e:
            self.logger.error(f"Error generating TTS style: {e}")
            return None

    def _parse_json_response(self, response_text):
        """Helper to extract JSON from AI response."""
        try:
            # Simple cleanup to find the first '{' and last '}'
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                self.logger.error("No JSON found in response.")
                return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON Decode Error: {e}\nResponse: {response_text}")
            return None
