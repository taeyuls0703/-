import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QLineEdit, QFileDialog, QProgressBar, QMessageBox,
    QFormLayout, QGroupBox, QScrollArea, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.ai import AIEngine
from src.automation import BrowserManager, FlowDriver, WhiskDriver
from src.tts import TTSEngine
from src.utils import ConfigManager, FontManager

class WorkerThread(QThread):
    """Worker thread to run long-running tasks without freezing GUI."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.task_func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class SceneEditDialog(QDialog):
    def __init__(self, scene_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Scene")
        self.scene_data = scene_data.copy() # Work on a copy
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.visual_edit = QTextEdit()
        self.visual_edit.setPlainText(self.scene_data.get("visual_description", ""))
        self.visual_edit.setMaximumHeight(100)

        self.audio_edit = QTextEdit()
        self.audio_edit.setPlainText(self.scene_data.get("audio_script", ""))
        self.audio_edit.setMaximumHeight(100)

        self.edit_instr = QLineEdit()
        self.edit_instr.setText(self.scene_data.get("edit_instruction", ""))

        layout.addRow("Visual Description:", self.visual_edit)
        layout.addRow("Audio Script:", self.audio_edit)
        layout.addRow("Edit Instruction:", self.edit_instr)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        self.scene_data["visual_description"] = self.visual_edit.toPlainText()
        self.scene_data["audio_script"] = self.audio_edit.toPlainText()
        self.scene_data["edit_instruction"] = self.edit_instr.text()
        return self.scene_data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Shorts Creator - Ultimate Automation")
        self.resize(1200, 800)

        self.config = ConfigManager()
        self.logger = logging.getLogger("GUI")

        # Initialize Backend Modules
        self.ai_engine = AIEngine()
        self.browser_manager = BrowserManager(headless=self.config.get("automation", "headless", False))
        self.flow_driver = FlowDriver(self.browser_manager)
        self.whisk_driver = WhiskDriver(self.browser_manager)
        self.tts_engine = TTSEngine()
        self.font_manager = FontManager()

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.create_dashboard_tab()
        self.create_workspace_tab()
        self.create_settings_tab()

        # Status Bar
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()

    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        lbl = QLabel("Enter your video idea, topic, or link:")
        layout.addWidget(lbl)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("E.g., 'A suspenseful short about a detective in 2050 solving a cybercrime.'")
        layout.addWidget(self.input_text)

        btn_layout = QHBoxLayout()
        self.btn_plan = QPushButton("Generate Plan & Scripts")
        self.btn_plan.clicked.connect(self.generate_plan)
        btn_layout.addWidget(self.btn_plan)

        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, "Dashboard")

    def create_workspace_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Scenes List
        self.scene_list = QListWidget()
        layout.addWidget(self.scene_list)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_update_plan = QPushButton("Update Scene")
        self.btn_update_plan.clicked.connect(self.update_current_scene)

        self.btn_execute = QPushButton("Execute Full Automation")
        self.btn_execute.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_execute.clicked.connect(self.execute_automation)

        btn_layout.addWidget(self.btn_update_plan)
        btn_layout.addWidget(self.btn_execute)
        layout.addLayout(btn_layout)

        # Logs area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        layout.addWidget(self.log_output)

        self.tabs.addTab(tab, "Workspace")

    def create_settings_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.path_flow = QLineEdit(self.config.get("paths", "flow_html"))
        self.path_whisk = QLineEdit(self.config.get("paths", "whisk_html"))
        self.path_model = QLineEdit(self.config.get("paths", "qwen_tts_model"))
        self.key_gemini = QLineEdit(self.config.get("api_keys", "gemini_api_key"))
        self.key_gemini.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Flow.html Path:", self.path_flow)
        layout.addRow("Whisk.tml Path:", self.path_whisk)
        layout.addRow("TTS Model Path:", self.path_model)
        layout.addRow("Gemini API Key:", self.key_gemini)

        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        layout.addRow(btn_save)

        # Session Management
        group_session = QGroupBox("Session Management")
        session_layout = QVBoxLayout()
        btn_login = QPushButton("Open Browser for Login")
        btn_login.clicked.connect(self.open_login_browser)
        btn_save_sess = QPushButton("Save Current Session")
        btn_save_sess.clicked.connect(self.save_session)
        session_layout.addWidget(btn_login)
        session_layout.addWidget(btn_save_sess)
        group_session.setLayout(session_layout)

        layout.addRow(group_session)

        self.tabs.addTab(tab, "Settings")

    # --- Logic ---

    def log(self, message):
        self.log_output.append(message)
        self.logger.info(message)
        self.status_bar.showMessage(message)

    def generate_plan(self):
        input_text = self.input_text.toPlainText()
        if not input_text:
            QMessageBox.warning(self, "Input Error", "Please enter some text.")
            return

        self.log("Generating plan... Please wait.")
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0) # Indeterminate

        self.worker = WorkerThread(self.ai_engine.generate_plan, input_text)
        self.worker.finished.connect(self.on_plan_generated)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_plan_generated(self, plan):
        self.progress_bar.hide()
        if not plan:
            QMessageBox.critical(self, "Error", "Failed to generate plan.")
            return

        self.current_plan = plan
        self.scene_list.clear()

        scenes = plan.get("scenes", [])
        for scene in scenes:
            item_text = f"Scene {scene.get('scene_number')}: {scene.get('visual_description')[:50]}..."
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, scene)
            self.scene_list.addItem(item)

        self.log(f"Plan generated with {len(scenes)} scenes.")
        self.tabs.setCurrentIndex(1) # Switch to Workspace

    def update_current_scene(self):
        item = self.scene_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Error", "Please select a scene to edit.")
            return

        scene_data = item.data(Qt.ItemDataRole.UserRole)
        dialog = SceneEditDialog(scene_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            item.setData(Qt.ItemDataRole.UserRole, new_data)
            # Update display text
            item.setText(f"Scene {new_data.get('scene_number')}: {new_data.get('visual_description')[:50]}...")

            # Update the plan in config/memory
            # Find and update in self.current_plan
            for i, scene in enumerate(self.current_plan.get("scenes", [])):
                if scene.get("scene_number") == new_data.get("scene_number"):
                    self.current_plan["scenes"][i] = new_data
                    break
            self.log(f"Scene {new_data.get('scene_number')} updated.")

    def execute_automation(self):
        if not hasattr(self, 'current_plan') or not self.current_plan:
            QMessageBox.warning(self, "Error", "No plan generated yet.")
            return

        self.log("Starting automation sequence...")
        self.progress_bar.show()
        self.btn_execute.setEnabled(False)

        # Setup Automation Runner in a Thread
        self.automation_thread = QThread()
        self.runner = AutomationRunner(
            self.current_plan,
            self.flow_driver,
            self.whisk_driver,
            self.tts_engine
        )
        self.runner.moveToThread(self.automation_thread)

        # Connect Signals
        self.automation_thread.started.connect(self.runner.run)
        self.runner.progress_update.connect(self.on_progress)
        self.runner.finished.connect(self.on_automation_finished)
        self.runner.error.connect(self.on_error)
        self.runner.finished.connect(self.automation_thread.quit)
        self.runner.finished.connect(self.runner.deleteLater)
        self.automation_thread.finished.connect(self.automation_thread.deleteLater)

        self.automation_thread.start()

    def on_progress(self, message, progress):
        self.log(message)
        self.progress_bar.setValue(progress)

    def on_automation_finished(self, results):
        self.log("Automation Finished Successfully!")
        self.progress_bar.hide()
        self.btn_execute.setEnabled(True)
        # Here we could display results or open folder
        if results:
            QMessageBox.information(self, "Success", f"Generated {len(results)} scenes.")

    def save_settings(self):
        self.config.set("paths", "flow_html", self.path_flow.text())
        self.config.set("paths", "whisk_html", self.path_whisk.text())
        self.config.set("paths", "qwen_tts_model", self.path_model.text())
        self.config.set("api_keys", "gemini_api_key", self.key_gemini.text())
        self.log("Settings saved.")

    def open_login_browser(self):
        self.browser_manager.load_url("https://accounts.google.com") # Or relevant URL
        self.log("Browser opened for login. Please log in manually.")

    def save_session(self):
        self.browser_manager.save_session("user_session")
        self.log("Session saved.")

    def on_error(self, error_msg):
        self.progress_bar.hide()
        QMessageBox.critical(self, "Error", error_msg)
        self.log(f"Error: {error_msg}")

    def closeEvent(self, event):
        self.browser_manager.quit()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
