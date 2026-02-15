import sys
from src.utils.logger import setup_logging
from src.gui.main_window import MainWindow, QApplication

def main():
    setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
