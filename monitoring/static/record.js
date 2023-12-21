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
let captureIntervalId;
let startTime;
let elapsedTimeIntervalId;

function videoStart() {
    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
        previewPlayer.srcObject = stream;
        startRecording(previewPlayer.captureStream())
    })

    captureIntervalId = setInterval(capture, 60000); // 1분
    startTime = Date.now();
    elapsedTimeIntervalId = setInterval(updateElapsedTime, 1000);
}

function updateElapsedTime() {
    const elapsedTime = Date.now() - startTime;
    const hours = Math.floor(elapsedTime / 3600000);
    const minutes = Math.floor((elapsedTime % 3600000) / 60000);
    const seconds = Math.floor((elapsedTime % 60000) / 1000);
    document.getElementById('elapsed-time').textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
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

    const recordedBlob = new Blob(recordedChunks, {type: "video/webm"});
    sendFile(recordedBlob).then(data => console.log(data)).catch(error => console.error(error));

    clearInterval(captureIntervalId);
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
    canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        img.src = url;
        imgDownloadButton.href = url;
        imgDownloadButton.download = `capture_${new Date().toISOString()}.png`;

        sendFile(blob).then(data => console.log(data)).catch(error => console.error(error));
    }, 'image/png');
}

async function sendFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    // formData.append('file', file, `capture_${new Date().toISOString()}.png`);

    $.ajax({
        url: '/live/media/',
        data: formData,
        method: 'POST',
        processData: false,
        contentType: false,
        success: function (result) {
            console.log('성공');
        },
        error: function (request, status, error) {
            console.log('에러');
            console.log(request);
            console.log(status);
            console.log(error);
        }
    })
}

recordButton.addEventListener("click", videoStart);
stopButton.addEventListener("click", stopRecording);
playButton.addEventListener("click", playRecording);
captureButton.addEventListener("click", capture);
