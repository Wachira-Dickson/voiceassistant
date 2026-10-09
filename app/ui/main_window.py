from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFileDialog,
)

from app.audio.recorder import AudioRecorder
from app.audio.player import AudioPlayer

class VoiceAssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voice Assistant")
        self.setMinimumSize(700, 450)

        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        self.last_recording = None

        self.recordings_dir = (
            Path(__file__).resolve().parents[2]
            /"storage"
            /"recordings"
        )

        self.status_label = QLabel("Ready to record audio.")
        self.status_label.setWordWrap(True)

        self.record_button = QPushButton("Record Voice")
        self.stop_record_button = QPushButton("Stop Recording")
        self.play_button = QPushButton("Play Recording")
        self.stop_play_button = QPushButton("Stop Playback")

        self.stop_record_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.stop_play_button.setEnabled(False)

        self.record_button.clicked.connect(self.start_recording)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.play_button.clicked.connect(self.play_recording)
        self.stop_play_button.clicked.connect(self.stop_playback)

        title = QLabel("Voice Assistant")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )
        description = QLabel(
            "Phase 2: Microphone Recording and Audio Playback"
        )

        audio_layout = QHBoxLayout()
        audio_layout.addWidget(self.record_button)
        audio_layout.addWidget(self.stop_record_button)

        playback_layout = QHBoxLayout()
        playback_layout.addWidget(self.play_button)
        playback_layout.addWidget(self.stop_play_button)

        layout = QHBoxLayout()
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addLayout(audio_layout)
        layout.addLayout(playback_layout)
        layout.addSpacing(15)
        layout.addWidget(self.status_label)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_recording(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = (
            self.recordings_dir / f"recording_{timestamp}.wav"
        )

        try:
            self.player.stop()
            self.recorder.start_recording(output_path)

            self.record_button.setEnabled(False)
            self.stop_record_button.setEnabled(True)
            self.play_button.setEnabled(False)
            self.stop_play_button.setEnabled(False)

            self.status_label.settext(
                "Recording... Speak into your microphone,"
                "then press Stop Recording."
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Recording Error",
                f"Could not start recording:\n{error}",
            )
    
    def stop_recording(self):
        try:
            saved_path = self.recorder.stop_recording()

            if saved_path is not None and saved_path.exists():
                self.last_recording = saved_path
                self.play_button.setEnabled(True)

                self.status_label.setText(
                    f"Recording saved successfully:\n{saved_path}"
                )
            else: self.status_label.setText(
                "No recording was saved."
            )
                
        except Exception as error:
            QMessageBox.critical(
                self,
                "Recording Error",
                f"Could not stop recording cleanly:\n{error}",
            )
        
        finally:
            self.record_button.setEnabled(True)
            self.stop_record_button.setEnabled(False)

    def play_recording(self):
        audio_path = self.last_recording

        if audio_path is None or not audio_path.exists():
            selected_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select an audio recording",
                str(self.recording_dir),
                "WAV Audio (*.wav)",
            )

            if not selected_path:
                return
            
            audio_path = Path(selected_path)

        try:
            self.player.play(audio_path)
            self.stop_play_button.setEnabled(True)

            self.status_label.setText(
                f"Playing recording:\n{audio_path}"
            )

        except Exception as error:
            QMessageBox.critical(
                self, 
                "Playback Error",
                f"Could not play audio:\n{error}",
            )

    def stop_playback(self):
        self.playing.stop()
        self.stop_play_button.setEnabled(False)
        self.status_label.setText("Playback stopped.")

    def closeEvent(self, event):
        if self.recorder.is_recording:
            self.recorder.stop_recording()

        self.player.stop()
        event.accept()