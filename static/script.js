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
                
                // ✅ Handle Safari & older browser issues with mimeType fallback
                const options = MediaRecorder.isTypeSupported("audio/webm") 
                    ? { mimeType: "audio/webm" } 
                    : {};
                    
                mediaRecorder = new MediaRecorder(stream, options);
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
                alert("Error accessing the microphone. Please check your permissions.");
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

        // ✅ Show processing message & disable UI elements
        transcriptionBox.innerText = "Processing... ⏳";
        threatBox.innerText = "";
        recordBtn.disabled = true;
        stopBtn.disabled = true;
        audioFileInput.disabled = true;

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
                threatBox.style.color = result.threat_status === "Threatening" ? "red" : "green";
            } else {
                transcriptionBox.innerText = "Transcription failed.";
                threatBox.innerText = "";
            }
        } catch (error) {
            console.error("Error during upload:", error);
            transcriptionBox.innerText = "Error processing the audio.";
            threatBox.innerText = "";
        } finally {
            // ✅ Re-enable UI elements after processing
            recordBtn.disabled = false;
            audioFileInput.disabled = false;
        }
    }

    // 🎵 Handle file upload
    if (audioFileInput) {
        audioFileInput.addEventListener("change", async function (event) {
            const file = event.target.files[0];
            if (file) {
                const audioURL = URL.createObjectURL(file);
                audioPlayer.src = audioURL;

                // ✅ Reset UI before processing
                transcriptionBox.innerText = "Processing... ⏳";
                threatBox.innerText = "";

                // Upload & Transcribe
                await uploadAudio(file, file.name);
            }
        });
    }
});
