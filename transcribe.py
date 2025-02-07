from pydub import AudioSegment
import speech_recognition as sr
import os

def convert_to_wav(audio_path, wav_path):
    """
    Convert audio file (MP3, WebM, etc.) to WAV format with PCM encoding.
    """
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # Convert to mono, 16kHz
    audio.export(wav_path, format="wav")

def transcribe_audio(file_path):
    """
    Convert uploaded audio file (MP3/WebM) to WAV, then transcribe using Google's Speech API.
    """
    # Define WAV output path
    wav_path = file_path.rsplit(".", 1)[0] + ".wav"

    # Convert audio to WAV format
    convert_to_wav(file_path, wav_path)

    # Transcribe audio
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        transcription = recognizer.recognize_google(audio_data)
    
    return transcription
