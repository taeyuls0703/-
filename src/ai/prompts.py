# Prompts for AI Generation

SCRIPT_GENERATION_PROMPT = """
You are a professional YouTube Shorts scriptwriter and director.
Create a detailed plan for a short video based on the following input: "{input_text}"

The output must be a valid JSON object with the following structure:
{{
    "title": "Video Title",
    "description": "Video Description",
    "scenes": [
        {{
            "scene_number": 1,
            "visual_description": "Detailed description of the visual for this scene (e.g., 'A futuristic city skyline at sunset')",
            "audio_script": "The spoken text for the voiceover.",
            "duration_seconds": 5,
            "keywords": ["futuristic", "city", "sunset"],
            "edit_instruction": "Optional: Specific editing instructions for this scene (e.g., 'Apply vintage filter', 'Add text: New Tech')"
        }},
        ...
    ],
    "background_music_mood": "Upbeat/Calm/Dramatic"
}}

Ensure the total duration is under 60 seconds.
Make the visual descriptions vivid and suitable for AI video generation tools.
Keep the audio script concise and engaging.
"""

EDIT_INSTRUCTION_PROMPT = """
You are a video editor assistant. Based on the user's request: "{user_request}",
provide specific editing instructions for the following scene:
Scene: {scene_description}

Output a JSON object:
{{
    "action": "cut/filter/text_overlay",
    "parameters": {{
        "filter_name": "...",
        "text_content": "...",
        "start_time": "...",
        "end_time": "..."
    }}
}}
"""

TTS_STYLE_PROMPT = """
Analyze the following text and suggest a speaking style and emotion for the TTS engine.
Text: "{text}"

Output a JSON object:
{{
    "emotion": "Happy/Sad/Excited/Serious/Whisper",
    "speed": "Fast/Slow/Normal",
    "pitch": "High/Low/Normal"
}}
"""
