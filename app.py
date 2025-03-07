from flask import Flask, render_template, request, jsonify
from transcribe import transcribe_audio, predict_threat
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {"wav", "mp3", "ogg", "webm", "flac"}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please upload an audio file (wav, mp3, ogg, webm, flac)."}), 400

    # Generate a unique filename to prevent conflicts
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)

    try:
        file.save(file_path)

        transcription = transcribe_audio(file_path)
        threat_prediction = predict_threat(transcription)

        return jsonify({"transcription": transcription, "threat_status": threat_prediction})

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
