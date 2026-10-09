import sys

from PySide6.QtWidgets import QApplication
from app.ui.main_window import VoiceAssistantWindow


def main():
    app = QApplication(sys.argv)

    window = VoiceAssistantWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()