let isRecording = false;
let session = [];

chrome.runtime.onMessage.addListener((msg, sender) => {

    if (msg.type === "START_RECORDING") {
        isRecording = true;
        session = [];
        chrome.storage.local.set({ isRecording: true });
        console.log("Recording started");
    }

    if (msg.type === "STOP_RECORDING") {
        isRecording = false;
        chrome.storage.local.set({ session, isRecording: false });
        console.log("Recording stopped. Saved:", session);
    }

    if (msg.type === "USER_ACTION" && isRecording) {
        session.push(msg.payload);
    }
});
