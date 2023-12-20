const recordButton = document.querySelector(".record-button");
const stopButton = document.querySelector(".stop-button");
const playButton = document.querySelector(".play-button");
const downloadButton = document.querySelector(".video-download-button");
const imgDownloadButton = document.querySelector(".img-download-button");
const captureButton = document.querySelector(".capture-button");
const previewPlayer = document.querySelector("#preview");
const recordingPlayer = document.querySelector("#recording");

let recorder;
let recordedChunks;

function videoStart() {
    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
        previewPlayer.srcObject = stream;
        startRecording(previewPlayer.captureStream())
    })
}

function startRecording(stream) {
    recordedChunks = [];
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => {
        recordedChunks.push(e.data)
    }
    recorder.start();
}

function stopRecording() {
    previewPlayer.srcObject.getTracks().forEach(track => track.stop());
    recorder.stop();
}

function playRecording() {
    const recordedBlob = new Blob(recordedChunks, {type: "video/webm"});
    recordingPlayer.src = URL.createObjectURL(recordedBlob);
    recordingPlayer.play();
    downloadButton.href = recordingPlayer.src;
    downloadButton.download = `recording_${new Date()}.webm`;
    console.log(recordingPlayer.src);
}


function capture() {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const img = document.getElementById('image');

    context.drawImage(previewPlayer, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL();
    img.src = dataURL;

    imgDownloadButton.href = dataURL;
    imgDownloadButton.download = `capture_${new Date().toISOString()}.png`;
}

recordButton.addEventListener("click", videoStart);
stopButton.addEventListener("click", stopRecording);
playButton.addEventListener("click", playRecording);
captureButton.addEventListener("click", capture);
