document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("uploadForm").addEventListener("submit", function(event) {
        event.preventDefault();
        let fileInput = document.getElementById("audioFile");
        let transcriptionBox = document.getElementById("transcription");
        let threatBox = document.getElementById("threatStatus");
        let uploadBtn = document.getElementById("uploadBtn");
        let audioPlayer = document.getElementById("audioPlayer");

        if (!fileInput.files.length) {
            alert("Please select an audio file.");
            return;
        }

        let formData = new FormData();
        formData.append("file", fileInput.files[0]);
        transcriptionBox.innerText = "Processing...";
        threatBox.innerText = "Processing...";
        uploadBtn.disabled = true;
        let audioURL = URL.createObjectURL(fileInput.files[0]);
        audioPlayer.src = audioURL;
        audioPlayer.load();

        fetch("/transcribe", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            transcriptionBox.innerText = data.transcription || "Error in transcription";
            threatBox.innerText = data.threat_status || "Error in threat detection";
            threatBox.style.color = data.threat_status === "Threatening" ? "red" : "green";
        })
        .catch(error => {
            transcriptionBox.innerText = "Error processing audio.";
            threatBox.innerText = "Error analyzing threat.";
        })
        .finally(() => {
            uploadBtn.disabled = false;
        });
    });
});
