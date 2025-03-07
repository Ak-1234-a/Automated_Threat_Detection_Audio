from flask import Flask, request, jsonify
from pydub import AudioSegment
import speech_recognition as sr
import os
import joblib
import re

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the trained threat detection model
try:
    model = joblib.load("threat_model.pkl")
    vectorizer = model.named_steps['tfidf']  # Extract TF-IDF vectorizer
    classifier = model.named_steps['classifier']  # Extract classifier
    print("Threat detection model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model, vectorizer, classifier = None, None, None

def preprocess_text(text):
    """Apply same preprocessing as in training."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text

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

def predict_threat(text):
    """Predict if the transcribed text is a threat."""
    if not model:
        return "Model not available."
    if not text.strip():
        return "No text detected."
    text = preprocess_text(text)  # Apply preprocessing
    text_vectorized = vectorizer.transform([text])  # Apply TF-IDF transformation
    prediction = classifier.predict(text_vectorized)[0]
    return "Threatening" if prediction == 1 else "Non-Threatening"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Handle audio file uploads and return transcription with threat detection."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        transcription = transcribe_audio(file_path)
        threat_prediction = predict_threat(transcription)
        return jsonify({"transcription": transcription, "threat_status": threat_prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
