# transcribe.py (Updated with Email Notification and Location Tracking)
from flask import Flask, request, jsonify
from pydub import AudioSegment
import speech_recognition as sr
import os
import joblib
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Email Configuration
EMAIL_SENDER = "aruncse60@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "qbmx cdsb zmgd yxxh"  # Replace with your password
EMAIL_RECEIVER = "aruncse60@gmail.com"  # Replace with the recipient email

def get_location():
    """Fetch the user's location based on their IP address."""
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        ip = data.get("ip", "Unknown IP")
        city = data.get("city", "Unknown City")
        region = data.get("region", "Unknown Region")
        country = data.get("country", "Unknown Country")
        isp = data.get("org", "Unknown ISP")
        return f"IP: {ip}\nLocation: {city}, {region}, {country}\nISP: {isp}"
    except Exception as e:
        return f"Error fetching location: {e}"

def send_email(transcription):
    """Send an email notification if a threatening message is detected."""
    location_details = get_location()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    subject = "⚠️ Threat Detected in Transcription"
    body = (
        f"A threatening message was detected:\n\n"
        f"📝 **Transcription:** {transcription}\n\n"
        f"📍 **Location Details:**\n{location_details}\n\n"
        f"⏰ **Detection Time:** {timestamp}\n\n"
        f"Please take appropriate action."
    )
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # Use SMTP server of your email provider
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

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
    try:
        model = joblib.load("threat_detection_model.pkl")
        vectorizer = joblib.load("tfidf_vectorizer.pkl")
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower().strip())
        text_vectorized = vectorizer.transform([text])
        prediction = model.predict(text_vectorized)[0]
        
        if prediction == "Threat":
            send_email(text)  # Send email if threat detected
            return "Threatening"
        return "Non-Threatening"
    except Exception as e:
        return f"Error in threat detection: {e}"

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
        threat_prediction = predict_threat(transcription)
        return jsonify({"transcription": transcription, "threat_status": threat_prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
