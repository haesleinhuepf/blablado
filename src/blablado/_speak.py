

def speak_out(text, voice='nova'):
    """
    Speak out a string using Google Text To Speech
    """
    from pydub import AudioSegment
    from pydub.playback import play
    import os
    from openai import OpenAI
    client = OpenAI()

    # Convert text to audio
    temp_filename = "temp_audio.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    response.stream_to_file(temp_filename)

    # Load audio into pydub
    audio_segment = AudioSegment.from_mp3(temp_filename)

    silence = AudioSegment.silent(duration=1000)  # a bit of silence

    audio_with_silence = silence + audio_segment

    # Remove the temporary file
    os.remove(temp_filename)

    # Play audio
    play(audio_with_silence)