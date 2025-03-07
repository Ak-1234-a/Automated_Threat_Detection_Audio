document.addEventListener("DOMContentLoaded", () => {
    let mediaRecorder;
    let audioChunks = [];
    let recording = false;

    const recordBtn = document.getElementById("recordBtn");
    const stopBtn = document.getElementById("stopBtn");
    const audioFileInput = document.getElementById("audioFile");
    const transcriptionBox = document.getElementById("transcription");
    const threatBox = document.getElementById("threatStatus"); // ✅ Display threat result
    const audioPlayer = document.getElementById("audioPlayer");

    // 🎤 Initialize button states
    stopBtn.disabled = true;

    // 🎤 Start Recording
    if (recordBtn && stopBtn) {
        recordBtn.addEventListener("click", async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

                audioChunks = [];
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

                    // 🎵 Set recorded audio for playback
                    const audioURL = URL.createObjectURL(audioBlob);
                    audioPlayer.src = audioURL;

                    // 📌 Upload and Transcribe
                    await uploadAudio(audioBlob, "recorded_audio.webm");
                };

                mediaRecorder.start();
                recording = true;
                stopBtn.disabled = false;
                recordBtn.disabled = true;
                recordBtn.innerText = "Recording... 🎙️"; // ✅ Update UI
            } catch (error) {
                alert("Error accessing the microphone.");
                console.error("Microphone error:", error);
            }
        });

        // 🛑 Stop Recording
        stopBtn.addEventListener("click", () => {
            if (recording && mediaRecorder) {
                mediaRecorder.stop();
                recording = false;
                stopBtn.disabled = true;
                recordBtn.disabled = false;
                recordBtn.innerText = "Start Recording 🎤"; // ✅ Reset button text
            }
        });
    }

    // 📤 Upload Audio File
    async function uploadAudio(file, filename) {
        if (!file) {
            alert("Please select an audio file to upload.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file, filename);

        // ✅ Show processing message
        transcriptionBox.innerText = "Processing... ⏳";
        threatBox.innerText = "";

        try {
            const response = await fetch("/transcribe", {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (result.transcription) {
                // ✅ Display full transcription
                transcriptionBox.innerHTML = `<p>${result.transcription}</p>`;
                threatBox.innerHTML = `<strong>Status: ${result.threat_status}</strong>`;

                // ✅ Change color based on threat status
                if (result.threat_status === "Threatening") {
                    threatBox.style.color = "red";
                } else {
                    threatBox.style.color = "green";
                }
            } else {
                transcriptionBox.innerText = "Transcription failed.";
                threatBox.innerText = "";
            }
        } catch (error) {
            console.error("Error during upload:", error);
            transcriptionBox.innerText = "Error processing the audio.";
            threatBox.innerText = "";
        }
    }

    // 🎵 Handle file upload
    if (audioFileInput) {
        audioFileInput.addEventListener("change", async function (event) {
            const file = event.target.files[0];
            if (file) {
                const audioURL = URL.createObjectURL(file);
                audioPlayer.src = audioURL;

                // Upload & Transcribe
                await uploadAudio(file, file.name);
            }
        });
    }
});
