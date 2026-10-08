import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class VoiceAssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voice Assistant")
        self.setMinimumSize(800, 500)

        label = QLabel("Voice Assistant is starting...", self)
        label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                padding: 20px;                        
            }
        """)

        self.setCentralWidget(label)


def main():
    app = QApplication(sys.argv)

    window = VoiceAssistantWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()