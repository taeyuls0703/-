import time
import logging
from PyQt6.QtCore import QObject, pyqtSignal

class AutomationRunner(QObject):
    """Orchestrates the automation process based on the generated plan."""
    progress_update = pyqtSignal(str, int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, plan, flow_driver, whisk_driver, tts_engine):
        super().__init__()
        self.plan = plan
        self.flow_driver = flow_driver
        self.whisk_driver = whisk_driver
        self.tts_engine = tts_engine
        self.logger = logging.getLogger("AutomationRunner")
        self.should_stop = False

    def run(self):
        """Executes the automation plan."""
        scenes = self.plan.get("scenes", [])
        total_scenes = len(scenes)
        results = []

        self.logger.info(f"Starting automation for {total_scenes} scenes.")

        try:
            for i, scene in enumerate(scenes):
                if self.should_stop:
                    break

                scene_num = scene.get("scene_number", i+1)
                self.progress_update.emit(f"Processing Scene {scene_num}...", int((i / total_scenes) * 100))

                result = {"scene": scene_num}

                # 1. Generate Video
                visual_prompt = scene.get("visual_description")
                if visual_prompt:
                    self.logger.info(f"Generating video for Scene {scene_num}: {visual_prompt}")
                    video_path = self.flow_driver.generate_video(visual_prompt, f"scene_{scene_num}.mp4")
                    result["video_path"] = video_path

                # 2. Generate Audio
                audio_script = scene.get("audio_script")
                tts_style = scene.get("tts_style")
                if audio_script:
                    self.logger.info(f"Generating audio for Scene {scene_num}: {audio_script}")
                    audio_path = self.tts_engine.generate_speech(audio_script, f"scene_{scene_num}.wav", style_prompt=tts_style)
                    result["audio_path"] = audio_path

                # 3. Edit (Optional)
                edit_instr = scene.get("edit_instruction")
                if edit_instr and result.get("video_path"):
                     self.logger.info(f"Applying edit instructions: {edit_instr}")
                     edited_path = self.whisk_driver.edit_video(result["video_path"], edit_instr)
                     result["video_path"] = edited_path

                results.append(result)
                time.sleep(1) # Small pause

            self.progress_update.emit("Automation Complete!", 100)
            self.finished.emit(results)

        except Exception as e:
            self.logger.error(f"Automation failed: {e}")
            self.error.emit(str(e))

    def stop(self):
        self.should_stop = True
