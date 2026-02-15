# AI Shorts Creator

A comprehensive tool for creating and managing YouTube Shorts using AI, automated editing, and local TTS.

## Features
- **AI Brain**: Powered by Gemini (via `bardapi`) for scriptwriting and scene planning.
- **Automation**: Uses `DrissionPage` to automate local HTML tools (`Flow.html`, `Whisk.tml`).
- **TTS**: Local Qwen3-TTS integration for voiceovers.
- **GUI**: User-friendly interface built with PyQt6.
- **Asset Management**: Automatic font downloading and media handling.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Place `Flow.html` and `Whisk.tml` in `assets/html/`.
3. Configure `config/settings.json` with your API keys and paths.
4. Run tests to verify setup: `python -m unittest tests/test_full_flow.py`
5. Run the application: `python src/main.py`
