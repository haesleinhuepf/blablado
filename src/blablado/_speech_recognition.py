def list_microphones():
    import speech_recognition as sr
    return sr.Microphone.list_microphone_names()


def listen_to_microphone(microphone_index=None, timeout=None):
    """Recognizes speech from microphone and return it as string"""
    import speech_recognition as sr

    microphone_name = list_microphones()[microphone_index]

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    with sr.Microphone(microphone_index) as source:
        # Reducing the noise
        recognizer.adjust_for_ambient_noise(source)
        print(f"Listening via {microphone_name} (timeout: {timeout})...")
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
        print("Processing...")

        try:
            # Recognize the content
            text = recognizer.recognize_google(audio)

        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError as e:
            print("Error calling the API; {0}".format(e))
            return None

        print("You said:", text)
        return text
