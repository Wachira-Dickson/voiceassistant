from pathlib import Path

import sounddevice as sd
import soundfile as sf

class AudioRecorder:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self.audio_file = None
        self.is_recording = False
        self.output_path = None

    def _record_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}")

        if self.audio_file is not None:
            self.audio_file.write(indata)

    def start_recording(self, output_path):
        if self.is_recording:
            raise RuntimeError("Recording is already in progress.")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self.audio_file = sf.SoundFile(
                str(output_path),
                mode="w",
                samplerate=self.sample_rate,
                channels=self.channels,
                subtype="PCM_16",
            )

            self.output_path = output_path

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                callback=self._record_callback,
            )

            self.stream.start()
            self.is_recording = True

        except Exception:
            if self.stream is not None:
                self.stream.close()
                self.stream = None

            if self.audio_file is not None:
                self.audio_file.close()
                self.audio_file = None

            raise

    def stop_recording(self):
        if not self.is_recording:
            return None
        
        try:
            self.stream.stop()
            self.stream.close()

        finally:
            self.stream = None
            self.is_recording = False

            if self.audio_file is not None:
                self.audio_file.close()
                self.audio_file = None

        return self.output_path