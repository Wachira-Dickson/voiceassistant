from app.speech.text_to_speech import TextToSpeech

def main():
    speaker = TextToSpeech()
    speaker.speak(
        "Hello. Your voice assistant can now speak text aloud offline."
    )
    print("Text-to-speech test completed.")

if __name__ == "__main__":
    main()