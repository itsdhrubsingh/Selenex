const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("stop");
const exportBtn = document.getElementById("export");

function updateUI(isRecording) {
    if (isRecording) {
        startBtn.innerText = "Recording Started...";
        startBtn.disabled = true;
        stopBtn.disabled = false;
        exportBtn.disabled = true; // Disable export while recording
    } else {
        startBtn.innerText = "Start Recording";
        startBtn.disabled = false;
        stopBtn.disabled = true;
        exportBtn.disabled = false; // Enable export when stopped
    }
}

// Check state on load
chrome.storage.local.get("isRecording", (data) => {
    updateUI(data.isRecording || false);
});

startBtn.onclick = () => {
    chrome.runtime.sendMessage({ type: "START_RECORDING" });
    updateUI(true);
};

stopBtn.onclick = () => {
    chrome.runtime.sendMessage({ type: "STOP_RECORDING" });
    updateUI(false);
};

exportBtn.onclick = () => {
    chrome.storage.local.get("session", (data) => {
        if (!data.session || data.session.length === 0) {
            alert("No session data found!");
            return;
        }
        const blob = new Blob([JSON.stringify(data.session, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "session.json";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });
};
