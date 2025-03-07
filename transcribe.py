from flask import Flask, request, jsonify
from pydub import AudioSegment
import speech_recognition as sr
import os
import joblib
import re
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed audio formats
ALLOWED_EXTENSIONS = {"wav", "mp3", "ogg", "webm", "flac"}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Load the trained threat detection model
try:
    model = joblib.load("threat_model.pkl")
    vectorizer = model.named_steps['tfidf']  # Extract TF-IDF vectorizer
    classifier = model.named_steps['classifier']  # Extract classifier
    print("✅ Threat detection model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model, vectorizer, classifier = None, None, None

def preprocess_text(text):
    """Apply same preprocessing as in training."""
    text = text.lower().strip()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    return text

def convert_to_wav(audio_path, wav_path):
    """Convert audio file to WAV format."""
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(wav_path, format="wav")
        return wav_path
    except Exception as e:
        print(f"❌ Error converting audio: {e}")
        return None

def transcribe_audio(file_path):
    """Transcribe uploaded audio file."""
    try:
        wav_path = file_path.rsplit(".", 1)[0] + ".wav"
        convert_to_wav(file_path, wav_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)
        
        return transcription
    except sr.UnknownValueError:
        return "❌ Speech recognition could not understand the audio."
    except sr.RequestError as e:
        return f"❌ Error with speech recognition service: {e}"
    except Exception as e:
        return f"❌ Error during transcription: {e}"

def predict_threat(text):
    """Predict if the transcribed text is a threat."""
    if not model:
        return "❌ Model not available."
    if not text.strip():
        return "⚠️ No text detected."
    
    text = preprocess_text(text)  # Apply preprocessing
    text_vectorized = vectorizer.transform([text])  # Apply TF-IDF transformation
    prediction = classifier.predict(text_vectorized)[0]
    
    return "🔴 Threatening" if prediction == 1 else "🟢 Non-Threatening"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Handle audio file uploads and return transcription with threat detection."""
    if "file" not in request.files:
        return jsonify({"error": "❌ No file uploaded."}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "❌ No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "❌ Invalid file type. Please upload an audio file (wav, mp3, ogg, webm, flac)."}), 400

    # Generate a unique filename to prevent overwriting
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)

    try:
        transcription = transcribe_audio(file_path)
        threat_prediction = predict_threat(transcription)
        return jsonify({"transcription": transcription, "threat_status": threat_prediction})
    except Exception as e:
        print(f"❌ Internal error: {e}")
        return jsonify({"error": "❌ Internal server error."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
