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
from app.documents.reader import DocumentReader
from app.speech.text_to_speech import TextToSpeech

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

class SpeechWorker(QThread):
    completed = Signal()
    failed = Signal(str)

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.speaker = None

    def run(self):
        try:
            self.speaker = TextToSpeech()
            self.speaker.speak(self.text)
            self.completed.emit()
        except Exception as error:
            self.failed.emit(str(error))

    def stop_speaking(self):
        if self.speaker is not None:
            self.speaker.stop()

class VoiceAssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voice Assistant")
        self.setMinimumSize(750, 700)

        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        self.document_reader = DocumentReader()

        self.last_recording = None
        self.transcription_worker = None
        self.speech_worker = None
        self.document_text = ""

        project_dir = Path(__file__).resolve().parents[2]
        self.recordings_dir = project_dir / "storage" / "recordings"
        self.documents_dir = project_dir / "storage" / "documents"

        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

        title = QLabel("Voice Assistant")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        description = QLabel(
            "Record audio, transcribe speech, and listen to text documents."
        )
        description.setWordWrap(True)

        self.status_label = QLabel("Ready.")
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

        # Document controls
        self.open_document_button = QPushButton("Open Text File")
        self.read_aloud_button = QPushButton("Read Aoud")
        self.stop_speaking_button = QPushButton("Stop Speaking")

        self.read_aloud_button.setEnabled(False)
        self.stop_speaking_button.setEnabled(False)

        self.open_document_button.clicked.connect(self.open_document)
        self.read_aloud_button.clicked.connect(self.read_aloud)
        self.stop_speaking_button.clicked.connect(self.stop_speaking)

        document_controls = QHBoxLayout()
        document_controls.addWidget(self.open_document_button)
        document_controls.addWidget(self.read_aloud_button)
        document_controls.addWidget(self.stop_speaking_button)

        self.document_output = QTextEdit()
        self.document_output.setPlaceholderText(
            "Open a .txt document to display its contents here."
        )

        self.transcription_output = QTextEdit()
        self.transcription_output.setReadOnly(True)
        self.transcription_output.setPlaceholderText(
            "Your recognized speech will appear here..."
        )

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(10)

        layout.addWidget(QLabel("Audio Recording"))
        layout.addLayout(recording_layout)
        layout.addLayout(playback_layout)
        layout.addWidget(self.transcribe_button)

        layout.addSpacing(10)
        layout.addWidget(QLabel("Document Reader"))
        layout.addLayout(document_controls)
        layout.addWidget(self.document_output, 2)

        layout.addWidget(QLabel("Recognized Speech"))
        layout.addWidget(self.transcription_output, 1)
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
                str(error)
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
            else:
                self.status_label.setText(
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
        
        if self.transcription_worker is not None:
            if self.transcription_worker.isRunning():
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

        worker = TranscriptionWorker(audio_path)

        worker.completed.connect(
            self.on_transcription_completed
        )
        worker.failed.connect(
            self.on_transcription_failed
        )
        worker.finished.connect(
            self.on_transcription_finished
        )
        worker.start()

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
            or self.recordings_dir.exists()
        )
        self.transcription_worker = None

    def open_document(self):
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open a text document",
            str(self.documents_dir),
            "Text Files (*.txt)",
        )

        if not selected_path:
            return
        
        try:
            text = self.document_reader.read(selected_path)

            self.document_text = text
            self.document_output.setPlainText(text)
            self.read_aloud_button.setEnabled(bool(text.strip()))
            self.status_label.setText(
                f"Document loaded: {Path(selected_path).name}"
            )

        except Exception as error:
            QMessageBox.critical(self, "Document Error", str(error))

    def read_aloud(self):
        if self.speech_worker is not None:
            if self.speech_worker.isRunning():
                return
            
        text = self.document_output.toPlainText().strip()
        print("DEBUG: Text length:", len(text))
        print("DEBUG: Text preview:", repr(text[:100]))

        if not text:
            QMessageBox.information(
                self, "No Text", "Open a text document first."
            )
            return
        
        self.read_aloud_button.setEnabled(False)
        self.stop_speaking_button.setEnabled(True)
        self.status_label.setText("Reading document aloud...")

        worker = SpeechWorker(text)
        self.speech_worker = worker

        worker.completed.connect(self.on_speech_completed)
        worker.failed.connect(self.on_speech_failed)
        worker.finished.connect(self.on_speech_finished)
        worker.start()

    def stop_speaking(self):
        if self.speech_worker is not None:
            self.speech_worker.stop_speaking()
            self.status_label.setText("Stopping speech....")

    def on_speech_completed(self):
        self.status_label.setText("Finished reading document.")

    def on_speech_failed(self, error):
        self.status_label.setText("Speech failed.")
        QMessageBox.critical(self, "Text-to-Speech Error", error)

    def on_speech_finished(self):
        self.read_aloud_button.setEnabled(
            bool(self.document_output.toPlainText().strip())
        )
        self.stop_speaking_button.setEnabled(False)
        self.speech_worker = None


    def closeEvent(self, event):
        for worker in (
            self.transcription_worker,
            self.speech_worker,
        ):
            if worker is not None and worker.isRunning():
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