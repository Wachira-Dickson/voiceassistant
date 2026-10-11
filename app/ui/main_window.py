from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFileDialog,
    QTextEdit,
)

from app.audio.recorder import AudioRecorder
from app.audio.player import AudioPlayer

class TranscriptionWorker(QThread):
    completed = Signal(str)
    failed = Signal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = str(audio_path)

    def run(self):
        try:
            from app.speech.speech_to_text import SpeechToText

            recognizer = SpeechToText(model_size="tiny.en")
            text = recognizer.transcribe_file(self.audio_path)
            self.completed.emit(text)

        except Exception as error:
            self.failed.emit(str(error))

class VoiceAssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voice Assistant")
        self.setMinimumSize(700, 600)

        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        self.last_recording = None
        self.transcription_worker = None

        self.recordings_dir = (
            Path(__file__).resolve().parents[2]
            /"storage"
            /"recordings"
        )

        title = QLabel("Voice Assistant")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        description = QLabel(
            "Phase 3: Offline Speech Recognition."
        )

        self.status_label = QLabel("Ready to record audio.")
        self.status_label.setWordWrap(True)

        self.record_button = QPushButton("Record Voice")
        self.stop_record_button = QPushButton("Stop Recording")
        self.play_button = QPushButton("Play Recording")
        self.stop_play_button = QPushButton("Stop Playback")
        self.transcribe_button = QPushButton("Transcribe Recording")

        self.stop_record_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.stop_play_button.setEnabled(False)
        self.transcribe_button.setEnabled(False)

        self.record_button.clicked.connect(self.start_recording)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.play_button.clicked.connect(self.play_recording)
        self.stop_play_button.clicked.connect(self.stop_playback)
        self.transcribe_button.clicked.connect( self.transcribe_recording )

        recording_layout = QHBoxLayout()
        recording_layout.addWidget(self.record_button)
        recording_layout.addWidget(self.stop_record_button)

        playback_layout = QHBoxLayout()
        playback_layout.addWidget(self.play_button)
        playback_layout.addWidget(self.stop_play_button)

        self.transcription_output = QTextEdit()
        self.transcription_output.setReadOnly(True)
        self.transcription_output.setPlaceholderText(
            "Your recognized speech will appear here..."
        )

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(12)
        layout.addLayout(recording_layout)
        layout.addLayout(playback_layout)
        layout.addWidget(self.transcribe_button)
        layout.addWidget(QLabel("Recognized Speech"))
        layout.addWidget(self.transcription_output)
        layout.addWidget(self.status_label)

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

            self.last_recording = None
            self.record_button.setEnabled(False)
            self.stop_record_button.setEnabled(True)
            self.play_button.setEnabled(False)
            self.stop_play_button.setEnabled(False)
            self.transcribe_button.setEnabled(False)

            self.status_label.setText(
                "Recording... Speak into your microphone,"
                "then press Stop Recording."
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Recording Error",
                str(error),
            )
    
    def stop_recording(self):
        try:
            saved_path = self.recorder.stop_recording()

            if saved_path is not None and saved_path.exists():
                self.last_recording = saved_path
                self.play_button.setEnabled(True)
                self.transcribe_button.setEnabled(True)

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
                str(error),
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
                str(self.recordings_dir),
                "WAV Audio (*.wav)",
            )

            if not selected_path:
                return
            
            audio_path = Path(selected_path)

        try:
            self.player.play(audio_path)
            self.stop_play_button.setEnabled(True)

            self.status_label.setText(
                f"Playing:\n{audio_path}"
            )

        except Exception as error:
            QMessageBox.critical(
                self, 
                "Playback Error",
                str(error),
            )

    def stop_playback(self):
        self.player.stop()
        self.stop_play_button.setEnabled(False)
        self.status_label.setText("Playback stopped.")

    def transcribe_recording(self):
        if self.recorder.is_recording:
            QMessageBox.warning(
                self,
                "Recording in Progress",
                "Stop recording before transcribing.",
            )
            return
        
        audio_path = self.last_recording

        if audio_path is None or not audio_path.exists():
            selected_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select a recording to transcribe",
                str(self.recordings_dir),
                "WAV Audio (*.wav)",
            )
            if not selected_path:
                return
            
            audio_path = Path(selected_path)

        self.transcribe_button.setEnabled(False)
        self.status_label.setText(
            "Loading the speech model and transcribing..."
            "The first run may take longer..."
        )
        self.transcription_output.clear()

        self.transcription_worker = TranscriptionWorker(audio_path)

        self.transcription_worker.completed.connect(
            self.on_transcription_completed
        )
        self.transcription_worker.failed.connect(
            self.on_transcription_failed
        )
        self.transcription_worker.finished.connect(
            self.on_transcription_finished
        )
        self.transcription_worker.start()

    def on_transcription_completed(self, text):
        self.transcription_output.setPlainText(
            text or "No speech was recognized."
        )

        self.status_label.setText(
            "Transcription completed."
        )

    def on_transcription_failed(self, error):
        self.status_label.setText("Transcription_failed.")
        QMessageBox.critical(
            self,
            "Transcription Error",
            error,
        )

    def on_transcription_finished(self):
        self.transcribe_button.setEnabled(
            self.last_recording is not None
            or self.recording_dir.exists()
        )
        self.transcription_worker = None

    def closeEvent(self, event):
        if self.transcription_worker is not None:
            if self.transcription_worker.isRunning():
                QMessageBox.warning(
                    self,
                    "Transcription in Progress",
                    "Wait for transcription to finish before closing.",
                )
                event.ignore()
                return

        if self.recorder.is_recording:
            self.recorder.stop_recording()

        self.player.stop()
        event.accept()