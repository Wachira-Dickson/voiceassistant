from pathlib import Path

import sounddevice as sd
import soundfile as sf

class AudioPlayer:
    def __init__(self):
        self.is_playing = False

    def play(self, audio_path):
        audio_path = Path(audio_path)

        if not audio_path.is_file():
            raise FileNotFoundError(
                f"Recording not found: {audio_path}"
            )
        
        #Stop any audio that is already playing.
        sd.stop()
        self.is_playing = False

        #Load the WAV file into memory.
        audio_data, sample_rate = sf.read(
            str(audio_path),
            dtype="float32",
        )

        #Start playback without blocking the GUI.
        sd.play(audio_data, sample_rate)
        self.is_playing = True

    def stop(self):
        sd.stop()
        self.is_playing = False