from pathlib import Path

from faster_whisper import WhisperModel

class SpeechToText:
    def __init__(self, model_size="tiny.en"):
        # Run speech recognition locally on the CPU.
        # int8 reduces memory usage on a modest laptop.
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            
        )
    
    def transcribe_file(self, audio_path):
        audio_path = Path(audio_path)
        
        if not audio_path.is_file():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )
        
        segments, info = self.model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True,
        )

        # Segments are generated lazily, so iterate over them
        # to complete transcription.
        text = "".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        return text
        