// Upload Audio
function uploadAudio() {
    document.getElementById('audioUpload').click();
}

// Recording Logic
let mediaRecorder;
let audioChunks = [];

document.getElementById('startRecord')?.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        document.getElementById('audioPlayback').src = audioUrl;
    };

    mediaRecorder.start();
    document.getElementById('stopRecord').disabled = false;
});

document.getElementById('stopRecord')?.addEventListener('click', () => {
    mediaRecorder.stop();
});

// Save Settings
function saveSettings() {
    const threshold = document.getElementById('threshold').value;
    const notifications = document.getElementById('notifications').value;
    const userDetails = document.getElementById('userDetails').value;

    localStorage.setItem('threshold', threshold);
    localStorage.setItem('notifications', notifications);
    localStorage.setItem('userDetails', userDetails);

    alert('Settings saved!');
}

// Load Settings
window.onload = function() {
    if (document.getElementById('threshold')) {
        document.getElementById('threshold').value = localStorage.getItem('threshold') || 50;
        document.getElementById('notifications').value = localStorage.getItem('notifications') || 'on';
        document.getElementById('userDetails').value = localStorage.getItem('userDetails') || '';
    }
};
