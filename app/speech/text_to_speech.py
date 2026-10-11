import pyttsx3

class TextToSpeech:
    """Convert text into spoken audio using a local speech engine."""

    def __init__(self, rate=170, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)

    def speak(self, text):
        """Speak the supplied text and wait until speech finishes."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text to speak cannot be empty.")
        
        self.engine.say(text.strip())
        self.engine.runAndWait()

    def stop(self):
        """Stop speech currently being played."""
        self.engine.stop()
