from flask import Flask, request, jsonify
from pydub import AudioSegment
import speech_recognition as sr
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def convert_to_wav(audio_path, wav_path):
    """Convert MP3/WebM audio file to WAV."""
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(wav_path, format="wav")
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

def transcribe_audio(file_path):
    """Convert uploaded audio file to WAV, then transcribe."""
    try:
        wav_path = file_path.rsplit(".", 1)[0] + ".wav"
        convert_to_wav(file_path, wav_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)
        
        return transcription
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio."
    except sr.RequestError as e:
        return f"Error with speech recognition service: {e}"
    except Exception as e:
        return f"Error during transcription: {e}"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Handle audio file uploads and return full transcription."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        transcription = transcribe_audio(file_path)
        return jsonify({"transcription": transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
